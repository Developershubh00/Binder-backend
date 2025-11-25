"""
Auth Service Serializers
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Tenant, Permission, RolePermission


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model"""
    
    available_slots = serializers.ReadOnlyField()
    can_add_users = serializers.ReadOnlyField()
    logo = serializers.ImageField(read_only=True)
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'company_name', 'company_email', 'company_phone',
            'company_address', 'user_limit', 'current_user_count',
            'available_slots', 'can_add_users', 'is_active', 'plan',
            'subscription_start_date', 'subscription_end_date',
            'logo', 'logo_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_user_count', 'created_at', 'updated_at']
    
    def validate_user_limit(self, value):
        """Validate user limit is between 1 and 1000"""
        if value < 1 or value > 1000:
            raise serializers.ValidationError("User limit must be between 1 and 1000")
        return value
    
    def get_logo_url(self, obj):
        """Get logo URL"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    tenant_name = serializers.CharField(source='tenant.company_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'designation', 'tenant', 'tenant_name',
            'is_active', 'email_verified', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            print("Authenticating user...")
            print(f"Email: {email}")
            print(f"Password: {password}")
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            print(f"Authenticated user: {user}")
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
            
            # Skip email verification check (Twilio verification will be added later)
            # if not user.email_verified:
            #     raise serializers.ValidationError(
            #         'Email not verified. Please verify your email first.',
            #         code='email_not_verified'
            #     )
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )
        
        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    token = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset"""
    
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs


class CreateMemberSerializer(serializers.ModelSerializer):
    """Serializer for tenant to create members with permissions"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    custom_role_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    permissions = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="List of permission IDs to assign to the user"
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'phone', 'role', 'designation', 'custom_role_name', 'permissions'
        ]
    
    def validate(self, attrs):
        """Validate member creation"""
        # Get the request user (tenant owner)
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        # Check if user can create members
        if not request.user.can_create_members:
            raise serializers.ValidationError(
                "You don't have permission to create members"
            )
        
        # Check tenant user limit
        if request.user.tenant and not request.user.tenant.can_add_users:
            raise serializers.ValidationError(
                f"User limit reached. Your plan allows {request.user.tenant.user_limit} users."
            )
        
        # Validate custom role name if role is 'custom'
        if attrs.get('role') == 'custom':
            if not attrs.get('custom_role_name') or not attrs.get('custom_role_name').strip():
                raise serializers.ValidationError({
                    'custom_role_name': 'Custom role name is required when role is set to "custom"'
                })
        elif attrs.get('custom_role_name'):
            # Clear custom_role_name if role is not 'custom'
            attrs['custom_role_name'] = None
        
        return attrs
    
    def create(self, validated_data):
        """Create new member with permissions"""
        request = self.context.get('request')
        permission_ids = validated_data.pop('permissions', [])
        custom_role_name = validated_data.pop('custom_role_name', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Set custom role name if provided
        needs_save = False
        if custom_role_name:
            user.custom_role_name = custom_role_name.strip()
            needs_save = True
        
        # Assign to tenant
        if request.user.tenant:
            user.tenant = request.user.tenant
            user.created_by = request.user
            needs_save = True
            
            # Increment tenant user count
            request.user.tenant.increment_user_count()
        
        # Save user if any changes were made
        if needs_save:
            user.save()
        
        # Assign permissions if provided
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            for permission in permissions:
                RolePermission.objects.create(
                    user=user,
                    permission=permission,
                    is_enabled=True,
                    granted_by=request.user
                )
        
        return user


class UpdateMemberSerializer(serializers.ModelSerializer):
    """Serializer for updating member details"""
    
    custom_role_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'role', 'custom_role_name', 'designation', 'is_active'
        ]
    
    def validate(self, attrs):
        """Validate custom role name"""
        if attrs.get('role') == 'custom':
            if not attrs.get('custom_role_name') or not attrs.get('custom_role_name').strip():
                raise serializers.ValidationError({
                    'custom_role_name': 'Custom role name is required when role is set to "custom"'
                })
        elif attrs.get('custom_role_name'):
            attrs['custom_role_name'] = None
        return attrs


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model"""
    
    class Meta:
        model = Permission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for Role Permission mapping"""
    
    permission_details = PermissionSerializer(source='permission', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    granted_by_email = serializers.CharField(source='granted_by.email', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'user', 'user_email', 'permission', 'permission_details',
            'is_enabled', 'granted_by', 'granted_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with permissions"""
    
    tenant_details = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    custom_role_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'custom_role_name', 'designation', 'tenant', 'tenant_details',
            'is_active', 'email_verified', 'permissions',
            'date_joined', 'last_login', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_tenant_details(self, obj):
        """Get tenant details with logo"""
        if obj.tenant:
            return {
                'id': str(obj.tenant.id),
                'company_name': obj.tenant.company_name,
                'logo': obj.tenant.logo.url if obj.tenant.logo else None
            }
        return None
    
    def get_permissions(self, obj):
        """Get user permissions with enabled status"""
        role_permissions = obj.role_permissions.select_related('permission').all()
        return [
            {
                'id': str(rp.permission.id),
                'permission_id': str(rp.id),
                'category': rp.permission.category,
                'action': rp.permission.action,
                'resource': rp.permission.resource,
                'description': rp.permission.description,
                'is_enabled': rp.is_enabled
            }
            for rp in role_permissions
        ]


class UserPermissionUpdateSerializer(serializers.Serializer):
    """Serializer for updating user permissions"""
    permissions = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of permission objects with 'permission_id' and 'is_enabled'"
    )
    
    def validate_permissions(self, value):
        """Validate permissions list"""
        for perm in value:
            if 'permission_id' not in perm:
                raise serializers.ValidationError("Each permission must have 'permission_id'")
            if 'is_enabled' not in perm:
                raise serializers.ValidationError("Each permission must have 'is_enabled'")
        return value


class TenantLogoSerializer(serializers.ModelSerializer):
    """Serializer for tenant logo upload"""
    
    class Meta:
        model = Tenant
        fields = ['logo']
    
    def update(self, instance, validated_data):
        """Update tenant logo"""
        instance.logo = validated_data.get('logo', instance.logo)
        instance.save()
        return instance
