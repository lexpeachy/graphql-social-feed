# users/schema.py
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Count
from graphql_jwt.shortcuts import get_token

from .models import Follow

User = get_user_model()


# ------------------------
# GraphQL Types
# ------------------------
class UserType(DjangoObjectType):
    followers_count = graphene.Int()
    following_count = graphene.Int()

    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "role")

    def resolve_followers_count(self, info):
        return getattr(self, "followers_count", self.followers.count())

    def resolve_following_count(self, info):
        return getattr(self, "following_count", self.following.count())


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")


# ------------------------
# Queries
# ------------------------
class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(
        UserType,
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    followers = graphene.List(UserType, user_id=graphene.Int(required=True))
    following = graphene.List(UserType, user_id=graphene.Int(required=True))

    def resolve_me(root, info):
        user = info.context.user
        return None if user.is_anonymous else user

    def resolve_users(root, info, limit=None, offset=None):
        qs = User.objects.annotate(
            followers_count=Count("followers"),
            following_count=Count("following"),
        )
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    def resolve_followers(root, info, user_id):
        target = User.objects.filter(id=user_id).first()
        if not target:
            return []
        return [f.follower for f in target.followers.all()]

    def resolve_following(root, info, user_id):
        target = User.objects.filter(id=user_id).first()
        if not target:
            return []
        return [f.following for f in target.following.all()]


# ------------------------
# Mutations
# ------------------------
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        bio = graphene.String(required=False)
        role = graphene.String(required=False)

    def mutate(self, info, username, email, password, bio=None, role=None):
        if User.objects.filter(username=username).exists():
            raise Exception("Username already taken")
        if User.objects.filter(email=email).exists():
            raise Exception("Email already in use")

        # Normalize + validate password
        email = User.objects.normalize_email(email)
        validate_password(password)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if bio:
            user.bio = bio
        if role:
            user.role = role
        user.save()

        token = get_token(user)
        return CreateUser(user=user, token=token)


class FollowUser(graphene.Mutation):
    follow = graphene.Field(FollowType)
    created = graphene.Boolean()

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        target = User.objects.filter(id=user_id).first()
        if not target:
            raise Exception("Target user not found")
        if user == target:
            raise Exception("You cannot follow yourself")

        follow, created = Follow.objects.get_or_create(follower=user, following=target)
        return FollowUser(follow=follow, created=created)


class UnfollowUser(graphene.Mutation):
    ok = graphene.Boolean()
    target_user_id = graphene.Int()

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        target = User.objects.filter(id=user_id).first()
        if not target:
            raise Exception("Target user not found")

        deleted, _ = Follow.objects.filter(follower=user, following=target).delete()
        return UnfollowUser(ok=bool(deleted), target_user_id=target.id)


class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
