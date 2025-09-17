from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


class FollowingInline(admin.TabularInline):
    model = Follow
    fk_name = "follower"
    extra = 0
    verbose_name = "Following"
    verbose_name_plural = "Following"
    readonly_fields = ("following", "created_at")
    can_delete = True


class FollowerInline(admin.TabularInline):
    model = Follow
    fk_name = "following"
    extra = 0
    verbose_name = "Follower"
    verbose_name_plural = "Followers"
    readonly_fields = ("follower", "created_at")
    can_delete = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile Info", {"fields": ("bio", "role")}),
    )
    list_display = (
        "id", "username", "email", "role", "is_staff", "is_active",
        "followers_count", "following_count"
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)
    inlines = [FollowingInline, FollowerInline]

    def followers_count(self, obj):
        return obj.followers.count()
    followers_count.short_description = "Followers"

    def following_count(self, obj):
        return obj.following.count()
    following_count.short_description = "Following"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
