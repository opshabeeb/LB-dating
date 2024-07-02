from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            return  # Skip creating OTP for superuser
        
        # Create OTP token
        otp = OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
        instance.is_active = False
        instance.save()
        
        # Check if OTP was successfully created
        if otp:
            # Email credentials
            subject = "Email Verification"
            message = f"""
                Hi {instance.username}, here is your OTP {otp.otp_code} 
                it expires in 5 minutes, use the URL below to redirect back to the website:
                http://127.0.0.1:8000/verify-email/{instance.username}
                """
            sender_email = "mohammedshabeeb0000@gmail.com"
            receiver_email = [instance.email, ]
            
            # Send email
            send_mail(
                subject,
                message,
                sender_email,
                receiver_email,
                fail_silently=False,
            )
        else:
            # Handle case where OTP creation failed
            print(f"Error: OTP creation failed for {instance.username}")

