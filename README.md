# 🗂️ Mini Google Drive (kms_minidrive)

A secure, scalable cloud file manager built with **Flask**, **JWT authentication**, **AWS S3 storage**, and **MariaDB**.  
Users can sign up, log in, upload files, search, download, delete, and share files with expiring links — all through a polished **Bootstrap interface**.  
Frontend is hosted on **Amazon S3 (static website hosting)**, while the backend runs on **Amazon EC2**.

---

## 🚀 Features

- 🔐 JWT-based user authentication  
- 📤 Upload files to AWS S3  
- 🔗 Generate secure expiring download links  
- 🗂️ Search, view, and manage uploaded files  
- 🎨 Responsive UI with Bootstrap (hosted on S3)  
- 🧠 MariaDB backend for user and file metadata  
- ☁️ Cloud-native deployment on AWS EC2 + S3  

---

## 🛠️ Tech Stack

- **Backend**: Flask, Python  
- **Frontend**: HTML, CSS (Bootstrap), JavaScript  
- **Database**: MariaDB (local EC2 instance)  
- **Cloud Storage**: AWS S3  
- **Authentication**: JWT  
- **Deployment**: Amazon EC2 (Amazon Linux) + S3 static hosting  

---

## 🌐 Deployment Architecture

- **Frontend**: Hosted on Amazon S3 with static website hosting  
  URL → `http://elevatelab1.s3-website.ap-south-1.amazonaws.com`  
- **Backend**: Flask app running on Amazon EC2 (port 5000)  
- **Storage**: AWS S3 bucket for file uploads/downloads  
- **Database**: MariaDB running locally on EC2  

### 🔄 Workflow
1. User accesses the frontend via the S3 bucket URL.  
2. Frontend (HTML, CSS, JS, Bootstrap) makes API calls to the EC2 backend.  
3. Backend authenticates users with JWT and interacts with MariaDB.  
4. Files are stored/retrieved from the S3 storage bucket.  

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
python3 app.py
🗃️ Database Schema (MariaDB)
1. users table
sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
2. files table
sql
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
3. shared_links table
sql
CREATE TABLE shared_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);
📁 Repository Structure
Code
kms_minidrive/
├── app.py
├── templates/          # HTML templates
├── static/             # JS, CSS, images
├── requirements.txt    # Dependencies
├── .env.example        # Environment variables template
├── README.md           # Documentation
└── docs/
    ├── screenshots/    # UI screenshots
    └── report.pdf      # Project report
📸 Screenshots
Screenshots of the working app (login, upload, file list, share, download) are included in: docs/Minidrive - PICTURES OF THE WORKING APP...

👤 Author
Kanmani N U from SASTRA University, passionate about building secure, scalable cloud systems and crafting user‑centric web applications with polished UI workflows.
