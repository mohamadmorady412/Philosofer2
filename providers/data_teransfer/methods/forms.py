from abc import ABC
from typing import Type

from fastapi import Request
from pydantic import BaseModel, Field, create_model

from providers.data_teransfer.strategy.fs import DataStrategy


class DynamicForm(ABC):
    def __init__(self, model_cls: Type[BaseModel], strategy: DataStrategy):
        self.model_cls = model_cls
        self.strategy = strategy
        self.data: BaseModel | None = None

    async def from_request(self, request: Request) -> BaseModel:
        raw_data = await self.strategy.extract(request)
        self.data = self.model_cls(**raw_data)
        return self.data

    def to_dict(self) -> dict:
        return self.data.model_dump() if self.data else {}


def create_field(name: str, field_type: type, required: bool = True, default=None):
    metadata = Field(... if required else default)
    return name, (field_type, metadata)


def build_form_class(name: str, fields: list[tuple], strategy: DataStrategy):
    model = create_model(name, **dict(fields))

    class CustomForm(DynamicForm):
        def __init__(self):
            super().__init__(model_cls=model, strategy=strategy)

    return CustomForm
