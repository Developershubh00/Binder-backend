from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Tenant, Permission, RolePermission, LoginHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'custom_role_name', 'tenant', 'is_active', 'email_verified']
    list_filter = ['role', 'is_active', 'email_verified', 'tenant']
    search_fields = ['email', 'first_name', 'last_name', 'custom_role_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Role & Access', {'fields': ('role', 'custom_role_name', 'designation', 'tenant')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified')}),
        ('Timestamps', {'fields': ('date_joined', 'last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'custom_role_name', 'tenant'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ['company_name', 'company_email', 'plan', 'current_user_count', 'user_limit', 'available_slots_display', 'is_active', 'created_at']
    search_fields = ['company_name', 'company_email']
    list_filter = ['is_active', 'plan', 'created_at']
    readonly_fields = ['id', 'current_user_count', 'available_slots_display', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('id', 'company_name', 'company_email', 'company_phone', 'company_address')
        }),
        ('Subscription & Plan', {
            'fields': ('plan', 'user_limit', 'current_user_count', 'available_slots_display', 'is_active')
        }),
        ('Logo', {
            'fields': ('logo',)
        }),
        ('Subscription Dates', {
            'fields': ('subscription_start_date', 'subscription_end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def available_slots_display(self, obj):
        """Display available user slots"""
        slots = obj.available_slots
        if slots > 0:
            return f"{slots} available"
        return "No slots available"
    available_slots_display.short_description = 'Available Slots'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()

@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ['category', 'action', 'resource']
    list_filter = ['category', 'action']

@admin.register(RolePermission)
class RolePermissionAdmin(ModelAdmin):
    list_display = ['user', 'permission', 'is_enabled']
    list_filter = ['is_enabled']

@admin.register(LoginHistory)
class LoginHistoryAdmin(ModelAdmin):
    list_display = ['user', 'ip_address', 'login_successful', 'login_at']
    list_filter = ['login_successful', 'login_at']
