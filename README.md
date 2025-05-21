# 📝 Flask Blog Website
A personal blog web application built using **Python**, **Flask**, **Jinja2**, **Bootstrap**, and **SQLAlchemy**. 
It supports user authentication, form validation, and basic routing across different pages.

## 🚀 Features
- 🧩 Modular Flask structure using `render_template()` and `Jinja2`
- 🎨 Responsive frontend with Bootstrap templates
- 🔐 User authentication with Flask-WTF
- ✅ Form validation
- 🗂️ Page routing (Home, Blog, About, etc.)
- 💾 SQLite database integration using SQLAlchemy ORM
- ☁️ Deployment: Will be deployed on [Render](https://render.com) or another platform.

## How to use
- To use it I already created a admin and a user whose credentials are below.
- You can create a new user to comment but the posts will be read-only.
- However, with the admin, you can do CRUD operations.

      Admin email: admin@gmail.com
      Admin Password: 12345678
      User email: user@gmail.com
      User Password: 12345678
  

## 📁 Project Structure
flask-blog/
├── static/ # CSS, JS, images
├── templates/ # HTML templates (Jinja2)
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ └── ...
├── app.py # Main Flask application
├── models.py # SQLAlchemy database models
├── forms.py # WTForms form definitions
├── requirements.txt # Project dependencies
└── README.md

## ⚙️ Tech Stack
| Layer       | Tech                                  |
|-------------|---------------------------------------|
| Backend     | Python, Flask, SQLAlchemy, SQLite     |
| Frontend    | HTML, CSS, Bootstrap, Jinja2          |
| Forms       | Flask-WTF (WTForms)                   |
| Deployment  | Render                                |
