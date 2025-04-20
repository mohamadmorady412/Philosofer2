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
This module defines an abstract base class for template loaders
and provides an example of how such a loader might be used within a FastAPI application.
"""
from abc import ABC, abstractmethod
from typing import Dict

from fastapi.responses import HTMLResponse


class AbstractTemplateLoader(ABC):
    """
    An abstract base class defining the interface for template loaders.

    Subclasses must implement the `render` method to load and render
    templates using a specific templating engine.
    """

    @abstractmethod
    def render(self, template_name: str, context: Dict) -> HTMLResponse:
        """
        Renders a template given its name and a context dictionary.

        Args:
            template_name: The name or path of the template file.
            context: A dictionary containing the data to be passed to the template.

        Returns:
            An HTMLResponse object containing the rendered template.
        """
        pass
