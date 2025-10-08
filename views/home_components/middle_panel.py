from nicegui import app, ui


def timetable_ui():
    user = getattr(app, "user")

    @ui.refreshable
    def render_timetable(seme: str):
        course_list = []
        for i in user.timetable[seme]:
            course_list += i
        course_list.pop(0)

        for lesson in course_list:
            if lesson == None:
                ui.card().classes("w-full h-full")
            elif type(lesson) == str:
                with ui.card().classes("w-full h-full bg-orange-100 flex justify-center items-center p-1"):
                    ui.label(lesson).classes("text-center line-clamp-3")
            else: # lesson: Course
                ui.button(lesson.name, color="yellow-100").classes("w-full h-full text-center leading-tight").props('dense')

    with ui.grid(columns='minmax(0, 2fr)'+' 3fr'*5 , rows='1fr'+' 2fr'*9).classes("w-full h-full gap-1 p-0"):
        with ui.button(icon='menu', color="orange-300").classes("w-full h-full text-black"):
            with ui.menu().props('auto-close'):
                for seme in user.seme_list:
                    ui.menu_item(text=seme, on_click=lambda s=seme: render_timetable.refresh(s))
        render_timetable(user.seme_list[0])


def course_list_ui():
    user = getattr(app, "user")
    for seme, course_list in user.course_list.items():
        ui.label(seme).classes("text-xl")
        for course in course_list.values():
            with ui.button(color="white").classes('w-full'):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(f"{course.id}_{course.name}")
                    ui.label("___")


def course_search_ui():
    ...


def search_empty_classroom_ui():
    ...


def schedule_ui():
    ...


def student_info_ui():
    ...