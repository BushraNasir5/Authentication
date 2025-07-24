# Django Authentication System

## Features
- User sign-up with: first name, last name, username, email, password, confirm password
- "Remember Me" checkbox: token valid for 1 day if checked, 15 minutes if not
- API endpoints for sign-up and login (Django REST Framework + SimpleJWT)
- Bootstrap-based frontend (see `templates/signup.html` and `templates/login.html`)
- Secure data transfer (CORS enabled, CSRF protection)
- Account lockout after 5 failed login attempts

## Setup

1. **Clone the repository** and enter the directory.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- `POST /api/signup/` — Register a new user
- `POST /api/login/` — Login and get JWT tokens
- `GET /api/profile/` — Get user profile (requires authentication)

## Notes

- **Do not use Live Server for Django templates.** Always use Django's server for `/signup/` and `/login/`.
- If you want to use the API from a different frontend, update `CORS_ALLOWED_ORIGINS` in `core/settings.py`.
