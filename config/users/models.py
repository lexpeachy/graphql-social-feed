from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    role =models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
            ('user', 'User'),
        ],
        default='user',
    )
    def __str__(self):
        return self.username