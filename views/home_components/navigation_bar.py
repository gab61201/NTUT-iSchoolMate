from nicegui import app, ui


def home_button():
    ui.button(icon="school").classes("w-full text-2xl text-black bg-white").props("rounded flat")
    

def navigation_tabs():
    ui.tab('timetable_tab', '個人課表').classes("text-lg")
    ui.tab('course_list_tab', '課程清單').classes("text-lg")
    ui.tab('course_search_tab', '課程查詢').classes("text-lg")
    # ui.tab('course_file_tab', '課程檔案').classes("text-lg")
    ui.tab('search_empty_classroom_ui', '找空教室').classes("text-lg")
    ui.tab('schedule_tab', '行事曆').classes("text-lg")
    ui.tab('student_info_tab', '個人資訊').classes("text-lg")


def logout_and_exit_button():

    def on_logout():
        getattr(app, "credentials").delete(app.storage.general["last_user_id"])
        app.storage.general["last_user_id"] = ""
        app.storage.general["login_status"] = False
        app.storage.general["auto_login"] = False
        ui.navigate.to('/login')

    def on_exit_app():
        ui.navigate.to('/exit')
        app.shutdown()
        
    ui.button("登出", on_click=on_logout, color="orange-5").classes('w-[80%] h-[5%] rounded-2xl text-md')
    ui.button("退出", on_click=on_exit_app, color="red-5").classes('w-[80%] h-[5%] rounded-2xl text-md')