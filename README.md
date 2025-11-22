# kms_minidrive
A secure cloud file manager with JWT login, AWS S3 storage, and MySQL database. Users can upload, search, download, delete, and share files with expiring links. Built with Flask and Bootstrap, deployed on Amazon Linux EC2.
README.md
markdown
# Mini Google Drive

A secure, scalable file manager built with Flask, JWT authentication, AWS S3 storage, and MySQL. Users can sign up, log in, upload files, and share download links — all through a polished Bootstrap interface.

---

## 🚀 Features

- 🔐 JWT-based user authentication
- 📤 Upload files to AWS S3
- 🔗 Generate secure download links
- 🗂️ View and manage uploaded files
- 🎨 Responsive UI with Bootstrap
- 🧠 MySQL backend for user and file metadata

---

## 🛠️ Tech Stack

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Database**: MySQL (local EC2)
- **Cloud Storage**: AWS S3
- **Auth**: JWT
- **Deployment**: Amazon EC2 (Amazon Linux)

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/kanmaninu-sketch/kms_minidrive.git
cd kms_minidrive
2. Install dependencies
bash
pip install -r requirements.txt
3. Configure environment variables
Create a .env file using .env.example:

env
JWT_SECRET_KEY=your_jwt_secret
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=minigoogledrive
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=mini_drive
4. Run the app
bash
python app.py
🌐 Live Demo
Access the deployed app at: http://13.204.3.189
📸 Screenshots
Add screenshots to docs/screenshots/ and embed here.

📄 Report
If submitting a report, include docs/report.pdf and link it here.

📁 Repo Structure
Code
kms_minidrive/
├── app.py
├── templates/
├── static/
├── requirements.txt
├── .env.example
├── README.md
└── docs/
    ├── screenshots/
    └── report.pdf
🧠 Author
Kanmani N U Final-year engineering student at SASTRA University Focused on secure cloud deployment, backend architecture, and polished UI workflows

📜 License
This project is licensed under the MIT License.

Code

---

Let me know if you want to tweak the tone, add screenshots, or generate your short
