from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
import datetime

security = HTTPBearer()

class AuthGuard:
    async def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
        if not credentials:
            raise HTTPException(status_code=401, detail="No token provided")

        token = credentials.credentials
        try:
            decoded_token = auth.verify_id_token(token)
            user = auth.get_user(decoded_token["uid"])
            tokens_valid_after_time = user.tokens_valid_after_timestamp

            if tokens_valid_after_time:
                token_revoke_time = datetime.datetime.fromtimestamp(tokens_valid_after_time / 1000.0)
                auth_time = datetime.datetime.fromtimestamp(decoded_token["auth_time"])
                if auth_time < token_revoke_time:
                    raise HTTPException(status_code=401, detail="Token has been revoked")

            user_claims = user.custom_claims or {}
            role = user_claims.get("role", "user")

            request.state.user = {"uid": decoded_token["uid"], "role": role}
            return request.state.user

        except auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid ID token")
        except auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except auth.RevokedIdTokenError:
            raise HTTPException(status_code=401, detail="Token has been revoked")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

auth_guard = AuthGuard()
