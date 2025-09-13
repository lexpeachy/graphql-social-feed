import graphene
import graphql_jwt
from users.schema import UserQuery, UserMutation
from social.schema import SocialQuery, SocialMutation

class Query(UserQuery, SocialQuery, graphene.ObjectType):
    pass

class Mutation(UserMutation, SocialMutation, graphene.ObjectType):
    # JWT auth
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
