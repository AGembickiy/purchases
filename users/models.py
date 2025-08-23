from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    email = models.EmailField(blank=True, verbose_name="Почта")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Автоматически сохраняет профиль при обновлении пользователя"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Если профиль не существует, создаем его
        UserProfile.objects.create(user=instance)
