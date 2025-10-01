import asyncio
from nicegui import app, ui
from home_components.navigation_bar import *
from home_components.middle_panel import *
from home_components.right_panel import *


@ui.page('/home')
async def home_page():
    if not app.storage.general.get("login_status") :
        ui.navigate.to('/login')
        return

    """定義主頁的佈局和內容"""
    with ui.grid(columns='1fr 5fr 8fr').classes("w-full h-[calc(100vh-32px)]"):

        #導覽列
        with ui.column().classes('w-full h-full rounded-2xl items-center'):
            home_button()
            ui.space()

            with ui.tabs().classes('w-full').props("vertical") as tabs:
                navigation_tabs()

            ui.space()
            logout_and_exit_button()
        
        #中間卡片
        with ui.tab_panels(tabs, value='timetable_tab')\
            .classes('w-full h-[calc(100vh-32px)] rounded-2xl bg-gray-200 shadow-lg').props("vertical"):
            with ui.tab_panel('timetable_tab').classes("flex-nowrap gap-2 p-4"):
                timetable_ui()
            with ui.tab_panel('course_list_tab'):
                course_list_ui()
            with ui.tab_panel('course_search_tab'):
                course_search_ui()
            with ui.tab_panel('schedule_tab'):
                schedule_ui()
            with ui.tab_panel('student_info_tab'):
                student_info_ui()
        #右側卡片
        with ui.card().classes("h-full rounded-2xl"):
            ui.label("第三塊 (8fr)")
