# 📜 ReviewQuotes

A clean and modern **Django-based web application** that allows users to view and manage inspirational quotes and reviews through RESTful APIs. The project is built with a focus on simplicity, scalability, and clean backend architecture.

---

## 🚀 Live Demo

🔗 **Live URL:** [https://reviewqoutes.onrender.com/](https://reviewqoutes.onrender.com/)

---

## 🛠️ Tech Stack

* **Backend:** Django 6, Django REST Framework
* **Database:** SQLite (development) / PostgreSQL-ready
* **Deployment:** Render
* **Server:** Gunicorn
* **Others:** CORS Headers

---

## ✨ Features

* ✅ RESTful CRUD APIs (Create, Read, Update, Delete)
* ✅ Clean and structured Django project setup
* ✅ Modular app-based architecture
* ✅ Ready for PostgreSQL / Supabase integration
* ✅ Deployed on Render with Gunicorn

---

## 📂 Project Structure

```
reviewqoutes/
│── manage.py
│── db.sqlite3
│── poets_canvas_backend/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│── quotes/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│── requirements.txt
```

---

## ⚙️ Setup Instructions (Local)

1. **Clone the repository**

```bash
git clone https://github.com/ravi-rkk/reviewqoutes.git
cd reviewqoutes
```

2. **Create & activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run migrations**

```bash
python manage.py migrate
```

5. **Start the server**

```bash
python manage.py runserver
```

---

## 🔐 Environment Variables

```env
DJANGO_SETTINGS_MODULE=poets_canvas_backend.settings
DEBUG=False
```

---

## 🌍 Deployment (Render)

**Build Command**

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**Start Command**

```bash
gunicorn poets_canvas_backend.wsgi:application
```

---

## 👤 Author

**Ravilesh Kashyap**

* 🌐 Portfolio: [https://ravileshportfolio.netlify.app/](https://ravileshportfolio.netlify.app/)
* 💼 LinkedIn: [https://www.linkedin.com/in/ka-ra/](https://www.linkedin.com/in/ka-ra/)
* 🧑‍💻 GitHub: [https://github.com/ravi-rkk](https://github.com/ravi-rkk)

---

## 📌 Notes

* PostgreSQL / Supabase can be plugged in easily for production
* Designed as a demo task for Full Stack Developer evaluation

---

⭐ If you like this project, feel free to give it a star!
