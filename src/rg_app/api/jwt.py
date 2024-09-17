import typing as ty
from datetime import timedelta

from litestar.config.app import AppConfig
from litestar.connection import ASGIConnection
from litestar.datastructures import State
from litestar.di import Provide
from litestar.plugins import InitPluginProtocol
from litestar.security.jwt import JWTAuth, Token

from rg_app.common.msg import BaseStruct


class MinimalUser(BaseStruct):
    id: int


_STATE_KEY = "jwt_plugin_stuff"


async def _retrieve_user_handler(
    token: Token, connection: "ASGIConnection[ty.Any, ty.Any, ty.Any, ty.Any]"
) -> ty.Optional[MinimalUser]:
    return MinimalUser(id=int(token.sub))


# Ugly hack, somehow JWTAuth cannot be used as a dependency
class CreateTokenHandler:
    def __init__(self, jwt: JWTAuth[MinimalUser]) -> None:
        self._ch = jwt.create_token

    def create_token(
        self,
        identifier: str,
        token_expiration: timedelta | None = None,
        token_issuer: str | None = None,
        token_audience: str | None = None,
        token_unique_jwt_id: str | None = None,
        token_extras: dict | None = None,
        **kwargs: ty.Any,
    ) -> str:
        return self._ch(
            identifier, token_expiration, token_issuer, token_audience, token_unique_jwt_id, token_extras, **kwargs
        )


class SimpleJwtPlugin(InitPluginProtocol):
    def __init__(self, secret: str, exclude: list[str]) -> None:
        self.jwt_auth = JWTAuth[MinimalUser](
            retrieve_user_handler=_retrieve_user_handler,
            token_secret=secret,
            exclude=exclude,
        )

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        def get_jwt(state: State) -> CreateTokenHandler:
            return state[_STATE_KEY]

        app_config.state[_STATE_KEY] = CreateTokenHandler(self.jwt_auth)
        app_config.dependencies["jwt"] = Provide(get_jwt, sync_to_thread=False)
        app_config = self.jwt_auth.on_app_init(app_config)
        return app_config