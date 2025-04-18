# Copyright 2025 Mohammadjavad Morady

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jwt
from fastapi import HTTPException, Request
from jwt.exceptions import DecodeError, ExpiredSignatureError

from providers.auth.auth_strategy import AuthStrategy


class JWTAuth(AuthStrategy):
    """
    Implements authentication using JSON Web Tokens (JWT).

    This class provides a method to authenticate incoming requests by verifying
    the JWT present in the 'Authorization' header. It adheres to the Bearer
    token scheme.
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initializes the JWTAuth strategy.

        Args:
            secret_key: The secret key used to sign and verify JWTs.
            algorithm: The algorithm used for JWT encoding and decoding
                       (default: "HS256").
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def authenticate(self, request: Request) -> bool:
        """
        Authenticates the request by verifying the JWT in the 'Authorization' header.

        Args:
            request: The FastAPI Request object.

        Returns:
            True if the authentication is successful, False otherwise.

        Raises:
            HTTPException (401):
                - If the 'Authorization' header is missing.
                - If the 'Authorization' header format is invalid.
                - If the token has expired.
                - If the token is invalid.
            HTTPException (500): If there is an unexpected error during token verification.

        On successful authentication, the decoded JWT payload is stored in
        `request.state.user_payload`.
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            return False

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return False
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid auth header format")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user_payload = payload
            return True
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=500, detail="Token verification error")
