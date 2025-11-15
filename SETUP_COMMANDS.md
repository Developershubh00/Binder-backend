# Binder Backend - Complete Setup Commands

## Step 1: Initial Setup

```bash
# Navigate to project directory
cd binder_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: PostgreSQL Database Setup

```bash
# Start PostgreSQL service
# Windows: Start from Services
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database and user
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE binder_db;
CREATE USER binder_user WITH PASSWORD 'your_secure_password';
ALTER ROLE binder_user SET client_encoding TO 'utf8';
ALTER ROLE binder_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE binder_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE binder_db TO binder_user;
\q
```

## Step 3: Environment Configuration

```bash
# Copy example .env
cp .env.example .env

# Edit .env with your settings
# Use nano, vim, or your preferred editor
nano .env
```

### Required .env Variables:
```
SECRET_KEY=generate-a-strong-random-key-here
DEBUG=True
DATABASE_URL=postgresql://binder_user:your_secure_password@localhost:5432/binder_db
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
```

## Step 4: Django Project Initialization

```bash
# Create Django apps (if not already created)
python manage.py startapp auth_service
python manage.py startapp inventory_management
python manage.py startapp community
python manage.py startapp load_balancer
mkdir -p shared

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (Master Admin)
python manage.py createsuperuser
# Email: admin@binder.com
# Password: (set a strong password)
```

## Step 5: Google Sheets Setup

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "Google Sheets API"
4. Create Service Account credentials
5. Download JSON credentials file
6. Rename to `credentials.json`
7. Place in project root: `binder_backend/credentials.json`
8. Copy the service account email (e.g., service@project.iam.gserviceaccount.com)
9. Share your Google Sheet with this email (Editor access)
10. Copy Sheet ID from URL and add to .env

## Step 6: Run Development Server

```bash
# Run server
python manage.py runserver

# Server will start at: http://127.0.0.1:8000/
# API Docs at: http://127.0.0.1:8000/api/docs/
```

## Step 7: Test API Endpoints

```bash
# Register a user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123456","password_confirm":"Test@123456","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123456"}'

# Get current user (use token from login response)
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Step 8: Create Test Tenant (via Django Shell)

```bash
python manage.py shell
```

```python
from auth_service.models import Tenant, User

# Create tenant
tenant = Tenant.objects.create(
    company_name="Test Company",
    company_email="company@test.com",
    user_limit=40
)

# Create tenant owner
owner = User.objects.create_user(
    email="owner@test.com",
    password="Owner@123",
    first_name="Owner",
    last_name="Test",
    role="tenant_owner",
    tenant=tenant,
    email_verified=True
)

tenant.increment_user_count()
print(f"Tenant created: {tenant.company_name}")
print(f"Owner created: {owner.email}")
```

## Additional Commands

### Create migrations for specific app
```bash
python manage.py makemigrations auth_service
python manage.py makemigrations inventory_management
```

### Run tests
```bash
pytest
```

### Collect static files (for production)
```bash
python manage.py collectstatic --noinput
```

### Create custom management command
```bash
mkdir -p auth_service/management/commands
```

## Troubleshooting

### PostgreSQL connection issues
```bash
# Check if PostgreSQL is running
# macOS:
brew services list
# Linux:
sudo systemctl status postgresql
```

### Migration issues
```bash
# Reset migrations (⚠️ This will delete all data)
python manage.py migrate --fake auth_service zero
python manage.py migrate auth_service
```

### Port already in use
```bash
# Use different port
python manage.py runserver 8001
```

## Production Deployment (Render/Railway)

### Render.com
1. Connect GitHub repo
2. Create new Web Service
3. Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
4. Start Command: `gunicorn binder_config.wsgi:application`
5. Add environment variables from .env

### Railway.app
1. Connect GitHub repo
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

## Next Steps

1. ✅ Setup complete
2. Configure Google Sheets integration
3. Test auth flow with frontend
4. Create initial permissions
5. Add sample data
6. Test member creation
7. Configure email settings for production

## Quick Reference

- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **API Base URL**: http://localhost:8000/api/
