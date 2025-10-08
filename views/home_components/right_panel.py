from nicegui import app, ui
from typing import Literal, Any
from modules.course import Course


def render_home():
    ...

def render_course(course: Course):
    
    ui.label(course.name).classes("text-4lg")


@ui.refreshable
def render_right_panel(render_type: Literal["home", "course"], arg: Any):
    if render_type == "home":
        render_home()
    elif render_type == "course":
        render_course(arg)