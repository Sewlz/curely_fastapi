# Curely API – AI-Powered Cancer Diagnosis API

## 🏥 Introduction

**Curely API** is the backend system powering the **Curely** – an AI-powered mobile application that supports early detection of **brain cancer** and **kidney cancer**. This backend is developed with **FastAPI** using a modular monolith architecture and integrates AI models (LLM & CNN), authentication, user management, and Supabase for data storage.

## 🚀 Core Features

- 🔐 **Authentication**: Secure login, JWT tokens, and role-based access.
- 👤 **User Management**: Handle patient and doctor profiles.
- 🧠 **AI Model Integration**:
  - **LLM**: Chat-based assistant for cancer-related Q&A.
  - **CNN**: Analyze medical images (MRI for brain, CT for kidney).
- 🧾 **Medical Record Storage**: Store and manage image uploads and diagnosis history.

## 🛠 Tech Stack

- ⚡ **FastAPI**: High-performance Python web framework.
- 🧠 **TensorFlow/Keras**: For deep learning-based image analysis.
- 🧠 **LangChain**: LLM integration for Q&A features.
- 🔐 **JWT & Role-Based Access**: Secure and customizable access control.
- 🧩 **Modular Monolith**: Clean and scalable code organization.
- 🛢 **Supabase**: Scalable cloud database (PostgreSQL) and authentication service.

## 📁 Project Structure

```
Curely_backend/
│── app/
│   ├── modules/
│   │   ├── auth/
│   │   ├── user/
│   │   ├── llm/
│   │   ├── cnn/
│   ├── common/
│   │   ├── database/  # Supabase connection
│   │   ├── security/  # Auth, RBAC
│   │   ├── middlewares/
│   │   ├── utils/
│   ├── core/
│   ├── main.py
│
├── tests/
├── .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
```

## 📥 Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Vunghiak3/Curely-Backend.git
cd Curely-Backend
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory with your Supabase credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-secret-api-key
SUPABASE_SERVICE_ROLE_KEY=your-secret-service-role-key
SUPABASE_JWT_SECRE=your-secret-jwt-key
```

And ensure your `main.py` includes:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 5. Run the Server

If `main.py` is in `app/`:

```bash
uvicorn app.main:app
```

Or if it's in the root:

```bash
uvicorn main:app
```

### 6. Access the API Docs

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

✨ **Curely API – Empowering healthcare with AI.**
