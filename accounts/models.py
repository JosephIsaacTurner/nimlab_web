# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_cleared = models.BooleanField(default=False, help_text="Designates whether this user has been cleared by the admin.", verbose_name="Cleared")

    def __str__(self):
        return self.email
