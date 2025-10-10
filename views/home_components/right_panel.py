from nicegui import app, ui
from typing import Literal, Any
from modules.course import Course


def render_default():
    ...


async def render_course(course: Course):
    user = getattr(app, "user")

    with ui.skeleton().classes("w-full h-full rounded-2xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')
    await course.fetch_syllabus()
    await course.fetch_description()
    loading.delete()

    ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl w-full h-[10%] items-center")

    with ui.grid(rows=3, columns=4).classes("w-full h-[40%]"):
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"學分 : {course.data.get("學分")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"必/選 : {course.data.get("必/選")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"修課人數 : {course.data.get("修課人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"撤選人數 : {course.data.get("撤選人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"教師 : {course.data.get("教師")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"班級 : {course.data.get("班級")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl col-span-2 py-1"):
            ui.label(f"備註 : {course.data.get("備註")}")

        ui.button("課程資訊", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("description", course))
        ui.button("課程錄影", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("recordings", course))
        ui.button("i學園公告", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("announcement", course))
        ui.button("i學園檔案", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("ischool", course))

    

    with ui.card().tight().classes("w-full h-[50%] rounded-lg"):
        user_notes_dict = app.storage.general.setdefault(user.student_id, {})

        def close_edit():
            e.set_visibility(False)
            preview.set_visibility(True)
        with ui.scroll_area().classes("w-full h-full rounded-xl").props('content-class="p-0"') as e:
            editor = ui.editor(placeholder='在此輸入 Markdown 語法，按 esc 退出編輯模式').on('keydown.esc', close_edit)\
                .classes('w-full h-full').props('toolbar=[]').bind_value(user_notes_dict, course.id)
        e.set_visibility(False)

        def open_edit():
            e.set_visibility(True)
            preview.set_visibility(False)
        with ui.scroll_area().classes("w-full h-full rounded-lg cursor-pointer").props('content-class="p-0"')\
            .on("dblclick", open_edit).tooltip("雙擊以編輯") as preview:
            ui.markdown().classes("w-full h-full select-none").bind_content_from(editor, 'value')


def render_description(course:Course):
    ...


def render_recordings(course:Course):
    ...


def render_announcement(course: Course):
    ...


def render_ischool(course: Course):
    ...


@ui.refreshable
async def render_right_panel(render_type: Literal["default", "course", "recordings", "description", "announcement", "ischool"], arg: Any):
    
    def render_title(course:Course, page_name: str):
        with ui.row().classes("w-full h-[10%], items-center"):
            ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl hover:underline cursor-pointer")\
                .on('click', lambda: render_right_panel.refresh("course", course))
            ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
            ui.label(page_name).classes("text-2xl")

    if render_type == "default":
        render_default()

    elif render_type == "course":
        await render_course(arg)

    elif render_type == "description":
        render_title(arg, "課程資訊")
        render_description(arg)

    elif render_type == "recordings":
        render_title(arg, "課程錄影")
        render_recordings(arg)

    elif render_type == "announcement":
        render_title(arg, "i學園公告")
        render_announcement(arg)
        
    elif render_type == "ischool":
        render_title(arg, "i學園檔案")
        render_ischool(arg)