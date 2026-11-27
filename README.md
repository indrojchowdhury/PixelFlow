
# 🎨 PixelFlow

PixelFlow is a full-stack image and album management platform built with Django and React. It allows users to organize their images into albums, manage their collections, and enjoy a responsive experience with light and dark themes.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>

## 🌐 Live Demo

🔗 **Live Website:** [PixelFlow](https://pixelflow-rust.vercel.app/)

## ✨ Features

### 👤 User Authentication
- User registration and login
- JWT-based authentication
- Secure user-specific access
- Logout functionality

### 🖼️ Album Management
- Create new albums
- View album collections
- Edit album details
- Delete albums
- Track image counts in albums

### 📸 Image Management
- Upload and manage images
- Organize images into albums
- Browse personal image collections
- Manage uploaded content

### 🎨 User Experience
- Responsive design for desktop, tablet, and mobile
- Light and dark mode
- Persistent theme preferences
- Clean and intuitive interface

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Frontend | React.js, JavaScript, Tailwind CSS |
| Backend | Python, Django, Django REST Framework |
| Authentication | JWT |
| Database | PostgreSQL |
| API Communication | REST API |
| Deployment | Vercel, Render |

## 🚀 Getting Started

Follow these steps to run the project locally.

### 📋 Prerequisites

- Python 3.10+
- Node.js and npm
- PostgreSQL

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/indrojchowdhury/PixelFlow.git

cd PixelFlow
```

### 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your backend environment variables in a `.env` file.

Run database migrations:

```bash
python manage.py migrate
```

Start the backend server:

```bash
python manage.py runserver
```

### 3️⃣ Frontend Setup

Open a new terminal:

```bash
cd frontend

npm install
```

Configure your frontend environment variables in a `.env` file.

Start the frontend development server:

```bash
npm run dev
```

## 🔐 Environment Variables

### Backend (`.env`)

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=your_database_url

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (`.env`)

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

⚠️ Never commit actual secret keys, database credentials, or other sensitive environment variables to GitHub.

## 🔌 API Modules

The backend provides RESTful APIs for:

- User Authentication
- Album Management
- Image Upload and Management
- User-specific Data Management

## 🔮 Future Improvements

- Advanced image search and filtering
- Image sharing capabilities
- Cloud-based image optimization
- Album collaboration features

---

<p align="center">
  💻 Built with ❤️ using Django, React, and PostgreSQL
</p>
