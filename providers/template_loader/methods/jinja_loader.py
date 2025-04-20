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
This module defines a concrete implementation of the AbstractTemplateLoader
using the Jinja2 templating engine.
"""
from typing import Dict

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from providers.template_loader.strategy.jinja_strategy import AbstractTemplateLoader


class JinjaTemplateLoader(AbstractTemplateLoader):
    """
    A concrete implementation of the AbstractTemplateLoader using the Jinja2 templating engine.
    """

    def __init__(self, templates_dir: str = "templates"):
        """
        Initializes the JinjaTemplateLoader with a directory containing Jinja2 templates.

        Args:
            templates_dir: The path to the directory where Jinja2 templates are stored.
                           Defaults to "templates".
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, template_name: str, context: Dict) -> HTMLResponse:
        """
        Loads and renders a Jinja2 template.

        Args:
            template_name: The name of the Jinja2 template file to render.
            context: A dictionary containing the data to be passed to the template.

        Returns:
            An HTMLResponse object containing the rendered output.
        """
        template = self.env.get_template(template_name)
        content = template.render(**context)
        return HTMLResponse(content=content)


"""
Example Usage:
>>> from fastapi import FastAPI
>>> from fastapi.routing import APIRouter
>>> from typing import Dict
>>> from fastapi.responses import HTMLResponse
>>> from providers.template_loader.strategy.jinja_strategy import AbstractTemplateLoader
>>> from jinja2 import Environment, FileSystemLoader, select_autoescape
>>> class JinjaTemplateLoader(AbstractTemplateLoader):
>>>     def __init__(self, templates_dir: str = "templates"):
>>>         self.templates_dir = templates_dir
>>>         self.env = Environment(
>>>             loader=FileSystemLoader(self.templates_dir),
>>>             autoescape=select_autoescape(['html', 'xml'])
>>>         )
>>>
>>>     def render(self, template_name: str, context: Dict) -> HTMLResponse:
>>>         template = self.env.get_template(template_name)
>>>         content = template.render(**context)
>>>         return HTMLResponse(content=content)
>>> app = FastAPI()
>>> router = APIRouter()
>>>
>>> # Assuming you have a 'templates' directory with a file named 'index.html'
>>> # containing something like: <h1>Hello, {{ name }}!</h1>
>>> template_loader = JinjaTemplateLoader(templates_dir="templates")
>>>
>>> @router.get("/")
>>> async def read_root():
>>>     context: Dict = {"name": "World"}
>>>     return template_loader.render("index.html", context)
>>>
>>> app.include_router(router)
"""
