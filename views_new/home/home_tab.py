from nicegui import app, ui
from modules.user import UserManager
from modules.semester import Semester
from modules.course import Course


def get_timetable_size(table):
    days = 5
    lessons = 9

    saturday = [table[i][1] for i in range(1, 13)]
    sunday = [table[i][-1] for i in range(1, 13)]
    if any(saturday) or any(sunday):
        days = 7
    
    if any(table[12][1:]): #C
        lessons = 12
    elif any(table[11][1:]): #B
        lessons = 11
    elif any(table[10][1:]): #A
        lessons = 10
    return days, lessons
    



async def render_home_tab(user: UserManager):

    @ui.refreshable
    async def render_timetable(seme: Semester):
        timetable = seme.timetable
        days, lessons = get_timetable_size(timetable)

        with ui.grid(columns='minmax(0, 1fr)'+' 2fr'*days , rows='1fr'+' 2fr'*lessons).classes('w-[49%] h-full gap-1 p-0'):

            with ui.button(icon='menu', color="orange-300").classes("w-full h-full text-black"):
                with ui.menu().props('auto-close'):
                    for seme in user.semesters:
                        ui.menu_item(seme.semester, on_click=lambda s=seme:render_timetable.refresh(s))

            for row in range(lessons + 1):
                for column in range(days + 1 if days == 7 else days + 2):
                    cell = timetable[row][column]
                    if days == 5 and column == 1:  # skip sunday
                        continue
                    elif cell == 'menu':
                        continue
                    elif type(cell) == str:
                        with ui.card().classes('w-full h-full justify-center items-center'):
                            ui.label(cell)
                    elif type(cell) == Course:
                        ui.button(cell.name).classes('w-full h-full justify-center items-center p-0')
                    else: 
                        ui.card().classes('w-full h-full justify-center items-center')


    with ui.row().classes('w-full h-full p-0 justify-between'):
        if user.semesters:
            await render_timetable(user.semesters[0])


        with ui.card().classes('w-[49%] h-full'):
            ui.label('123')