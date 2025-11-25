"""
Auth Service Views - Pillar 1
Complete authentication flow with email verification
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
import secrets

from .models import Tenant, Permission, RolePermission, LoginHistory
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    EmailVerificationSerializer, CreateMemberSerializer,
    UpdateMemberSerializer, TenantSerializer, UserDetailSerializer,
    RolePermissionSerializer, UserPermissionUpdateSerializer,
    TenantLogoSerializer, PermissionSerializer
)
from .utils.email_verification import send_verification_email

User = get_user_model()


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """
    User Registration
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Auto-verify email (skip verification process - Twilio will be added later)
        user.email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'Registration successful. Your account is ready to use.',
            'data': {
                'email': user.email,
                'id': str(user.id),
                'email_verified': True
            }
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(generics.GenericAPIView):
    """
    Email Verification
    POST /api/auth/verify-email/
    """
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        try:
            user = User.objects.get(email_verification_token=token)
            
            # Check if token is still valid (24 hours)
            if user.email_verification_sent_at:
                time_diff = timezone.now() - user.email_verification_sent_at
                if time_diff.total_seconds() > 86400:  # 24 hours
                    return Response({
                        'status': 'error',
                        'message': 'Verification link expired. Please request a new one.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify email
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Email verified successfully. You can now login.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid verification token.'
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    User Login
    POST /api/auth/login/
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        print( "LoginView POST called" )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("serializer.validated_data")
        
        user = serializer.validated_data['user']
        print(user)
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        # Create login history
        LoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            login_successful=True
        )
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        # Prepare user data
        user_data = UserDetailSerializer(user).data
        
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'user': user_data,
                'tokens': tokens
            }
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """
    User Logout
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Update login history
            last_login = LoginHistory.objects.filter(
                user=request.user,
                logout_at__isnull=True
            ).order_by('-login_at').first()
            
            if last_login:
                last_login.logout_at = timezone.now()
                last_login.save()
            
            # Blacklist refresh token (if provided)
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'status': 'success',
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get Current User
    GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    
    def get_object(self):
        return self.request.user


class MemberViewSet(viewsets.ModelViewSet):
    """
    Member Management (for Tenant Owners)
    GET    /api/auth/members/           - List members
    POST   /api/auth/members/           - Create member
    GET    /api/auth/members/{id}/      - Get member details
    PATCH  /api/auth/members/{id}/      - Update member
    DELETE /api/auth/members/{id}/      - Deactivate member
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateMemberSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateMemberSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        """Return members of the tenant"""
        user = self.request.user
        
        if user.is_master_admin:
            # Master admin can see all users
            return User.objects.all()
        elif user.is_tenant_owner and user.tenant:
            # Tenant owner can see their members
            return User.objects.filter(tenant=user.tenant)
        else:
            # Regular users can only see themselves
            return User.objects.filter(id=user.id)
    
    def create(self, request, *args, **kwargs):
        """Create new member"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        member = serializer.save()
        
        # Auto-verify email (skip verification process - Twilio will be added later)
        member.email_verified = True
        member.save()
        
        return Response({
            'status': 'success',
            'message': 'Member created successfully',
            'data': UserDetailSerializer(member).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update member with custom role name"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Member updated successfully',
            'data': UserDetailSerializer(instance).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Deactivate member instead of deleting"""
        instance = self.get_object()
        
        # Don't allow self-deactivation
        if instance.id == request.user.id:
            return Response({
                'status': 'error',
                'message': 'You cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deactivate user
        instance.is_active = False
        instance.save()
        
        # Decrement tenant user count
        if instance.tenant:
            instance.tenant.decrement_user_count()
        
        return Response({
            'status': 'success',
            'message': 'Member deactivated successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='update-permissions')
    def update_permissions(self, request, pk=None):
        """Update user permissions"""
        user = self.get_object()
        
        # Check if requester can manage permissions
        if not request.user.can_create_members:
            return Response({
                'status': 'error',
                'message': 'You do not have permission to manage user permissions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserPermissionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        permissions_data = serializer.validated_data['permissions']
        
        # Update permissions
        for perm_data in permissions_data:
            # permission_id is the RolePermission ID (for existing permissions)
            # id is the Permission UUID (for new permissions)
            permission_id = perm_data.get('permission_id')  # RolePermission ID
            permission_uuid = perm_data.get('id')  # Permission UUID
            is_enabled = perm_data.get('is_enabled', True)
            
            # If permission_id is provided, it's an existing RolePermission
            if permission_id:
                try:
                    role_permission = RolePermission.objects.get(
                        id=permission_id,
                        user=user
                    )
                    role_permission.is_enabled = is_enabled
                    role_permission.granted_by = request.user
                    role_permission.save()
                    continue
                except RolePermission.DoesNotExist:
                    pass
            
            # If permission_uuid is provided, it's a Permission UUID (for new permissions)
            if permission_uuid:
                try:
                    permission = Permission.objects.get(id=permission_uuid)
                    # Check if RolePermission already exists
                    role_permission, created = RolePermission.objects.get_or_create(
                        user=user,
                        permission=permission,
                        defaults={
                            'is_enabled': is_enabled,
                            'granted_by': request.user
                        }
                    )
                    if not created:
                        role_permission.is_enabled = is_enabled
                        role_permission.granted_by = request.user
                        role_permission.save()
                except Permission.DoesNotExist:
                    continue
        
        return Response({
            'status': 'success',
            'message': 'Permissions updated successfully',
            'data': UserDetailSerializer(user).data
        })
    
    @action(detail=True, methods=['get'], url_path='available-permissions')
    def available_permissions(self, request, pk=None):
        """Get available permissions grouped by category for a user"""
        user = self.get_object()
        
        # Get all permissions
        all_permissions = Permission.objects.all().order_by('category', 'resource', 'action')
        
        # Get user's existing permissions
        user_permissions = {
            str(rp.permission.id): {
                'permission_id': str(rp.id),
                'is_enabled': rp.is_enabled
            }
            for rp in user.role_permissions.select_related('permission').all()
        }
        
        # Group by category
        grouped = {}
        for perm in all_permissions:
            perm_id = str(perm.id)
            if perm.category not in grouped:
                grouped[perm.category] = []
            
            # Check if user has this permission
            user_perm = user_permissions.get(perm_id, None)
            
            grouped[perm.category].append({
                'id': perm_id,
                'category': perm.category,
                'action': perm.action,
                'resource': perm.resource,
                'description': perm.description,
                'permission_id': user_perm['permission_id'] if user_perm else None,
                'is_enabled': user_perm['is_enabled'] if user_perm else False
            })
        
        return Response({
            'status': 'success',
            'data': grouped
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_permissions(request):
    """Get all available permissions grouped by category"""
    permissions = Permission.objects.all().order_by('category', 'resource', 'action')
    
    # Group by category
    grouped = {}
    for perm in permissions:
        if perm.category not in grouped:
            grouped[perm.category] = []
        grouped[perm.category].append({
            'id': str(perm.id),
            'category': perm.category,
            'action': perm.action,
            'resource': perm.resource,
            'description': perm.description
        })
    
    return Response({
        'status': 'success',
        'data': grouped
    })


class TenantViewSet(viewsets.ModelViewSet):
    """
    Tenant Management
    - Master Admin: Full CRUD access
    - Tenant Owner: Can view and update their own tenant (limited fields)
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'upload_logo':
            return TenantLogoSerializer
        return TenantSerializer
    
    def get_queryset(self):
        """Filter tenants based on user role"""
        user = self.request.user
        
        if user.is_master_admin:
            return Tenant.objects.all()
        elif user.is_tenant_owner and user.tenant:
            return Tenant.objects.filter(id=user.tenant.id)
        return Tenant.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Update tenant - master admin can update user_limit, tenant owners cannot"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # If not master admin, restrict what can be updated
        if not request.user.is_master_admin:
            # Tenant owners can only update certain fields
            restricted_fields = ['user_limit', 'plan', 'is_active']
            for field in restricted_fields:
                if field in request.data:
                    return Response({
                        'status': 'error',
                        'message': f'You do not have permission to update {field}. Only master admin can modify this.'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Tenant updated successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='update-user-limit')
    def update_user_limit(self, request, pk=None):
        """
        Update tenant user limit (Master Admin Only)
        Allows expanding user limit from 1 to 1000 based on tenant plan
        """
        tenant = self.get_object()
        
        # Only master admin can update user limits
        if not request.user.is_master_admin:
            return Response({
                'status': 'error',
                'message': 'Only master admin can update user limits'
            }, status=status.HTTP_403_FORBIDDEN)
        
        new_limit = request.data.get('user_limit')
        plan = request.data.get('plan', tenant.plan)
        
        if new_limit is None:
            return Response({
                'status': 'error',
                'message': 'user_limit is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user limit
        if not isinstance(new_limit, int) or new_limit < 1 or new_limit > 1000:
            return Response({
                'status': 'error',
                'message': 'User limit must be between 1 and 1000'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if new limit is less than current user count
        if new_limit < tenant.current_user_count:
            return Response({
                'status': 'error',
                'message': f'User limit cannot be less than current user count ({tenant.current_user_count})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update tenant
        tenant.user_limit = new_limit
        tenant.plan = plan
        tenant.save()
        
        return Response({
            'status': 'success',
            'message': f'User limit updated to {new_limit} users',
            'data': {
                'id': str(tenant.id),
                'company_name': tenant.company_name,
                'user_limit': tenant.user_limit,
                'current_user_count': tenant.current_user_count,
                'available_slots': tenant.available_slots,
                'plan': tenant.plan
            }
        })
    
    @action(detail=True, methods=['post'], url_path='upload-logo')
    def upload_logo(self, request, pk=None):
        """Upload tenant logo"""
        tenant = self.get_object()
        
        # Check if user can update tenant
        if not request.user.is_master_admin and not (request.user.is_tenant_owner and request.user.tenant == tenant):
            return Response({
                'status': 'error',
                'message': 'You do not have permission to update this tenant'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TenantLogoSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Logo uploaded successfully',
            'data': {
                'logo': tenant.logo.url if tenant.logo else None
            }
        })


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Permission Management
    GET /api/auth/permissions/
    """
    queryset = Permission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_permission(request, user_id, permission_id):
    """
    Toggle permission for a user
    POST /api/auth/members/{user_id}/permissions/{permission_id}/toggle/
    """
    # Check if requester can manage permissions
    if not request.user.can_create_members:
        return Response({
            'status': 'error',
            'message': 'You don\'t have permission to manage permissions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        permission = Permission.objects.get(id=permission_id)
        
        # Check if permission mapping exists
        role_perm, created = RolePermission.objects.get_or_create(
            user=user,
            permission=permission,
            defaults={'granted_by': request.user}
        )
        
        if not created:
            # Toggle the permission
            role_perm.is_enabled = not role_perm.is_enabled
            role_perm.save()
        
        return Response({
            'status': 'success',
            'message': f'Permission {"enabled" if role_perm.is_enabled else "disabled"} successfully',
            'data': RolePermissionSerializer(role_perm).data
        }, status=status.HTTP_200_OK)
        
    except (User.DoesNotExist, Permission.DoesNotExist):
        return Response({
            'status': 'error',
            'message': 'User or Permission not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend verification email
    POST /api/auth/resend-verification/
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'status': 'error',
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        if user.email_verified:
            return Response({
                'status': 'error',
                'message': 'Email already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new token
        user.email_verification_token = secrets.token_urlsafe(32)
        user.email_verification_sent_at = timezone.now()
        user.save()
        
        # Send email
        send_verification_email(user)
        
        return Response({
            'status': 'success',
            'message': 'Verification email sent successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
