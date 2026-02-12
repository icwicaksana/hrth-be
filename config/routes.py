# import os
# import importlib
from config.setting import env
from routes.api import v1 as api_v1

def setup_routes(app):
    root = [
        # Security(CorsMiddleware())
    ]
    app.include_router(
        api_v1.router,
        prefix="/api/v1",
        tags=["api_v1"],
        dependencies = root
    )

    @app.get("/health-check")
    async def read_health():
        return {"status": "OK"}
        
    @app.get("/")
    async def read_root():
        return {
            "app_env": env.APP_ENV,
            "app_name": env.APP_NAME,
            "app_version": env.APP_VERSION,
        }