from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.plugins.problem_details import ProblemDetailsConfig, ProblemDetailsPlugin
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin

from .auth import authenticate_handler
from .config import Config
from .hc import hc_handler
from .jwt import SimpleJwtPlugin
from rg_app.common.litestar.plugins import ConfigPlugin


def app_factory(config: Config, debug_mode: bool = False) -> Litestar:
    sa_config = SQLAlchemyAsyncConfig(connection_string=config.db_url)
    sa_plugin = SQLAlchemyInitPlugin(config=sa_config)
    problem_details_plugin = ProblemDetailsPlugin(ProblemDetailsConfig())
    config_plugin = ConfigPlugin(config)

    jwt_plugin = SimpleJwtPlugin(secret=config.jwt_secret, exclude=["/authenticate", "/docs", "/hc"])
    
    app = Litestar(
        debug=debug_mode,
        route_handlers=[authenticate_handler, hc_handler],
        openapi_config=OpenAPIConfig(
            title="Rowerowe Gminy API",
            version="0.0.1",
            render_plugins=[SwaggerRenderPlugin()],
            path="/docs",
        ),
        plugins=[problem_details_plugin, config_plugin, sa_plugin, jwt_plugin],
    )
    return app
