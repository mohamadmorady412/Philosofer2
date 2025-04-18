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
This module defines an abstract base class for authentication strategies.

Subclasses of AuthStrategy are responsible for implementing specific
authentication mechanisms, such as JWT, API keys, or session-based authentication.
The `authenticate` method is the core of each strategy, responsible for
verifying the incoming request and determining if it is authenticated.
"""
from fastapi import Request


class AuthStrategy:
    """
    An abstract base class defining the interface for authentication strategies.

    Subclasses must implement the `authenticate` method to provide a specific
    authentication mechanism.
    """

    async def authenticate(self, request: Request) -> bool:
        """
        Authenticates the incoming request.

        This method must be implemented by subclasses to define the specific
        authentication logic.

        Args:
            request: The FastAPI Request object.

        Returns:
            True if the request is authenticated, False otherwise.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            "AuthStrategy subclasses must implement authenticate."
        )
