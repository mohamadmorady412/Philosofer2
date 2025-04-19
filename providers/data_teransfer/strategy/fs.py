# strategies.py
from abc import ABC, abstractmethod

from fastapi import Request


class DataStrategy(ABC):
    @abstractmethod
    async def extract(self, request: Request) -> dict:
        pass


class FormDataStrategy(DataStrategy):
    async def extract(self, request: Request) -> dict:
        form = await request.form()
        return dict(form)


class JSONDataStrategy(DataStrategy):
    async def extract(self, request: Request) -> dict:
        return await request.json()
