#!/bin/bash

# Script to create all remaining Django files

# Create auth_service files
mkdir -p auth_service/utils
mkdir -p auth_service/migrations

# auth_service/__init__.py
cat > auth_service/__init__.py << 'EOF'
default_app_config = 'auth_service.apps.AuthServiceConfig'
EOF

# auth_service/apps.py
cat > auth_service/apps.py << 'EOF'
from django.apps import AppConfig

class AuthServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_service'
    verbose_name = 'Authentication Service'
EOF

# auth_service/admin.py
cat > auth_service/admin.py << 'EOF'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Tenant, Permission, RolePermission, LoginHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'tenant', 'is_active', 'email_verified']
    list_filter = ['role', 'is_active', 'email_verified', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Role & Access', {'fields': ('role', 'designation', 'tenant')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified')}),
        ('Timestamps', {'fields': ('date_joined', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'tenant'),
        }),
    )

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_email', 'current_user_count', 'user_limit', 'is_active']
    search_fields = ['company_name', 'company_email']
    list_filter = ['is_active']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['category', 'action', 'resource']
    list_filter = ['category', 'action']

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'is_enabled']
    list_filter = ['is_enabled']

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_successful', 'login_at']
    list_filter = ['login_successful', 'login_at']
EOF

# auth_service/urls.py
cat > auth_service/urls.py << 'EOF'
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, VerifyEmailView, LoginView, LogoutView,
    CurrentUserView, MemberViewSet, TenantViewSet,
    toggle_permission, resend_verification_email
)

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'tenants', TenantViewSet, basename='tenant')

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', resend_verification_email, name='resend-verification'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User
    path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # Permissions
    path('members/<uuid:user_id>/permissions/<uuid:permission_id>/toggle/', 
         toggle_permission, name='toggle-permission'),
    
    # Router URLs
    path('', include(router.urls)),
]
EOF

# auth_service/utils/__init__.py
cat > auth_service/utils/__init__.py << 'EOF'
EOF

# auth_service/utils/email_verification.py
cat > auth_service/utils/email_verification.py << 'EOF'
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_verification_email(user):
    """Send email verification link"""
    
    # In production, use actual frontend URL
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}"
    
    subject = 'Verify your Binder account'
    
    # For development, just print to console
    if settings.DEBUG:
        print(f"\n{'='*60}")
        print(f"EMAIL VERIFICATION")
        print(f"To: {user.email}")
        print(f"Subject: {subject}")
        print(f"Verification URL: {verification_url}")
        print(f"Token: {user.email_verification_token}")
        print(f"{'='*60}\n")
    
    message = f"""
    Hi {user.get_full_name()},
    
    Welcome to Binder! Please verify your email address by clicking the link below:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    Binder Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
EOF

# Create shared utilities
mkdir -p shared

cat > shared/__init__.py << 'EOF'
EOF

cat > shared/exceptions.py << 'EOF'
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """Custom exception handler for DRF"""
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'status': 'error',
            'message': str(exc),
            'data': response.data
        }
    
    return response
EOF

cat > shared/permissions.py << 'EOF'
from rest_framework import permissions

class IsTenantOwner(permissions.BasePermission):
    """Permission class for tenant owners"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_tenant_owner

class IsMasterAdmin(permissions.BasePermission):
    """Permission class for master admins"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_master_admin

class CanManageMembers(permissions.BasePermission):
    """Permission class for users who can manage members"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_create_members
EOF

echo "Auth service files created successfully!"

# Create other app directories
for app in inventory_management community load_balancer; do
    mkdir -p $app/migrations
    
    cat > $app/__init__.py << 'EOF'
EOF
    
    cat > $app/apps.py << EOF2
from django.apps import AppConfig

class $(echo ${app^} | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1' | sed 's/ //g')Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '$app'
EOF2

    cat > $app/models.py << 'EOF'
from django.db import models

# Models will be added as we develop each pillar
EOF

    cat > $app/admin.py << 'EOF'
from django.contrib import admin

# Register your models here
EOF

    cat > $app/views.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Views will be added as we develop each pillar
EOF

    cat > $app/serializers.py << 'EOF'
from rest_framework import serializers

# Serializers will be added as we develop each pillar
EOF

    cat > $app/urls.py << 'EOF'
from django.urls import path

urlpatterns = [
    # URLs will be added as we develop each pillar
]
EOF

    echo "$app app structure created!"
done

# Create Google Sheets integration
cat > shared/google_sheets.py << 'EOF'
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
import json

class GoogleSheetsService:
    """Service for Google Sheets integration"""
    
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.initialize()
    
    def initialize(self):
        """Initialize Google Sheets client"""
        try:
            self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                self.scope
            )
            self.client = gspread.authorize(self.credentials)
        except Exception as e:
            print(f"Error initializing Google Sheets: {e}")
    
    def get_sheet(self, spreadsheet_id, sheet_name='Sheet1'):
        """Get worksheet"""
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            return worksheet
        except Exception as e:
            print(f"Error getting sheet: {e}")
            return None
    
    def get_all_records(self, spreadsheet_id, sheet_name='Sheet1'):
        """Get all records from sheet"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            return worksheet.get_all_records()
        return []
    
    def append_row(self, spreadsheet_id, values, sheet_name='Sheet1'):
        """Append row to sheet"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            worksheet.append_row(values)
            return True
        return False
    
    def update_cell(self, spreadsheet_id, row, col, value, sheet_name='Sheet1'):
        """Update specific cell"""
        worksheet = self.get_sheet(spreadsheet_id, sheet_name)
        if worksheet:
            worksheet.update_cell(row, col, value)
            return True
        return False

# Singleton instance
sheets_service = GoogleSheetsService()
EOF

cat > shared/sheets_urls.py << 'EOF'
from django.urls import path
from . import sheets_views

urlpatterns = [
    path('departments/', sheets_views.list_departments, name='list-departments'),
    path('departments/add/', sheets_views.add_department, name='add-department'),
    path('accessories/', sheets_views.list_accessories, name='list-accessories'),
    path('accessories/add/', sheets_views.add_accessory, name='add-accessory'),
]
EOF

cat > shared/sheets_views.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .google_sheets import sheets_service

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_departments(request):
    """Get all departments from Google Sheets"""
    try:
        records = sheets_service.get_all_records(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            'Departments'
        )
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_department(request):
    """Add department to Google Sheets"""
    try:
        data = request.data
        values = [
            data.get('code'),
            data.get('name'),
            data.get('description', '')
        ]
        
        success = sheets_service.append_row(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            values,
            'Departments'
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Department added successfully'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to add department'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_accessories(request):
    """Get all accessories from Google Sheets"""
    try:
        records = sheets_service.get_all_records(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            'Accessories'
        )
        return Response({
            'status': 'success',
            'data': records
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_accessory(request):
    """Add accessory to Google Sheets"""
    try:
        data = request.data
        values = [
            data.get('code'),
            data.get('name'),
            data.get('category', ''),
            data.get('description', '')
        ]
        
        success = sheets_service.append_row(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            values,
            'Accessories'
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': 'Accessory added successfully'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to add accessory'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
EOF

# Load balancer health check
cat > load_balancer/urls.py << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health-check'),
    path('detailed/', views.detailed_health, name='detailed-health'),
]
EOF

cat > load_balancer/views.py << 'EOF'
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import time

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Basic health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': time.time()
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def detailed_health(request):
    """Detailed health check with system metrics"""
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        health_status['checks']['cache'] = 'healthy' if cache_value == 'ok' else 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    return Response(health_status)
EOF

echo "All files created successfully!"
