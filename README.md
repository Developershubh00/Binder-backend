# Binder - ERP System for Textile Manufacturing

A comprehensive SaaS ERP system for India's textile manufacturing industry with multi-tenant architecture.

## 🏗️ Architecture - 4 Pillars

### 1. **Auth Service** (auth_service/)
- Email verification-based authentication
- JWT token management
- Role-based access control (RBAC)
- Future: Mobile OTP via Twilio/Wati
- Tenant & member management

### 2. **IMS** (inventory_management/)
- Inventory Management System
- Product categories & workflows
- Access restrictions
- Product details & descriptions
- Import/Export management

### 3. **Community** (community/)
- Problem-solving forum
- Database-driven solutions
- Future: AI chatbot integration
- Knowledge base

### 4. **Load Balancer** (load_balancer/)
- System health monitoring
- Issue fallback reports
- Server health checks
- Scalability management

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis (for Celery)
- Google Cloud Account (for Sheets API)

### Step 1: Clone and Setup

```bash
# Create project directory
mkdir binder_backend
cd binder_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE binder_db;
CREATE USER binder_user WITH PASSWORD 'your_password';
ALTER ROLE binder_user SET client_encoding TO 'utf8';
ALTER ROLE binder_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE binder_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE binder_db TO binder_user;
\q
```

### Step 3: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configurations
nano .env
```

### Step 4: Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create Service Account credentials
5. Download credentials.json
6. Place in project root
7. Share your Google Sheet with the service account email

### Step 5: Django Setup

```bash
# Create Django project
django-admin startproject binder_config .

# Create apps
python manage.py startapp auth_service
python manage.py startapp inventory_management
python manage.py startapp community
python manage.py startapp load_balancer

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 📁 Project Structure

```
binder_backend/
├── binder_config/          # Main Django configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── auth_service/           # Pillar 1: Authentication
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── utils/
│       ├── email_verification.py
│       └── jwt_handler.py
├── inventory_management/   # Pillar 2: IMS
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── community/              # Pillar 3: Community Forum
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── load_balancer/          # Pillar 4: Health & Monitoring
│   ├── health_checks.py
│   ├── monitors.py
│   └── urls.py
├── shared/                 # Shared utilities
│   ├── google_sheets.py
│   ├── permissions.py
│   └── exceptions.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔐 Authentication Flow

1. **Tenant Creation** (Backend Admin Only)
   - Master admin creates tenant accounts
   - Sets user limits (default: 40)
   - Assigns initial credentials

2. **User Registration**
   - User registers with email and password
   - **Email verification is automatically skipped** (Twilio verification will be added later)
   - Account is immediately activated and ready to use

3. **Login**
   - Email + Password
   - Returns JWT access & refresh tokens
   - Frontend stores tokens

4. **Member Management** (Tenant)
   - Tenant creates employee accounts
   - Assigns roles & designations
   - Sets permissions via toggle buttons

**Note**: Email verification is currently disabled. Users are auto-verified on registration. Twilio OTP verification will be implemented in the future.

## 🎯 User Roles

- **Master Admin**: Full system access, creates tenants
- **Tenant Owner**: Manages their organization, creates members
- **Manager**: Department-level access
- **General Manager**: Cross-department access
- **Inventory Manager**: IMS-specific access
- **Custom Roles**: Tenant-defined with custom permissions

## 🔧 API Endpoints

### Auth Service
```
POST   /api/auth/register/              # Email registration
POST   /api/auth/verify-email/          # Email verification
POST   /api/auth/login/                 # Login (returns JWT)
POST   /api/auth/refresh/               # Refresh token
POST   /api/auth/logout/                # Logout
GET    /api/auth/me/                    # Current user
POST   /api/auth/members/               # Create member (tenant only)
GET    /api/auth/members/               # List members
PATCH  /api/auth/members/{id}/          # Update member
```

### Google Sheets
```
GET    /api/sheets/departments/         # Fetch departments
POST   /api/sheets/departments/         # Add department
GET    /api/sheets/accessories/         # Fetch accessories
POST   /api/sheets/accessories/         # Add accessory
```

### Health Monitoring
```
GET    /api/health/                     # System health
GET    /api/health/detailed/            # Detailed health report
```

## 🛠️ Development Commands

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run tests
pytest

# Create app
python manage.py startapp app_name

# Collect static files (production)
python manage.py collectstatic
```

## 🌐 Frontend Integration

The backend is designed to work with the React frontend:
- CORS configured for localhost:5173 (Vite)
- JWT authentication
- RESTful API responses
- Google Sheets integration for departments

## 📊 Google Sheets Integration

Currently used for:
- Department code creation
- Accessories management
- Future: Additional configurations

## 🔮 Future Features

- [x] Email verification (currently skipped - auto-verified)
- [ ] Mobile OTP via Twilio (will replace email verification)
- [ ] WhatsApp OTP via Wati API
- [ ] AI Chatbot for Community
- [ ] Advanced analytics
- [ ] Mobile app support
- [ ] Multi-language support

## 🐛 Debugging

```bash
# Enable debug mode
DEBUG=True in .env

# View logs
tail -f logs/debug.log

# Django shell
python manage.py shell
```

## 🚀 Production Deployment

### Quick Start

**Local Development:**
```bash
./start.sh
# or
python manage.py runserver
```

**Production Build (Render/OLS):**
```bash
./build.sh
# or manually:
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn binder_config.wsgi:application
```

### Render Deployment

1. **Using render.yaml** (Recommended)
   - Push code to GitHub
   - Connect repository to Render
   - Render will auto-detect `render.yaml` and configure everything

2. **Manual Setup**
   - Create Web Service in Render Dashboard
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn binder_config.wsgi:application`
   - Add PostgreSQL database
   - Set environment variables (see DEPLOYMENT.md)

### Environment Variables for Production
```
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<postgresql-url>
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
RENDER_EXTERNAL_HOSTNAME=<auto-provided-by-render>
```

**See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.**

## 📝 License

Proprietary - Next 33 Lab

## 👥 Contact

Vikram - Next 33 Lab
Email: support@binder.com
# Binder-backend
