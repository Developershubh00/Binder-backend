"""
OTP-based authentication views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import secrets

from .models import User
from .serializers import LoginSerializer
from .views import get_tokens_for_user, get_client_ip, LoginHistory


def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(user, otp):
    """Send OTP via email"""
    subject = 'Binder Login OTP'
    
    message = f"""
    Hi {user.get_full_name()},
    
    Your OTP for Binder login is: {otp}
    
    This OTP will expire in 10 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Binder Team
    """
    
    if settings.DEBUG:
        print(f"\n{'='*60}")
        print(f"OTP EMAIL")
        print(f"To: {user.email}")
        print(f"OTP: {otp}")
        print(f"Expires: 10 minutes")
        print(f"{'='*60}\n")
    
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
        print(f"Error sending OTP email: {e}")
        return False


@api_view(['POST'])
@permission_classes([AllowAny])
def login_request_otp(request):
    """
    Step 1: Validate credentials and send OTP
    POST /api/auth/login/request-otp/
    Body: { "email": "user@example.com", "password": "password" }
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    
    # Generate and save OTP
    otp = generate_otp()
    user.email_otp = otp
    user.email_otp_created_at = timezone.now()
    user.email_otp_verified = False
    user.save()
    
    # Send OTP email
    send_otp_email(user, otp)
    
    return Response({
        'status': 'success',
        'message': 'OTP sent to your email',
        'data': {
            'email': user.email,
            'otp_expires_in': 600  # 10 minutes in seconds
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_verify_otp(request):
    """
    Step 2: Verify OTP and complete login
    POST /api/auth/login/verify-otp/
    Body: { "email": "user@example.com", "otp": "123456" }
    """
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    if not email or not otp:
        return Response({
            'status': 'error',
            'message': 'Email and OTP are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email, email_verified=True, is_active=True)
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if OTP exists
    if not user.email_otp:
        return Response({
            'status': 'error',
            'message': 'No OTP found. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check OTP expiry (10 minutes)
    if user.email_otp_created_at:
        time_diff = timezone.now() - user.email_otp_created_at
        if time_diff.total_seconds() > 600:  # 10 minutes
            return Response({
                'status': 'error',
                'message': 'OTP expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify OTP
    if user.email_otp != otp:
        return Response({
            'status': 'error',
            'message': 'Invalid OTP'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # OTP verified - clear OTP and mark as verified
    user.email_otp = None
    user.email_otp_created_at = None
    user.email_otp_verified = True
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
    from .serializers import UserDetailSerializer
    user_data = UserDetailSerializer(user).data
    
    return Response({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'user': user_data,
            'tokens': tokens
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_password(request):
    """
    Set new password (for first-time users)
    POST /api/auth/set-password/
    Body: { "token": "reset_token", "password": "newpass", "password_confirm": "newpass" }
    """
    token = request.data.get('token')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    
    if not all([token, password, password_confirm]):
        return Response({
            'status': 'error',
            'message': 'All fields are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if password != password_confirm:
        return Response({
            'status': 'error',
            'message': 'Passwords do not match'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(password_reset_token=token)
        
        # Check token expiry (24 hours)
        if user.password_reset_sent_at:
            time_diff = timezone.now() - user.password_reset_sent_at
            if time_diff.total_seconds() > 86400:  # 24 hours
                return Response({
                    'status': 'error',
                    'message': 'Link expired'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(password)
        user.password_reset_token = None
        user.password_reset_sent_at = None
        user.email_verified = True  # Auto-verify on password set
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'Password set successfully. You can now login.'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Invalid or expired link'
        }, status=status.HTTP_400_BAD_REQUEST)