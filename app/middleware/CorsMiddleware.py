
from typing import Annotated
from config.setting import env
from fastapi import Header, HTTPException, status
from typing_extensions import Annotated

class CorsMiddleware:
    async def __call__(self, origin: Annotated[str, Header()] = None):
        try:
            if origin not in env.ALLOWED_ORIGINS.split(","):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail= {
                        "msg": "Not allowed by cors",
                        "data": None,
                        "error": None
                    }
                )
            return True
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail= {
                        "msg": "Not allowed by cors",
                        "data": None,
                        "error": e
                    },
                    headers={"Authorization": "Bearer"},
                )

