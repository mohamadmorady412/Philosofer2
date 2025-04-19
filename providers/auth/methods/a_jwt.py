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

"""
This file implements a JWT-based authentication strategy for FastAPI applications.
The JWTAuth class handles extracting the token from the Authorization header
and verifying its authenticity. Upon successful verification, the token's
payload is stored in the request state.
"""

import jwt
from fastapi import HTTPException, Request, status
from jwt.exceptions import DecodeError, ExpiredSignatureError

from ..strategy.auth_strategy import AuthStrategy


class JWTAuth(AuthStrategy):
    """
    An authentication strategy for verifying requests based on JSON Web Tokens (JWT).

    Attributes:
        secret_key (str): The secret key used to sign the JWT.
        algorithm (str): The algorithm used to sign the JWT (default: "HS256").
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initializes the JWTAuth strategy.

        Args:
            secret_key (str): The secret key used to sign the JWT.
            algorithm (str): The algorithm used to sign the JWT (default: "HS256").
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def authenticate(self, request: Request) -> bool:
        """
        Authenticates the request based on the JWT found in the Authorization header.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            bool: True if the token is valid, False otherwise.

        Raises:
            HTTPException (401): If the token has expired, is invalid, or the
                                 Authorization header is improperly formatted.
            HTTPException (500): If an unexpected error occurs during token verification.
        """
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            return False

        try:
            scheme, token = authorization_header.split()
            if scheme.lower() != "bearer":
                return False
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not token:
            return False

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user_payload = payload  # Store payload in request state
            return True
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(f"JWT Verification Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during token verification",
                headers={"WWW-Authenticate": "Bearer"},
            )


"""
Example usage of the JWTAuth strategy with a FastAPI application.

This demonstrates how to integrate JWTAuth as a dependency for route protection
and how to access the decoded payload within a route.

To run this example:
1. Install necessary libraries: pip install fastapi uvicorn python-jwt
2. Save this code as a Python file (e.g., main.py).
3. Run the application using Uvicorn: uvicorn main:app --reload

You can then test the protected route by sending a GET request to /protected
with a valid Bearer token in the Authorization header.

>>> app = FastAPI()
>>> SECRET_KEY = "your-secret-key"  # Replace with a strong, secret key
>>> jwt_auth = JWTAuth(secret_key=SECRET_KEY)

Helper function to create a sample JWT for testing:
>>> def create_jwt(payload: dict):
>>>     return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

A public route accessible without authentication:
>>> @app.get("/public")
>>> async def public_route():
>>>     return {"message": "This is a public endpoint."}

A protected route that requires a valid JWT for access.
The decoded JWT payload is available in request.state.user_payload:
>>> @app.get("/protected", dependencies=[Depends(jwt_auth.authenticate)])
>>> async def protected_route(request: Request):
>>>     user_info = request.state.user_payload
>>>     return {"message": "Access granted to protected endpoint.", "user": user_info}

Example of creating a token (for testing purposes):
>>> example_payload = {"sub": "testuser", "exp": 1745080000}  # Example payload with expiration
>>> example_token = create_jwt(example_payload)
>>> print(f"\nExample JWT (for testing): Bearer {example_token}\n")

>>> print("Try accessing /protected with the above token in the Authorization header.")

>>> print("For example, using curl: curl -H 'Authorization: Bearer <your_token>' http://127.0.0.1:8000/protected")
"""
