from django.contrib import admin
from .models import Post, Comment, Like, Share


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("user", "text", "created_at")
    can_delete = False


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


class ShareInline(admin.TabularInline):
    model = Share
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_content", "created_at",
                    "likes_count", "comments_count", "shares_count")
    list_filter = ("created_at", "author")
    search_fields = ("content", "author__username")
    inlines = [CommentInline, LikeInline, ShareInline]
    date_hierarchy = "created_at"

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Content"

    def likes_count(self, obj):
        return obj.likes.count()
    def comments_count(self, obj):
        return obj.comments.count()
    def shares_count(self, obj):
        return obj.shares.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "short_text", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("text", "user__username", "post__content")
    date_hierarchy = "created_at"

    def short_text(self, obj):
        return obj.text[:40] + ("..." if len(obj.text) > 40 else "")
    short_text.short_description = "Text"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "post__content")
    date_hierarchy = "created_at"


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "post__content")
    date_hierarchy = "created_at"
