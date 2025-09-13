from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("moderator", "Moderator"),
            ("admin", "Admin"),
        ],
        default="user",
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")  # no duplicates

    def __str__(self):
        return f"{self.follower} follows {self.following}"
