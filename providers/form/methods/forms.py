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
This module provides utilities to dynamically build form classes using Pydantic models
and a customizable data extraction strategy. Useful for FastAPI applications where form
structures and their data sources are dynamically defined.
"""

from abc import ABC
from typing import Type

from fastapi import Request
from providers.data_teransfer.strategy.fs import DataStrategy
from pydantic import BaseModel, Field, create_model


class DynamicForm(ABC):
    """
    Base class for dynamically generated forms using a specified data strategy.

    Attributes:
        model_cls (Type[BaseModel]): The Pydantic model class used for validation.
        strategy (DataStrategy): Strategy used to extract data from a request.
        data (BaseModel | None): An instance of the model class containing parsed data.
    """

    def __init__(self, model_cls: Type[BaseModel], strategy: DataStrategy):
        """
        Initializes a DynamicForm with the given model and data extraction strategy.

        Args:
            model_cls (Type[BaseModel]): Pydantic model to use for validation.
            strategy (DataStrategy): Strategy for extracting request data.
        """
        self.model_cls = model_cls
        self.strategy = strategy
        self.data: BaseModel | None = None

    async def from_request(self, request: Request) -> BaseModel:
        """
        Extracts and parses data from an incoming request using the strategy.

        Args:
            request (Request): FastAPI request object.

        Returns:
            BaseModel: The parsed and validated data.
        """
        raw_data = await self.strategy.extract(request)
        self.data = self.model_cls(**raw_data)
        return self.data

    def to_dict(self) -> dict:
        """
        Converts the validated data to a dictionary.

        Returns:
            dict: Parsed form data as a dictionary. Empty if no data is set.
        """
        return self.data.model_dump() if self.data else {}


def create_field(name: str, field_type: type, required: bool = True, default=None):
    """
    Creates a field definition for dynamic Pydantic model creation.

    Args:
        name (str): Field name.
        field_type (type): Type of the field.
        required (bool): Whether the field is required. Defaults to True.
        default: Default value if the field is not required.

    Returns:
        tuple: A name and a tuple containing the field type and Pydantic Field.
    """
    metadata = Field(... if required else default)
    return name, (field_type, metadata)


def build_form_class(name: str, fields: list[tuple], strategy: DataStrategy):
    """
    Dynamically builds a form class based on the given name, fields, and strategy.

    Args:
        name (str): Name of the form/model class.
        fields (list[tuple]): List of field definitions created by `create_field`.
        strategy (DataStrategy): Strategy for extracting data.

    Returns:
        Type[DynamicForm]: A custom form class extending DynamicForm.
    """
    model = create_model(name, **dict(fields))

    class CustomForm(DynamicForm):
        def __init__(self):
            """
            Initializes the custom form using the dynamically generated model.
            """
            super().__init__(model_cls=model, strategy=strategy)

    return CustomForm


"""
Example:
    Here's how you might use this module in a FastAPI route:

    >>> from fastapi import FastAPI, Request
    >>> from pydantic import constr
    >>> from providers.data_teransfer.strategy.fs import JSONBodyStrategy
    >>> from your_module import create_field, build_form_class

    >>> app = FastAPI()

    >>> fields = [
    ...     create_field("username", str),
    ...     create_field("email", constr(regex=r"[^@]+@[^@]+\.[^@]+")),
    ...     create_field("age", int, required=False, default=18),
    ... ]

    >>> UserForm = build_form_class("UserForm", fields, strategy=JSONBodyStrategy())

    >>> @app.post("/submit/")
    ... async def submit(request: Request):
    ...     form = UserForm()
    ...     data = await form.from_request(request)
    ...     return {"parsed_data": form.to_dict()}
"""
