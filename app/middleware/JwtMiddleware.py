from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Annotated
from config.setting import env
# import base64  <-- Hapus ini (tidak diperlukan lagi)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class CredentialError(Exception):
    pass

class JwtMiddleware:
    def __init__(self, algo: str = "HS256", key: str = "JWT_HS_SECRET"):
        self.algorithms = algo
        self.key_string = key
        key_val = getattr(env, self.key_string.upper(), None)
        if not key_val:
            raise AttributeError(f"Invalid JWT key empty or not found in env: {self.key_string}")
        self.key = key_val 
        
    async def __call__(
        self, 
        token: Annotated[str, Depends(oauth2_scheme)],
        ):
        try:
            # Decode token (signature & expiry check is automatic)
            # Kita tambahkan options={"verify_aud": False} untuk mematikan cek audience
            # agar tidak ribet dengan format string vs list.
            payload = jwt.decode(
                token, 
                self.key, 
                algorithms=[self.algorithms],
                options={"verify_aud": False} 
            )
            
            # Cek Expiry manual (jika library tidak otomatis raise error)
            if payload.get("exp") is None:
                raise CredentialError("Token has no expiration")

            return payload
        
        except (JWTError, CredentialError) as e:
            print(f"JWT Verification Failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"msg": "Could not validate credentials. Invalid token."},
                headers={"Authorization": "Bearer"},
            )