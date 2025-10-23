from nicegui import app, ui
from modules.user import UserManager
from modules.semester import Semester
from modules.course import Course


async def render_home_tab(user: UserManager):

    @ui.refreshable
    async def render_timetable(seme: Semester):
        timetable = seme.timetable
        for hour in timetable:
            for lesson in hour:
                if lesson == 'menu':
                    continue
                elif type(lesson) == str:
                    with ui.card().classes('w-full h-full justify-center items-center'):
                        ui.label(lesson)
                elif type(lesson) == Course:
                    ui.button(lesson.name).classes('w-full h-full justify-center items-center p-0')
                else: 
                    ui.card().classes('w-full h-full justify-center items-center')

    with ui.row().classes('w-full h-full p-0 justify-between'):


        with ui.grid(columns='minmax(0, 1fr)'+' 2fr'*7 , rows='1fr'+' 2fr'*12).classes('w-[49%] h-full gap-1 p-0'):

            with ui.button(icon='menu', color="orange-300").classes("w-full h-full text-black"):
                with ui.menu().props('auto-close'):
                    for seme in user.semesters:
                        ui.menu_item(seme.semester, on_click=lambda s=seme:render_timetable.refresh(s))
            if user.semesters:
                await render_timetable(user.semesters[0])


        with ui.card().classes('w-[49%] h-full'):
            ui.label('123')