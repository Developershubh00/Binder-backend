"""
Auth Service Models - Pillar 1
Complete multi-tenant user management system
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('role', 'master_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    Supports multi-tenant architecture with role-based access control
    """
    
    ROLE_CHOICES = [
        ('master_admin', 'Master Admin'),       # Full system access
        ('tenant_owner', 'Tenant Owner'),       # Organization owner
        ('manager', 'Manager'),                 # Department manager
        ('general_manager', 'General Manager'), # Cross-department
        ('inventory_manager', 'Inventory Manager'), # IMS specific
        ('supervisor', 'Supervisor'),            # Supervisor role
        ('attendant', 'Attendant'),             # Attendant role
        ('accountant', 'Accountant'),           # Accountant role
        ('vendor', 'Vendor'),                   # Vendor role
        ('distributor', 'Distributor'),         # Distributor role
        ('employee', 'Employee'),               # Basic access
        ('custom', 'Custom Role'),              # Tenant-defined custom role
    ]
    
    # Primary Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        db_index=True
    )
    # Email OTP (Current implementation)
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    email_otp_created_at = models.DateTimeField(null=True, blank=True)
    email_otp_verified = models.BooleanField(default=False)

    # Password reset token
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Profile Information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # Role & Access
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='employee')
    designation = models.CharField(max_length=100, blank=True)  # Custom designation
    custom_role_name = models.CharField(max_length=100, blank=True, null=True)  # For 'custom' role type
    
    # Tenant Relationship
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True
    )
    
    # Status Flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Email Verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Future: Mobile OTP (Twilio/Wati)
    # mobile_verified = models.BooleanField(default=False)
    # mobile_otp = models.CharField(max_length=6, blank=True, null=True)
    # mobile_otp_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['email_verification_token']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        """Return the short name of the user"""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_tenant_owner(self):
        """Check if user is a tenant owner"""
        return self.role == 'tenant_owner'
    
    @property
    def is_master_admin(self):
        """Check if user is master admin"""
        return self.role == 'master_admin'
    
    @property
    def can_create_members(self):
        """Check if user can create members"""
        return self.role in ['master_admin', 'tenant_owner']


class Tenant(models.Model):
    """
    Tenant/Organization Model
    Represents a company/organization using the SaaS platform
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Company Information
    company_name = models.CharField(max_length=255, unique=True)
    company_email = models.EmailField(max_length=255)
    company_phone = models.CharField(max_length=15, blank=True)
    company_address = models.TextField(blank=True)
    
    # Subscription Details
    user_limit = models.IntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Maximum number of users allowed (1-1000)"
    )
    current_user_count = models.IntegerField(default=0)
    
    # Plan Information
    PLAN_CHOICES = [
        ('basic', 'Basic Plan'),
        ('standard', 'Standard Plan'),
        ('premium', 'Premium Plan'),
        ('enterprise', 'Enterprise Plan'),
        ('custom', 'Custom Plan'),
    ]
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='standard',
        help_text="Tenant subscription plan"
    )
    
    # Tenant Logo
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    subscription_start_date = models.DateField(default=timezone.now)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.company_name
    
    @property
    def can_add_users(self):
        """Check if tenant can add more users"""
        return self.current_user_count < self.user_limit
    
    @property
    def available_slots(self):
        """Return number of available user slots"""
        return self.user_limit - self.current_user_count
    
    def increment_user_count(self):
        """Increment current user count"""
        self.current_user_count += 1
        self.save()
    
    def decrement_user_count(self):
        """Decrement current user count"""
        if self.current_user_count > 0:
            self.current_user_count -= 1
            self.save()


class Permission(models.Model):
    """
    Custom Permissions for Role-Based Access Control
    Tenant owners can create custom roles with specific permissions
    """
    
    PERMISSION_CATEGORIES = [
        ('master_sheets', 'Master Sheets'),
        ('ims', 'Inventory Management System (IMS)'),
        ('sourcing', 'Sourcing'),
        ('community', 'Community'),
        ('reports', 'Reports'),
        ('settings', 'Settings'),
        ('members', 'Member Management'),
    ]
    
    ACTION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('approve', 'Approve'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Permission Details
    category = models.CharField(max_length=50, choices=PERMISSION_CATEGORIES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=100)  # e.g., 'products', 'orders'
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        unique_together = ['category', 'action', 'resource']
    
    def __str__(self):
        return f"{self.category}.{self.action}.{self.resource}"


class RolePermission(models.Model):
    """
    Mapping between Users and Permissions
    Allows granular permission control via toggle buttons in frontend
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    # Toggle status
    is_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_permissions'
    )
    
    class Meta:
        db_table = 'role_permissions'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = ['user', 'permission']
    
    def __str__(self):
        return f"{self.user.email} - {self.permission}"


class LoginHistory(models.Model):
    """
    Track user login history for security and analytics
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    
    # Login Details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_successful = models.BooleanField(default=True)
    
    # Timestamps
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login History'
        ordering = ['-login_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_at}"
