from django.db import models
from django.conf import settings
from django.utils import timezone

# Reference to the custom User model (AUTH_USER_MODEL from settings)
User = settings.AUTH_USER_MODEL


# Post Model
class Post(models.Model):
    # Author of the post (linked to User model)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    # Content of the post
    content = models.TextField()
    # Timestamp when the post was created
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        # Add DB indexes for faster queries
        indexes = [
            models.Index(fields=["-created_at"]),          # recent posts
            models.Index(fields=["author", "created_at"]), # posts by author
        ]
        ordering = ["-created_at"]   # default ordering: newest first
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return f"Post by {self.author} at {self.created_at:%Y-%m-%d %H:%M}"

    # Computed properties (convenience + annotated compatibility)
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
        # Weighted formula for engagement: likes=1, comments=2, shares=3
        return (self.likes_count * 1) + (self.comments_count * 2) + (self.shares_count * 3)


# Comment Model
class Comment(models.Model):
    # Link to the post being commented on
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    # The user who wrote the comment
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    # Text content of the comment
    text = models.TextField()
    # Timestamp of when comment was created
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        # Add DB indexes for queries like "recent comments" or "user comments"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user} on Post {self.post_id}"


# Like Model
class Like(models.Model):
    # Post being liked
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    # User who liked the post
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    # Timestamp of when like was added
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        # A user can only like a post once
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like")
        ]
        # Index for sorting/filtering likes quickly
        indexes = [models.Index(fields=["-created_at"])]
        ordering = ["-created_at"]
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def __str__(self):
        return f"{self.user} likes Post {self.post_id}"


# Share Model
class Share(models.Model):
    # Post being shared
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shares")
    # User who shared the post
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shares")
    # Timestamp of when share happened
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        # A user can only share a post once
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_share")
        ]
        # Index for fast queries (e.g., trending posts by shares)
        indexes = [models.Index(fields=["-created_at"])]
        ordering = ["-created_at"]
        verbose_name = "Share"
        verbose_name_plural = "Shares"

    def __str__(self):
        return f"{self.user} shared Post {self.post_id}"
