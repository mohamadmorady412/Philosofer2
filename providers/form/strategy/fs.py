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
This module defines a set of strategies for extracting data from FastAPI request objects.
The strategy pattern allows interchangeable data sources such as form data or JSON payloads.
"""

from abc import ABC, abstractmethod

from fastapi import Request


class DataStrategy(ABC):
    """
    Abstract base class that defines the interface for data extraction strategies.

    Subclasses must implement the `extract` method to define how data is extracted
    from a FastAPI request.
    """

    @abstractmethod
    async def extract(self, request: Request) -> dict:
        """
        Extracts data from a FastAPI request object.

        Args:
            request (Request): The incoming FastAPI request.

        Returns:
            dict: Extracted data from the request.
        """
        pass


class FormDataStrategy(DataStrategy):
    """
    Extracts data from a FastAPI request's form data.

    Typically used when handling form submissions (e.g., from HTML forms).
    """

    async def extract(self, request: Request) -> dict:
        """
        Extracts form data from the request.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            dict: Parsed form data as a dictionary.
        """
        form = await request.form()
        return dict(form)


class JSONDataStrategy(DataStrategy):
    """
    Extracts data from a FastAPI request's JSON body.

    Typically used when clients send JSON payloads in POST or PUT requests.
    """

    async def extract(self, request: Request) -> dict:
        """
        Extracts JSON data from the request.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            dict: Parsed JSON data as a dictionary.
        """
        return await request.json()


"""
Example:
    You can use these strategies with a dynamic form handler like so:

    >>> from fastapi import FastAPI, Request
    >>> from pydantic import BaseModel
    >>> from your_module import JSONDataStrategy, FormDataStrategy

    >>> app = FastAPI()

    >>> class ExampleModel(BaseModel):
    ...     name: str
    ...     age: int

    >>> json_strategy = JSONDataStrategy()
    >>> form_strategy = FormDataStrategy()

    >>> @app.post("/submit/json/")
    ... async def handle_json(request: Request):
    ...     data = await json_strategy.extract(request)
    ...     return {"parsed": data}

    >>> @app.post("/submit/form/")
    ... async def handle_form(request: Request):
    ...     data = await form_strategy.extract(request)
    ...     return {"parsed": data}
"""
