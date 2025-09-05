from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    department = models.CharField(max_length=100, blank=True, verbose_name="Подразделение")
    email = models.EmailField(blank=True, verbose_name="Почта")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает или обновляет профиль пользователя"""
    if created:
        # Создаем профиль для нового пользователя
        UserProfile.objects.create(user=instance)
    else:
        # Обновляем существующий профиль или создаем, если не существует
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
