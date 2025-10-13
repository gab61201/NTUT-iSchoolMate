from nicegui import app, ui
from modules.course import Course
from modules.user import UserManager
from .right_panel import render_right_panel

async def timetable_ui():
    user: UserManager = getattr(app, "user")

    @ui.refreshable
    async def render_timetable(seme: str):
        if seme not in user.timetable:
            loading = ui.skeleton().classes("w-full h-full rounded-2xl")
            success = await user.fetch_seme_timetable(seme)
            loading.delete()
            if not success:
                ui.notify(f"無法取得 {seme} 的課表", color="negative")
                return

        course_list = []
        for i in user.timetable[seme]:
            course_list += i
        course_list.pop(0)

        for course in course_list:
            if course == None:
                ui.card().classes("w-full h-full")
            elif type(course) == str:
                with ui.card().classes("w-full h-full bg-orange-100 flex justify-center items-center p-1"):
                    ui.label(course).classes("text-center line-clamp-3")
            elif type(course) == Course: # course: Course
                ui.button(course.name, color="yellow-100", on_click=lambda c=course:render_right_panel.refresh("course", c))\
                    .classes("w-full h-full text-center leading-tight").props('dense')

    with ui.grid(columns='minmax(0, 2fr)'+' 3fr'*5 , rows='1fr'+' 2fr'*9).classes("w-full h-full gap-1 p-0"):
        with ui.button(icon='menu', color="orange-300").classes("w-full h-full text-black"):
            with ui.menu().props('auto-close'):
                for seme in user.seme_list:
                    ui.menu_item(text=seme, on_click=lambda s=seme: render_timetable.refresh(s))
        
        if user.seme_list:
            await render_timetable(user.seme_list[0])


def course_list_ui():
    user: UserManager = getattr(app, "user")
    
    @ui.refreshable
    def total_credits(seme):
        credits = 0
        for course in user.course_list[seme].values():
            credits += float(course.credits)
        ui.label(f"學分數 : {credits:.1f}")

    @ui.refreshable
    def render_course_list(seme):
        for id, course in user.course_list[seme].items():
            ui.button(f"{id}　{course.name}", color="white", on_click=lambda c=course:render_right_panel.refresh("course", c))\
                .classes('w-full h-8 rounded-lg').props('align=left')

    def on_selection_change(seme):
        total_credits.refresh(seme)
        render_course_list.refresh(seme)

    with ui.row().classes("w-full justify-between items-center"):
        ui.select(options=user.seme_list, value=user.seme_list[0], on_change=lambda e:on_selection_change(e.value))
        total_credits(user.seme_list[0])
    render_course_list(user.seme_list[0])


def course_search_ui():
    ui.label("期待一下")


def search_empty_classroom_ui():
    ui.label("期待一下")


def schedule_ui():
    url = 'index.html'
    ui.element('iframe').props(f'src="{url}"').classes('w-full h-full')


def student_info_ui():
    ui.label("期待一下")