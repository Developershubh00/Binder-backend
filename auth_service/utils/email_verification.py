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
