from rest_framework import serializers
import re
from .models import Department, Segment, BuyerCode, VendorCode


class SegmentSerializer(serializers.ModelSerializer):
    """Serializer for Segment model"""
    
    class Meta:
        model = Segment
        fields = [
            'id', 'code', 'name', 'description', 'department', 
            'display_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """Validate segment code"""
        if not value:
            raise serializers.ValidationError("Segment code is required")
        return value.lower().strip()


class SegmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Segment with department info"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    
    class Meta:
        model = Segment
        fields = [
            'id', 'code', 'name', 'description', 'department', 
            'department_name', 'department_code',
            'display_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'department_name', 'department_code']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    segments = SegmentSerializer(many=True, read_only=True)
    segments_count = serializers.IntegerField(source='segments.count', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'display_order', 
            'is_active', 'tenant', 'segments', 'segments_count',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'segments_count']
    
    def validate_code(self, value):
        """Validate department code"""
        if not value:
            raise serializers.ValidationError("Department code is required")
        return value.lower().strip()


class DepartmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for department list"""
    
    segments_count = serializers.IntegerField(source='segments.count', read_only=True)
    active_segments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'display_order', 
            'is_active', 'segments_count', 'active_segments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_segments_count(self, obj):
        """Get count of active segments"""
        return obj.segments.filter(is_active=True).count()


class DepartmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating department with initial segments"""
    
    segments = SegmentSerializer(many=True, required=False)
    
    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'display_order', 
            'is_active', 'tenant', 'segments', 'created_by'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Create department and associated segments"""
        segments_data = validated_data.pop('segments', [])
        department = Department.objects.create(**validated_data)
        
        for segment_data in segments_data:
            Segment.objects.create(department=department, **segment_data)
        
        return department


class BuyerCodeSerializer(serializers.ModelSerializer):
    """Serializer for BuyerCode model"""
    
    class Meta:
        model = BuyerCode
        fields = [
            'id', 'code', 'buyer_name', 'buyer_address', 'contact_person',
            'retailer', 'tenant', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def validate_buyer_name(self, value):
        """Validate buyer name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Buyer name is required")
        return value.strip()
    
    def validate_buyer_address(self, value):
        """Validate buyer address"""
        if not value or not value.strip():
            raise serializers.ValidationError("Buyer address is required")
        return value.strip()
    
    def validate_contact_person(self, value):
        """Validate contact person"""
        if not value or not value.strip():
            raise serializers.ValidationError("Contact person is required")
        return value.strip()
    
    def validate_retailer(self, value):
        """Validate retailer"""
        if not value or not value.strip():
            raise serializers.ValidationError("Retailer is required")
        return value.strip()


class BuyerCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating buyer code (code is auto-generated)"""
    
    class Meta:
        model = BuyerCode
        fields = [
            'id', 'code', 'buyer_name', 'buyer_address', 'contact_person',
            'retailer', 'tenant'
        ]
        read_only_fields = ['id', 'code']
    
    def validate_buyer_name(self, value):
        """Validate buyer name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Buyer name is required")
        return value.strip()
    
    def validate_buyer_address(self, value):
        """Validate buyer address"""
        if not value or not value.strip():
            raise serializers.ValidationError("Buyer address is required")
        return value.strip()
    
    def validate_contact_person(self, value):
        """Validate contact person"""
        if not value or not value.strip():
            raise serializers.ValidationError("Contact person is required")
        return value.strip()
    
    def validate_retailer(self, value):
        """Validate retailer"""
        if not value or not value.strip():
            raise serializers.ValidationError("Retailer is required")
        return value.strip()
    
    def create(self, validated_data):
        """Create buyer code with auto-generated code"""
        request = self.context.get('request')
        user = request.user if request else None
        
        # Get tenant from user if not provided
        if 'tenant' not in validated_data and user and user.tenant:
            validated_data['tenant'] = user.tenant
        
        # Create buyer code (code will be auto-generated in save method)
        buyer_code = BuyerCode.objects.create(
            **validated_data,
            created_by=user
        )
        
        return buyer_code


class BuyerCodeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for buyer code list"""
    
    class Meta:
        model = BuyerCode
        fields = [
            'id', 'code', 'buyer_name', 'retailer', 'contact_person',
            'created_at'
        ]
        read_only_fields = ['id', 'code', 'created_at']


class VendorCodeSerializer(serializers.ModelSerializer):
    """Serializer for VendorCode model"""
    
    class Meta:
        model = VendorCode
        fields = [
            'id', 'code', 'vendor_name', 'address', 'gst', 'bank_name',
            'account_number', 'ifsc_code', 'job_work_category', 'job_work_sub_category',
            'contact_person', 'whatsapp_number', 'alt_whatsapp_number', 'email',
            'payment_terms', 'tenant', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def validate_gst(self, value):
        """Validate GST number format"""
        if not value:
            raise serializers.ValidationError("GST number is required")
        # GST format: 22AAAAA0000A1Z5 (15 characters)
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gst_pattern, value.upper()):
            raise serializers.ValidationError("Please enter a valid GST number (e.g., 22AAAAA0000A1Z5)")
        return value.upper()
    
    def validate_ifsc_code(self, value):
        """Validate IFSC code format"""
        if not value:
            raise serializers.ValidationError("IFSC code is required")
        # IFSC format: AAAA0XXXXX (11 characters)
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        if not re.match(ifsc_pattern, value.upper()):
            raise serializers.ValidationError("Please enter a valid IFSC code (e.g., SBIN0000123)")
        return value.upper()
    
    def validate_whatsapp_number(self, value):
        """Validate WhatsApp number format"""
        if not value:
            raise serializers.ValidationError("WhatsApp number is required")
        # Remove spaces and check if it's 10 digits
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise serializers.ValidationError("Please enter a valid 10-digit WhatsApp number")
        return cleaned
    
    def validate_alt_whatsapp_number(self, value):
        """Validate alternative WhatsApp number format (optional)"""
        if value:
            cleaned = value.replace(' ', '').replace('-', '')
            if not cleaned.isdigit() or len(cleaned) != 10:
                raise serializers.ValidationError("Please enter a valid 10-digit WhatsApp number")
            return cleaned
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Please enter a valid email address")
        return value.lower()
    
    def validate_vendor_name(self, value):
        """Validate vendor name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Vendor name is required")
        return value.strip()
    
    def validate_address(self, value):
        """Validate address"""
        if not value or not value.strip():
            raise serializers.ValidationError("Address is required")
        return value.strip()
    
    def validate_contact_person(self, value):
        """Validate contact person"""
        if not value or not value.strip():
            raise serializers.ValidationError("Contact person is required")
        return value.strip()
    
    def validate_bank_name(self, value):
        """Validate bank name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Bank name is required")
        return value.strip()
    
    def validate_account_number(self, value):
        """Validate account number"""
        if not value or not value.strip():
            raise serializers.ValidationError("Account number is required")
        return value.strip()
    
    def validate_job_work_category(self, value):
        """Validate job work category"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job work category is required")
        return value.strip()
    
    def validate_job_work_sub_category(self, value):
        """Validate job work sub-category"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job work sub-category is required")
        return value.strip()
    
    def validate_payment_terms(self, value):
        """Validate payment terms"""
        if not value or not value.strip():
            raise serializers.ValidationError("Payment terms is required")
        return value.strip()


class VendorCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vendor code (code is auto-generated)"""
    
    class Meta:
        model = VendorCode
        fields = [
            'id', 'code', 'vendor_name', 'address', 'gst', 'bank_name',
            'account_number', 'ifsc_code', 'job_work_category', 'job_work_sub_category',
            'contact_person', 'whatsapp_number', 'alt_whatsapp_number', 'email',
            'payment_terms', 'tenant'
        ]
        read_only_fields = ['id', 'code']
    
    def validate_gst(self, value):
        """Validate GST number format"""
        if not value:
            raise serializers.ValidationError("GST number is required")
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gst_pattern, value.upper()):
            raise serializers.ValidationError("Please enter a valid GST number (e.g., 22AAAAA0000A1Z5)")
        return value.upper()
    
    def validate_ifsc_code(self, value):
        """Validate IFSC code format"""
        if not value:
            raise serializers.ValidationError("IFSC code is required")
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        if not re.match(ifsc_pattern, value.upper()):
            raise serializers.ValidationError("Please enter a valid IFSC code (e.g., SBIN0000123)")
        return value.upper()
    
    def validate_whatsapp_number(self, value):
        """Validate WhatsApp number format"""
        if not value:
            raise serializers.ValidationError("WhatsApp number is required")
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise serializers.ValidationError("Please enter a valid 10-digit WhatsApp number")
        return cleaned
    
    def validate_alt_whatsapp_number(self, value):
        """Validate alternative WhatsApp number format (optional)"""
        if value:
            cleaned = value.replace(' ', '').replace('-', '')
            if not cleaned.isdigit() or len(cleaned) != 10:
                raise serializers.ValidationError("Please enter a valid 10-digit WhatsApp number")
            return cleaned
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Please enter a valid email address")
        return value.lower()
    
    def validate_vendor_name(self, value):
        """Validate vendor name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Vendor name is required")
        return value.strip()
    
    def validate_address(self, value):
        """Validate address"""
        if not value or not value.strip():
            raise serializers.ValidationError("Address is required")
        return value.strip()
    
    def validate_contact_person(self, value):
        """Validate contact person"""
        if not value or not value.strip():
            raise serializers.ValidationError("Contact person is required")
        return value.strip()
    
    def validate_bank_name(self, value):
        """Validate bank name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Bank name is required")
        return value.strip()
    
    def validate_account_number(self, value):
        """Validate account number"""
        if not value or not value.strip():
            raise serializers.ValidationError("Account number is required")
        return value.strip()
    
    def validate_job_work_category(self, value):
        """Validate job work category"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job work category is required")
        return value.strip()
    
    def validate_job_work_sub_category(self, value):
        """Validate job work sub-category"""
        if not value or not value.strip():
            raise serializers.ValidationError("Job work sub-category is required")
        return value.strip()
    
    def validate_payment_terms(self, value):
        """Validate payment terms"""
        if not value or not value.strip():
            raise serializers.ValidationError("Payment terms is required")
        return value.strip()
    
    def create(self, validated_data):
        """Create vendor code with auto-generated code"""
        request = self.context.get('request')
        user = request.user if request else None
        
        # Get tenant from user if not provided
        if 'tenant' not in validated_data and user and user.tenant:
            validated_data['tenant'] = user.tenant
        
        # Create vendor code (code will be auto-generated in save method)
        vendor_code = VendorCode.objects.create(
            **validated_data,
            created_by=user
        )
        
        return vendor_code


class VendorCodeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vendor code list"""
    
    class Meta:
        model = VendorCode
        fields = [
            'id', 'code', 'vendor_name', 'gst', 'job_work_category',
            'contact_person', 'email', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'created_at']
