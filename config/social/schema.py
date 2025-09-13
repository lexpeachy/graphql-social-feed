import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, Share
from users.models import Follow
from django.db.models import Prefetch
from django.core.cache import cache

User = get_user_model()

# GraphQL Types
class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    shares_count = graphene.Int()
    popularity_score = graphene.Int()

    class Meta:
        model = Post
        fields = ("id", "content", "author", "created_at")

    def resolve_likes_count(self, info):
        return self.likes.count()

    def resolve_comments_count(self, info):
        return self.comments.count()

    def resolve_shares_count(self, info):
        return self.shares.count()

    def resolve_popularity_score(self, info):
        return self.popularity_score  # uses property in model

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


# Queries
class SocialQuery(graphene.ObjectType):
    posts = graphene.List(PostType, limit=graphene.Int(), order_by=graphene.String())
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    personalized_feed = graphene.List(PostType, limit=graphene.Int())
    trending_feed = graphene.List(PostType, limit=graphene.Int())

    def resolve_posts(root, info, limit=None, order_by="-created_at"):
        qs = (
            Post.objects.all()
            .select_related("author")  # optimize author fetch
            .prefetch_related(
                Prefetch("comments", queryset=Comment.objects.select_related("user")),
                Prefetch("likes", queryset=Like.objects.select_related("user")),
                Prefetch("shares", queryset=Share.objects.select_related("user")),
            )
            .order_by(order_by)
        )
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_post(root, info, id):
        return (
            Post.objects.filter(id=id)
            .select_related("author")
            .prefetch_related("comments", "likes", "shares")
            .first()
        )

    def resolve_personalized_feed(root, info, limit=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        following_ids = user.following.values_list("following_id", flat=True)
        qs = (
            Post.objects.filter(author__id__in=following_ids)
            .select_related("author")
            .prefetch_related("comments", "likes", "shares")
            .order_by("-created_at")
        )
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_trending_feed(root, info, limit=None):
        cache_key = f"trending_feed_{limit}"
        posts = cache.get(cache_key)
        if not posts:
            qs = (
                Post.objects.all()
                .select_related("author")
                .prefetch_related("comments", "likes", "shares")
            )
            posts = sorted(qs, key=lambda post: post.popularity_score, reverse=True)
            if limit:
                posts = posts[:limit]
            cache.set(cache_key, posts, timeout=60)  # cache for 1 minute
        return posts

# Mutations
class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        content = graphene.String(required=True)

    def mutate(self, info, content):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        post = Post.objects.create(author=user, content=content)
        return CreatePost(post=post)


class CreateComment(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        post_id = graphene.Int(required=True)
        text = graphene.String(required=True)

    def mutate(self, info, post_id, text):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(post=post, user=user, text=text)
        return CreateComment(comment=comment)


class LikePost(graphene.Mutation):
    like = graphene.Field(LikeType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(post=post, user=user)
        return LikePost(like=like)


class SharePost(graphene.Mutation):
    share = graphene.Field(ShareType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        post = Post.objects.get(id=post_id)
        share = Share.objects.create(post=post, user=user)
        return SharePost(share=share)


class SocialMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    create_comment = CreateComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()