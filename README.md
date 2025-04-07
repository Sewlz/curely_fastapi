# FastAPI Modular Monolith

## Project Description

This project is a modular monolith built using FastAPI. It follows a structured architecture with separate modules for authentication, user management, LLM integration, and CNN-based functionalities.

## Project Structure

```
curely_fastapi/
│── app/
│   ├── modules/  # Modular Monolith: Each module is independent
│   │   ├── auth/
│   │   │   ├── controllers/
│   │   │   │   ├── auth_controller.py
│   │   │   ├── services/
│   │   │   │   ├── auth_service.py
│   │   │   ├── repositories/
│   │   │   │   ├── auth_repository.py
│   │   │   ├── schemas/
│   │   │   │   ├── auth_schema.py
│   │   │   ├── __init__.py
│   │   │
│   │   ├── user/
│   │   │   ├── controllers/
│   │   │   │   ├── user_controller.py
│   │   │   ├── services/
│   │   │   │   ├── user_service.py
│   │   │   ├── repositories/
│   │   │   │   ├── user_repository.py
│   │   │   ├── schemas/
│   │   │   │   ├── user_schema.py
│   │   │   ├── __init__.py
│   │   │
│   │   ├── llm/
│   │   │   ├── controllers/
│   │   │   │   ├── llm_controller.py
│   │   │   ├── services/
│   │   │   │   ├── llm_service.py
│   │   │   ├── repositories/
│   │   │   │   ├── llm_repository.py
│   │   │   ├── schemas/
│   │   │   │   ├── llm_schema.py
│   │   │   ├── __init__.py
│   │   │
│   │   ├── cnn/
│   │   │   ├── controllers/
│   │   │   │   ├── cnn_controller.py
│   │   │   ├── services/
│   │   │   │   ├── cnn_service.py
│   │   │   ├── repositories/
│   │   │   │   ├── cnn_repository.py
│   │   │   ├── schemas/
│   │   │   │   ├── cnn_schema.py
│   │   │   ├── __init__.py
│   │
│   ├── common/  # Shared utilities across modules
│   │   ├── database/
│   │   │   ├── firestore.py
│   │   │   ├── __init__.py
│   │   ├── security/
│   │   │   ├── auth.py
│   │   │   ├── role_based_access.py
│   │   │   ├── csrf.py
│   │   │   ├── __init__.py
│   │   ├── middlewares/
│   │   │   ├── request_logging.py
│   │   │   ├── rate_limiting.py
│   │   │   ├── __init__.py
│   │   ├── utils/
│   │   │   ├── rate_limiter.py
│   │   │   ├── logging.py
│   │   │   ├── encryption.py
│   │   │   ├── __init__.py
│   │
│   ├── core/  # Application configuration
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │
│   ├── main.py  # FastAPI entry point
│
├── tests/  # Unit & integration tests
│   ├── test_auth.py
│   ├── test_user.py
│   ├── test_llm.py
│   ├── test_cnn.py
│   ├── __init__.py
│
├── .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
```

## Installation & Setup

### 1. Set Up Virtual Environment (Recommended)

If you haven't already, create and activate a virtual environment:

```bash
python -m venv venv
```

#### On Windows:

```bash
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory and define required environment variables. For example:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-secret-key
```

Make sure your app loads the environment using `python-dotenv`. Add the following to the top of your main file (`main.py` or `app/main.py`):

```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Run FastAPI Server

If `main.py` is in the `app/` directory:

```bash
uvicorn app.main:app
```

If `main.py` is in the root directory:

```bash
uvicorn main:app
```

### 5. API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss the intended modifications.
