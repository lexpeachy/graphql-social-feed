import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Count
from graphql import GraphQLError
from graphql_jwt.shortcuts import get_token, create_refresh_token
from graphql_jwt.mixins import ObtainJSONWebTokenMixin

from .models import Follow

User = get_user_model()


# GraphQL Types
class UserType(DjangoObjectType):
    # Extra fields for counts
    followers_count = graphene.Int()
    following_count = graphene.Int()

    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "role")

    # Resolve annotated or fallback followers count
    def resolve_followers_count(self, info):
        return getattr(self, "followers_count", self.followers.count())

    # Resolve annotated or fallback following count
    def resolve_following_count(self, info):
        return getattr(self, "following_count", self.following.count())


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")


# Queries
class UserQuery(graphene.ObjectType):
    # Expose user-related queries
    me = graphene.Field(UserType)
    users = graphene.List(UserType, limit=graphene.Int(), offset=graphene.Int())
    followers = graphene.List(UserType, user_id=graphene.Int(required=True))
    following = graphene.List(UserType, user_id=graphene.Int(required=True))

    # Current authenticated user
    def resolve_me(root, info):
        user = info.context.user
        return None if user.is_anonymous else user

    # List of users with optional pagination
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

    # Get followers of a specific user
    def resolve_followers(root, info, user_id):
        target = User.objects.filter(id=user_id).first()
        if not target:
            return []
        return (
            User.objects.filter(following__following=target)
            .annotate(following_count=Count("following"))
        )

    # Get users that a specific user is following
    def resolve_following(root, info, user_id):
        target = User.objects.filter(id=user_id).first()
        if not target:
            return []
        return (
            User.objects.filter(followers__follower=target)
            .annotate(followers_count=Count("followers"))
        )


# Mutations
class CreateUser(graphene.Mutation):
    # Return user and tokens after signup
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        bio = graphene.String(required=False)
        role = graphene.String(required=False)

    # Handle user signup
    def mutate(self, info, username, email, password, bio=None, role=None):
        username = username.lower().strip()
        email = User.objects.normalize_email(email)

        # Prevent duplicates
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already taken")
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already in use")

        # Validate password strength
        validate_password(password)

        # Create user account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # Optional fields
        if bio:
            user.bio = bio
        if role and role.lower() in ["user"]:  # restrict roles
            user.role = role
        user.save()

        # Generate tokens
        token = get_token(user)
        refresh = create_refresh_token(user)

        return CreateUser(user=user, token=token, refresh_token=refresh)


class FollowUser(graphene.Mutation):
    follow = graphene.Field(FollowType)
    created = graphene.Boolean()

    class Arguments:
        user_id = graphene.Int(required=True)

    # Follow another user
    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        target = User.objects.filter(id=user_id).first()
        if not target:
            raise GraphQLError("Target user not found")
        if user == target:
            raise GraphQLError("You cannot follow yourself")

        follow, created = Follow.objects.get_or_create(follower=user, following=target)
        return FollowUser(follow=follow, created=created)


class UnfollowUser(graphene.Mutation):
    ok = graphene.Boolean()
    target_user_id = graphene.Int()

    class Arguments:
        user_id = graphene.Int(required=True)

    # Unfollow another user
    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        target = User.objects.filter(id=user_id).first()
        if not target:
            raise GraphQLError("Target user not found")

        # Delete the follow relationship
        deleted, _ = Follow.objects.filter(
            follower=user, following=target
        ).delete()

        return UnfollowUser(ok=bool(deleted), target_user_id=target.id)


class CustomObtainJSONWebToken(graphene.Mutation):
    """
    Custom login mutation that returns both access and refresh tokens.
    """
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    # Handle user login
    @classmethod
    def mutate(cls, root, info, username, password):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("Invalid username or password")

        if not user.check_password(password):
            raise Exception("Invalid username or password")

        token = get_token(user)
        refresh = create_refresh_token(user)

        return cls(user=user, token=token, refresh_token=refresh)

# Root Mutations
class UserMutation(graphene.ObjectType):
    signup = CreateUser.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
    login = CustomObtainJSONWebToken.Field()
