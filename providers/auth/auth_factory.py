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
This module defines a factory function for retrieving different authentication
strategies.

Currently, it supports the JSON Web Token (JWT) authentication method.
Other authentication methods can be added in the future by extending the
`get_auth_strategy` function.
"""
from providers.auth.auth_strategy import AuthStrategy
from providers.auth.methods.jwt_auth import JWTAuth


def get_auth_strategy(method: str = "jwt") -> AuthStrategy:
    """
    Retrieves an authentication strategy based on the specified method.

    Args:
        method: The name of the authentication method to use (default: "jwt").

    Returns:
        An instance of the corresponding AuthStrategy.

    Raises:
        ValueError: If an unknown authentication method is provided.

    Currently, only the 'jwt' authentication method is supported, which returns
    an instance of JWTAuth initialized with a default secret key.
    """
    match method:
        case "jwt":
            return JWTAuth(secret_key="mysecretkey")

    raise ValueError(f"Unknown auth method: {method}")
