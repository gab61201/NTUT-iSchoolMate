from nicegui import app, ui
from typing import Literal, Any
from modules.course import Course


def render_default():
    ...



async def render_course(course: Course):
    loading = ui.skeleton().classes("w-full h-full")
    await course.fetch_syllabus()
    await course.fetch_description()
    loading.delete()

    ui.label(f"{course.seme}　{course.name}　{course.id}").classes("text-2xl")

    with ui.grid(rows=2, columns=4).classes("w-full h-[30%]"):
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"學分 : {course.data.get("學分")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"必/選 : {course.data.get("必/選")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"修課人數 : {course.data.get("修課人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"撤選人數 : {course.data.get("撤選人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"教師 : {course.data.get("教師")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"): ui.label(f"班級 : {course.data.get("班級")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl col-span-2"): ui.label(f"備註 : {course.data.get("備註")}")

    with ui.grid(rows=1, columns=2).classes("w-full h-[15%]"):
        ui.button("課程資訊", color="white").classes("w-full h-full text-lg rounded-xl")
        ui.button("i 學園檔案", color="white").classes("w-full h-full text-lg rounded-xl")

    with ui.card().classes("w-full h-[40%] rounded-xl"):
        ui.label("")
    



@ui.refreshable
async def render_right_panel(render_type: Literal["default", "course"], arg: Any):
    if render_type == "default":
        render_default()
    elif render_type == "course":
        await render_course(arg)