from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Department, Segment, BuyerCode, VendorCode


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    """Admin interface for Department model"""
    
    list_display = ['name', 'code', 'display_order', 'is_active', 'segments_count', 'tenant', 'created_at']
    list_filter = ['is_active', 'tenant', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['display_order', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'code', 'name', 'description', 'display_order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Relationships', {
            'fields': ('tenant', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def segments_count(self, obj):
        """Display count of segments"""
        return obj.segments.count()
    segments_count.short_description = 'Segments'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('segments').select_related('tenant', 'created_by')


@admin.register(Segment)
class SegmentAdmin(ModelAdmin):
    """Admin interface for Segment model"""
    
    list_display = ['name', 'code', 'department', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'code', 'description', 'department__name']
    ordering = ['department', 'display_order', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'code', 'name', 'description', 'display_order')
        }),
        ('Relationships', {
            'fields': ('department', 'created_by')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('department', 'department__tenant', 'created_by')


@admin.register(BuyerCode)
class BuyerCodeAdmin(ModelAdmin):
    """Admin interface for BuyerCode model"""
    
    list_display = ['code', 'buyer_name', 'retailer', 'contact_person', 'tenant', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['code', 'buyer_name', 'retailer', 'contact_person', 'buyer_address']
    ordering = ['-created_at']
    readonly_fields = ['id', 'code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('id', 'code')
        }),
        ('Buyer Information', {
            'fields': ('buyer_name', 'buyer_address', 'contact_person', 'retailer')
        }),
        ('Relationships', {
            'fields': ('tenant', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('tenant', 'created_by')
    
    def has_change_permission(self, request, obj=None):
        """Allow editing buyer information but not the code"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion"""
        return True


@admin.register(VendorCode)
class VendorCodeAdmin(ModelAdmin):
    """Admin interface for VendorCode model"""
    
    list_display = ['code', 'vendor_name', 'gst', 'job_work_category', 'contact_person', 'email', 'tenant', 'created_at']
    list_filter = ['tenant', 'job_work_category', 'created_at']
    search_fields = ['code', 'vendor_name', 'gst', 'email', 'contact_person', 'job_work_category', 'address']
    ordering = ['-created_at']
    readonly_fields = ['id', 'code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('id', 'code')
        }),
        ('Vendor Information', {
            'fields': ('vendor_name', 'address', 'gst', 'contact_person', 'email', 'whatsapp_number', 'alt_whatsapp_number')
        }),
        ('Banking Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code')
        }),
        ('Job Work Details', {
            'fields': ('job_work_category', 'job_work_sub_category')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms',)
        }),
        ('Relationships', {
            'fields': ('tenant', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('tenant', 'created_by')
    
    def has_change_permission(self, request, obj=None):
        """Allow editing vendor information but not the code"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion"""
        return True
