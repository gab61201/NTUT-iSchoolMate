from nicegui import app, ui
from modules.course import Course
from .right_panel import render_right_panel

async def timetable_ui():
    user = getattr(app, "user")

    @ui.refreshable
    async def render_timetable(seme: str):
        # 若還沒抓過該學期的 timetable，就先去抓（避免 KeyError）
        if seme not in user.timetable:
            ui.label("載入中...").classes("w-full text-center")
            success = await user.fetch_seme_timetable(seme)
            if not success:
                ui.notify(f"無法取得 {seme} 的課表", color="negative")
                return

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
            elif type(lesson) == Course: # lesson: Course
                ui.button(lesson.name, color="yellow-100", on_click=lambda l=lesson:render_right_panel.refresh("course", l))\
                    .classes("w-full h-full text-center leading-tight").props('dense')

    with ui.grid(columns='minmax(0, 2fr)'+' 3fr'*5 , rows='1fr'+' 2fr'*9).classes("w-full h-full gap-1 p-0"):
        with ui.button(icon='menu', color="orange-300").classes("w-full h-full text-black"):
            with ui.menu().props('auto-close'):
                for seme in user.seme_list:
                    ui.menu_item(text=seme, on_click=lambda s=seme: render_timetable.refresh(s))
        # 呼叫前先檢查 user.seme_list 是否有內容
        if user.seme_list:
            await render_timetable(user.seme_list[0])


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
    ui.label("期待一下")


def search_empty_classroom_ui():
    ui.label("期待一下")


def schedule_ui():
    ui.label("期待一下")


def student_info_ui():
    ui.label("期待一下")