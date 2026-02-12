
from starlette.middleware.cors import CORSMiddleware
from .setting import env
origins = env.ALLOWED_ORIGINS.split(",")

def setup_middleware(app):
    # pass
    app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins, 
        allow_credentials=True, 
        allow_headers=["*"],
        allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
        max_age=600,
    )
