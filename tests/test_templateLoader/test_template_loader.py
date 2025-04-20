import pytest

from providers.template_loader.methods.jinja_loader import JinjaTemplateLoader


@pytest.fixture
def temp_template_dir(tmp_path):

    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_file = template_dir / "test.html"
    template_file.write_text("<h1>{{ title }}</h1>")

    return template_dir


def test_render_template(temp_template_dir):
    loader = JinjaTemplateLoader(templates_dir=str(temp_template_dir))
    context = {"title": "تست عنوان"}

    response = loader.render("test.html", context)

    assert response.status_code == 200
    assert "<h1>تست عنوان</h1>" in response.body.decode("utf-8")
