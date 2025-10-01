import asyncio
from nicegui import app, ui
from home_components.navigation_bar import *
from home_components.middle_panel import *
from home_components.right_panel import *


def on_logout():
    """處理登出邏輯"""
    getattr(app, "credentials").delete(app.storage.general["last_user_id"])
    app.storage.general["last_user_id"] = ""
    app.storage.general["login_status"] = False
    app.storage.general["auto_login"] = False
    ui.navigate.to('/login')


def on_exit_app():
    ui.navigate.to('/exit')
    app.shutdown()

        

@ui.page('/home')
async def home_page():
    if not app.storage.general.get("login_status") :
        ui.navigate.to('/login')
        return

    """定義主頁的佈局和內容"""
    with ui.grid(columns='1fr 5fr 8fr').classes("w-full h-[calc(100vh-32px)]"):

        #導覽列
        with ui.column().classes('w-full h-full rounded-2xl items-center'):
            # ui.space().classes("h-[20%]")
            ui.button(icon="school").classes("w-full text-2xl text-black bg-white").props("rounded flat")
            ui.space()

            with ui.tabs().classes('w-full').props("vertical") as tabs:
                ui.tab('timetable_tab', '個人課表').classes("text-lg")
                ui.tab('course_list_tab', '課程清單').classes("text-lg")
                ui.tab('course_search_tab', '課程查詢').classes("text-lg")
                # ui.tab('course_file_tab', '課程檔案').classes("text-lg")
                ui.tab('schedule_tab', '行事曆').classes("text-lg")
                ui.tab('student_info_tab', '個人資訊').classes("text-lg")
            # ui.button("北科入口", color="blue-2").classes('w-full h-[8%] rounded-2xl whitespace-nowrap text-black')
            # ui.button("課程系統", color="blue-2").classes('w-full h-[8%] rounded-2xl whitespace-nowrap text-black')
            ui.space()
            ui.button("登出", on_click=on_logout, color="orange-5").classes('w-[80%] h-[5%] rounded-2xl text-md')
            ui.button("退出", on_click=on_exit_app, color="red-5").classes('w-[80%] h-[5%] rounded-2xl text-md')
        
        #中間卡片
        with ui.tab_panels(tabs, value='timetable_tab')\
            .classes('w-full h-[calc(100vh-32px)] rounded-2xl bg-gray-200 shadow-lg').props("vertical"):
            with ui.tab_panel('timetable_tab').classes("flex-nowrap gap-2 p-4"):
                timetable_ui()
            with ui.tab_panel('course_list_tab'):
                course_list_ui()
        
        #右側卡片
        with ui.card().classes("h-full rounded-2xl"):
            ui.label("第三塊 (8fr)")
