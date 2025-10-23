from nicegui import ui
from modules.user import UserManager
from modules.semester import Semester
from modules.course import Course


def course_card(course: Course):
    with ui.card().classes('w-full h-full'):
        with ui.row().classes('w-full justify-between items-end'):
            ui.label(course.name).classes('text-lg')
            ui.label(course.id)
        ui.separator()
        ui.label(f'學分：{course.credits}')
        ui.label(f'班級：{course.classes}')



def render_course_list_tab(user: UserManager):
    with ui.tabs().classes('h-[8%]') as seme_tabs:
        for seme in user.semesters:
            ui.tab(seme.semester, seme.semester)
    
    with ui.tab_panels(seme_tabs, value=user.semesters[0].semester).classes('w-full h-[92%]'):
        for seme in user.semesters:
            with ui.tab_panel(seme.semester):
                with ui.scroll_area().classes('w-full h-full'):
                    with ui.grid().classes('w-full h-full grid-cols-4'):
                        for course in seme.courses:
                            course_card(course)