from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author} at {self.created_at}"

    # Counts via annotation preferred, but fallback is here
    @property
    def likes_count(self):
        return getattr(self, "likes_count", self.likes.count())

    @property
    def comments_count(self):
        return getattr(self, "comments_count", self.comments.count())

    @property
    def shares_count(self):
        return getattr(self, "shares_count", self.shares.count())

    @property
    def popularity_score(self):
        # This is used if not annotated in queryset
        return (self.likes_count * 1) + (self.comments_count * 2) + (self.shares_count * 3)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user} on Post {self.post_id}"


class Like(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like")
        ]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} likes Post {self.post_id}"


class Share(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="shares"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shares"
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_share")
        ]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} shared Post {self.post_id}"
