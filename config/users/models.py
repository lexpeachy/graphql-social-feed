from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User Model
class User(AbstractUser):
    # Extra field for user biography / description
    bio = models.TextField(blank=True, null=True)

    # Role field with predefined choices (role-based access or permissions)
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),           # Regular user
            ("moderator", "Moderator"), # Can manage/report content
            ("admin", "Admin"),         # Full privileges
        ],
        default="user",  # Default role when new user is created
    )

    def __str__(self):
        # Return the username when object is printed
        return self.username


# Follow Relationship Model
class Follow(models.Model):
    # The user who follows another user
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    # The user being followed
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    # Timestamp for when the follow happened
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate follows (a user can't follow the same person twice)
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow")
        ]
        # Indexes for faster queries, like "who follows who?"
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        # Human-readable representation of a follow relationship
        return f"{self.follower} follows {self.following}"
