# quizapp
# Quiz Master - V1

Quiz Master is a simple web-based quiz application designed for exam preparation across multiple subjects and chapters.  
It supports two types of users: **Admin (Quiz Master)** and **User**.

---

## 📌 What the Project Does
- **Admin (Quiz Master)** can:
  - Manage subjects and chapters
  - Create quizzes with multiple-choice questions (MCQs)
  - Edit or delete questions, subjects, and quizzes
  - View summary charts of user activity

- **Users** can:
  - Register and log in
  - Select subjects and chapters
  - Attempt quizzes
  - View scores and previous attempts

---

## 🛠 Tools & Technologies Used
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 Templates
- **Database:** SQLite
- **Charts:** Chart.js
- **APIs:** Flask JSON / Flask-RESTful

---

## 🚀 How to Run
1. Clone the repository  
2. Create and activate a virtual environment  
3. Install required dependencies from `requirements.txt`  
4. Initialize the database (`init_db.py`) — this will create the default admin user  
5. Run the app with `python app.py` and open it in your browser at **http://127.0.0.1:5000**

---

## ✨ Key Features
- Simple, easy-to-use quiz platform
- Role-based access (Admin & User)
- Responsive design using Bootstrap
- Data stored in SQLite database
- Summary charts for quick insights

---
