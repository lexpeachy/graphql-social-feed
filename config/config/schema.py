import graphene
import graphql_jwt

from users.schema import UserQuery, UserMutation, CustomObtainJSONWebToken
from social.schema import SocialQuery, SocialMutation


class UtilityQuery(graphene.ObjectType):
    """Utility queries for system checks."""
    health_check = graphene.String(description="Returns 'ok' if API is running.")

    def resolve_health_check(root, info):
        return "ok"


class Query(UserQuery, SocialQuery, UtilityQuery, graphene.ObjectType):
    """
    Root Query for the project.
    Combines User, Social, and Utility queries.
    """
    pass


class Mutation(UserMutation, SocialMutation, graphene.ObjectType):
    """
    Root Mutation for the project.
    Includes user/social mutations + JWT authentication mutations.
    """
    # JWT authentication
    token_auth = CustomObtainJSONWebToken.Field(
        description="Authenticate user and return both JWT and refresh token."
    )
    verify_token = graphql_jwt.Verify.Field(
        description="Verify if a token is valid."
    )
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    auto_camelcase=True,  # set False if you prefer snake_case in GraphQL
)
