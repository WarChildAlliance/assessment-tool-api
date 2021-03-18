from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create auth token on user creation
    """
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def disable_student_password(sender, instance=None, **kwargs):
    """
    Set student password as unusable on creation
    """
    if instance.is_student():
        instance.set_unusable_password()
