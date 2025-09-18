# social/schema.py
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.db.models import Count, F
from django.core.cache import cache
from graphql import GraphQLError

from .models import Post, Comment, Like, Share

User = get_user_model()


# ------------------------
# QuerySet Helpers
# ------------------------
class PostQuerySet:
    """Reusable queryset helpers for Posts."""

    @staticmethod
    def with_counts():
        return Post.objects.annotate(
            likes_count=Count("likes"),
            comments_count=Count("comments"),
            shares_count=Count("shares"),
        ).select_related("author")

    @staticmethod
    def with_popularity():
        return PostQuerySet.with_counts().annotate(
            popularity_score=(
                Count("likes") * 1
                + Count("comments") * 2
                + Count("shares") * 3
            )
        )


# ------------------------
# GraphQL Types
# ------------------------
class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    shares_count = graphene.Int()
    popularity_score = graphene.Int()

    class Meta:
        model = Post
        fields = ("id", "content", "author", "created_at")

    def resolve_likes_count(self, info):
        return getattr(self, "likes_count", 0)

    def resolve_comments_count(self, info):
        return getattr(self, "comments_count", 0)

    def resolve_shares_count(self, info):
        return getattr(self, "shares_count", 0)

    def resolve_popularity_score(self, info):
        return getattr(self, "popularity_score", 0)


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "text", "user", "post", "created_at")


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")


class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = ("id", "user", "post", "created_at")


# ------------------------
# Queries
# ------------------------
class SocialQuery(graphene.ObjectType):
    posts = graphene.List(
        PostType,
        limit=graphene.Int(),
        offset=graphene.Int(),
        order_by=graphene.String(),
    )
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    personalized_feed = graphene.List(PostType, limit=graphene.Int(), offset=graphene.Int())
    trending_feed = graphene.List(PostType, limit=graphene.Int())

    def resolve_posts(root, info, limit=None, offset=None, order_by="-created_at"):
        qs = PostQuerySet.with_popularity().order_by(order_by)
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_post(root, info, id):
        return PostQuerySet.with_popularity().filter(id=id).first()

    def resolve_personalized_feed(root, info, limit=None, offset=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        following_ids = user.following.values_list("following_id", flat=True)
        qs = PostQuerySet.with_counts().filter(author__id__in=following_ids).order_by("-created_at")
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_trending_feed(root, info, limit=None):
        cache_key = f"trending_feed_{limit}"
        posts = cache.get(cache_key)
        if not posts:
            qs = PostQuerySet.with_popularity().order_by("-popularity_score")
            if limit:
                qs = qs[:limit]
            posts = list(qs)
            cache.set(cache_key, posts, timeout=60)
        return posts


# ------------------------
# Mutations
# ------------------------
class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        content = graphene.String(required=True)

    def mutate(self, info, content):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        post = Post.objects.create(author=user, content=content)
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, post_id, content):
        user = info.context.user
        post = Post.objects.filter(id=post_id, author=user).first()
        if not post:
            raise GraphQLError("Post not found or not authorized")
        post.content = content
        post.save()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        deleted, _ = Post.objects.filter(id=post_id, author=user).delete()
        if not deleted:
            raise GraphQLError("Post not found or not authorized")
        return DeletePost(ok=True)


class CreateComment(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        post_id = graphene.Int(required=True)
        text = graphene.String(required=True)

    def mutate(self, info, post_id, text):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise GraphQLError("Post not found")
        comment = Comment.objects.create(post=post, user=user, text=text)
        return CreateComment(comment=comment)


class DeleteComment(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        comment_id = graphene.Int(required=True)

    def mutate(self, info, comment_id):
        user = info.context.user
        deleted, _ = Comment.objects.filter(id=comment_id, user=user).delete()
        if not deleted:
            raise GraphQLError("Comment not found or not authorized")
        return DeleteComment(ok=True)


class LikePost(graphene.Mutation):
    like = graphene.Field(LikeType)
    created = graphene.Boolean()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise GraphQLError("Post not found")
        like, created = Like.objects.get_or_create(post=post, user=user)
        return LikePost(like=like, created=created)


class SharePost(graphene.Mutation):
    share = graphene.Field(ShareType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise GraphQLError("Post not found")
        share = Share.objects.create(post=post, user=user)
        return SharePost(share=share)


class SocialMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()
