from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
import graphene
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
        # All users following this user
        return self.followers.count()

    def resolve_following_count(self, info):
        # All users this user is following
        return self.following.count()


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")


# ------------------------
# Queries
# ------------------------
class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    followers = graphene.List(UserType, user_id=graphene.Int(required=True))
    following = graphene.List(UserType, user_id=graphene.Int(required=True))

    def resolve_me(root, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user

    def resolve_users(root, info):
        return User.objects.all()

    def resolve_followers(root, info, user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return []
        return [f.follower for f in target.followers.all()]

    def resolve_following(root, info, user_id):
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
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

        # Use manager to hash password
        user = User.objects.create_user(username=username, email=email, password=password)

        if bio is not None:
            user.bio = bio
        if role is not None:
            user.role = role
        user.save()

        token = get_token(user)
        return CreateUser(user=user, token=token)


class FollowUser(graphene.Mutation):
    follow = graphene.Field(FollowType)

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Exception("Target user not found")

        if user == target:
            raise Exception("You cannot follow yourself")

        follow, created = Follow.objects.get_or_create(follower=user, following=target)
        return FollowUser(follow=follow)


class UnfollowUser(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, user_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Exception("Target user not found")

        deleted, _ = Follow.objects.filter(follower=user, following=target).delete()
        return UnfollowUser(ok=bool(deleted))


class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
