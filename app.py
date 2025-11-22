from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
import pymysql
import boto3
import botocore
import jwt, datetime, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'minigoogledrive')
REGION = os.environ.get('REGION', 'ap-south-1')
JWT_SECRET = os.environ.get('JWT_SECRET', 'changeme')
BASE_URL = os.environ.get('BASE_URL', 'http://13.204.3.189:5000')

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Kannusha@03')
DB_NAME = os.environ.get('DB_NAME', 'minidrive')

s3 = boto3.client(
    's3',
    region_name=REGION,
    config=botocore.config.Config(signature_version='s3v4')
)

def get_db_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.Cursor,
        autocommit=False
    )

def make_token(user_id, username, hours=12):
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    return jwt.encode({'user_id': user_id, 'username': username, 'exp': exp}, JWT_SECRET, algorithm='HS256')

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Auth required'}), 401
        try:
            token = auth.split(' ', 1)[1]
            claims = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = claims['user_id']
            request.username = claims.get('username')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return wrapper

# ---------------- PAGES & HEALTH ----------------
@app.route('/')
def health():
    return '<h2 style="color:green;">✅ Mini Google Drive Backend is running!</h2>'

@app.route('/frontend')
def frontend():
    return render_template('index.html')

@app.route('/upload-page')
def upload_page():
    return render_template('upload.html')

@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

# ---------------- AUTH ----------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    hashed = generate_password_hash(password)
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            return jsonify({'error': 'username exists'}), 409
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s,%s)", (username, hashed))
        conn.commit()
        return jsonify({'message': 'signup successful'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'invalid credentials'}), 401
        user_id, pw_hash = row[0], row[1]
        if not check_password_hash(pw_hash, password):
            return jsonify({'error': 'invalid credentials'}), 401
        token = make_token(user_id, username)
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ---------------- FILES ----------------
@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    s3_key = f"{request.username}/{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    try:
        s3.upload_fileobj(file, BUCKET_NAME, s3_key, ExtraArgs={'ACL': 'private', 'ContentType': file.content_type or 'application/octet-stream'})
    except Exception as e:
        return jsonify({'error': f'S3 upload failed: {str(e)}'}), 500
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO files (owner_id, filename, s3_key, upload_date) VALUES (%s,%s,%s,NOW())",
                    (request.user_id, filename, s3_key))
        conn.commit()
        return jsonify({'message': 'File uploaded successfully!', 'filename': filename})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/files', methods=['GET'])
@require_auth
def list_files():
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT filename, upload_date, s3_key FROM files WHERE owner_id=%s ORDER BY upload_date DESC", (request.user_id,))
        rows = cur.fetchall()
        files = [{'filename': r[0], 'uploaded': str(r[1]), 's3_key': r[2]} for r in rows]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/download/<path:filename>', methods=['GET'])
@require_auth
def download_file(filename):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT s3_key FROM files WHERE owner_id=%s AND filename=%s", (request.user_id, filename))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'file not found'}), 404
        s3_key = row[0]
        url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': s3_key}, ExpiresIn=3600)
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/delete/<path:filename>', methods=['DELETE'])
@require_auth
def delete_file(filename):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT s3_key FROM files WHERE owner_id=%s AND filename=%s", (request.user_id, filename))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'file not found'}), 404
        s3_key = row[0]
        s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        cur.execute("DELETE FROM files WHERE filename=%s AND (owner_id=%s OR owner_id=0)", (filename, request.user_id))
        conn.commit()
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ---------------- SHARING ----------------
@app.route('/share/<path:filename>', methods=['POST'])
@require_auth
def share_file(filename):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT s3_key FROM files WHERE owner_id=%s AND filename=%s", (request.user_id, filename))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'file not found'}), 404
        share_token = secrets.token_urlsafe(24)
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # ✅ 1-day expiry
        cur.execute("INSERT INTO shares (filename, s3_key, share_token, expires_at, owner_id) VALUES (%s,%s,%s,%s,%s)",
                    (filename, row[0], share_token, expires, request.user_id))
        conn.commit()
        share_url = f"{BASE_URL}/public/{share_token}"
        return jsonify({'share_url': share_url})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/public/<token>', methods=['GET'])
def public_download(token):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT s3_key, expires_at FROM shares WHERE share_token=%s", (token,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'invalid token'}), 404
        s3_key, expires_at = row[0], row[1]
        if datetime.datetime.utcnow() > expires_at:
            return jsonify({'error': 'Link expired'}), 403
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
                                        ExpiresIn=86400)  # ✅ 1-day presigned URL
        return redirect(url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

