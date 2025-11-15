from django.db import models
from django.utils import timezone
from django.db.models import Max
import uuid


class Department(models.Model):
    """
    Department Model
    Represents different departments in the inventory management system
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Department Information
    code = models.CharField(max_length=50, unique=True, db_index=True)  # e.g., 'chd-code', 'chd-po'
    name = models.CharField(max_length=255)  # e.g., 'CHD CODE CREATION', 'CHD PO ISSUE'
    description = models.TextField(blank=True, null=True)
    
    # Display Order
    display_order = models.IntegerField(default=0, help_text="Order in which department appears in menu")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Tenant Relationship (optional - can be shared across tenants)
    tenant = models.ForeignKey(
        'auth_service.Tenant',
        on_delete=models.CASCADE,
        related_name='departments',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth_service.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_departments'
    )
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Segment(models.Model):
    """
    Segment Model
    Represents segments/sub-menus within a department
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Segment Information
    code = models.CharField(max_length=50, db_index=True)  # e.g., 'buyer', 'vendor', 'factory'
    name = models.CharField(max_length=255)  # e.g., 'BUYER', 'VENDOR', 'FACTORY'
    description = models.TextField(blank=True, null=True)
    
    # Department Relationship
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='segments'
    )
    
    # Display Order
    display_order = models.IntegerField(default=0, help_text="Order in which segment appears in submenu")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth_service.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_segments'
    )
    
    class Meta:
        db_table = 'segments'
        verbose_name = 'Segment'
        verbose_name_plural = 'Segments'
        ordering = ['department', 'display_order', 'name']
        unique_together = [['department', 'code']]  # Code must be unique within a department
        indexes = [
            models.Index(fields=['department', 'code']),
            models.Index(fields=['department', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.department.name} - {self.name} ({self.code})"


class BuyerCode(models.Model):
    """
    Buyer Code Model
    Stores buyer information with auto-generated sequential codes (101A, 102A, etc.)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Auto-generated code (101A, 102A, 103A, etc.)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Buyer Information
    buyer_name = models.CharField(max_length=255)
    buyer_address = models.TextField()
    contact_person = models.CharField(max_length=255)
    retailer = models.CharField(max_length=255)
    
    # Tenant Relationship
    tenant = models.ForeignKey(
        'auth_service.Tenant',
        on_delete=models.CASCADE,
        related_name='buyer_codes',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth_service.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_buyer_codes'
    )
    
    class Meta:
        db_table = 'buyer_codes'
        verbose_name = 'Buyer Code'
        verbose_name_plural = 'Buyer Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['buyer_name']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.buyer_name}"
    
    @classmethod
    def generate_next_code(cls, tenant=None):
        """
        Generate the next buyer code in sequence (101A, 102A, etc.)
        Starts from 101A if no codes exist
        """
        # Filter by tenant if provided, otherwise get all
        queryset = cls.objects.all()
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        
        # Get the highest existing code number
        last_code = queryset.aggregate(Max('code'))['code__max']
        
        if last_code:
            # Extract number from code (e.g., "101A" -> 101)
            try:
                # Remove 'A' suffix and convert to int
                last_number = int(last_code.replace('A', ''))
                next_number = last_number + 1
            except (ValueError, AttributeError):
                # If parsing fails, start from 101
                next_number = 101
        else:
            # No codes exist, start from 101
            next_number = 101
        
        # Format as "XXXA"
        return f"{next_number}A"
    
    def save(self, *args, **kwargs):
        """Auto-generate code if not provided"""
        if not self.code:
            self.code = self.generate_next_code(tenant=self.tenant)
        super().save(*args, **kwargs)


class VendorCode(models.Model):
    """
    Vendor Code Model
    Stores vendor information with auto-generated sequential numeric codes (101, 102, etc.)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Auto-generated code (101, 102, 103, etc.)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Vendor Information
    vendor_name = models.CharField(max_length=255)
    address = models.TextField()
    gst = models.CharField(max_length=15, db_index=True)  # GST Number
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, db_index=True)
    whatsapp_number = models.CharField(max_length=15)
    alt_whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Banking Details
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11)
    
    # Job Work Details
    job_work_category = models.CharField(max_length=255)
    job_work_sub_category = models.CharField(max_length=255)
    
    # Payment Terms
    payment_terms = models.TextField()
    
    # Tenant Relationship
    tenant = models.ForeignKey(
        'auth_service.Tenant',
        on_delete=models.CASCADE,
        related_name='vendor_codes',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth_service.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_vendor_codes'
    )
    
    class Meta:
        db_table = 'vendor_codes'
        verbose_name = 'Vendor Code'
        verbose_name_plural = 'Vendor Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['vendor_name']),
            models.Index(fields=['gst']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.vendor_name}"
    
    @classmethod
    def generate_next_code(cls, tenant=None):
        """
        Generate the next vendor code in sequence (101, 102, etc.)
        Starts from 101 if no codes exist
        """
        # Filter by tenant if provided, otherwise get all
        queryset = cls.objects.all()
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        
        # Get the highest existing code number
        last_code = queryset.aggregate(Max('code'))['code__max']
        
        if last_code:
            # Extract number from code (e.g., "101" -> 101)
            try:
                last_number = int(last_code)
                next_number = last_number + 1
            except (ValueError, AttributeError):
                # If parsing fails, start from 101
                next_number = 101
        else:
            # No codes exist, start from 101
            next_number = 101
        
        # Return as string
        return str(next_number)
    
    def save(self, *args, **kwargs):
        """Auto-generate code if not provided"""
        if not self.code:
            self.code = self.generate_next_code(tenant=self.tenant)
        super().save(*args, **kwargs)
