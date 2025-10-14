from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path




# Путь к папке с шаблонами
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)
