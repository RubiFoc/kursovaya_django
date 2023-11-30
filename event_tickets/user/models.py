from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser, models.Model):
    avatar = models.ImageField(upload_to="user_photos/%Y/%m/%d/",
                               verbose_name="Фото пользователя", blank=True)
    is_organizer = models.BooleanField(default=False, blank=True)

