from nicegui import app, ui
from modules.user import UserManager


@ui.page('/login', title='登入')
async def login_route():

    user: UserManager = getattr(app, "user")
    auto_login = app.storage.general.setdefault("auto_login", False)

    async def handle_login():
        """處理登入邏輯"""
        login_button.set_visibility(False)
        skeleton.set_visibility(visible=True)

        login_msg = await user.login(student_id.value, password.value)
        if login_msg:
            ui.notify(login_msg)
            login_button.set_visibility(True)
            skeleton.set_visibility(visible=False)
            return
        
        #####
        await user.fetch_year_seme_list()
        for seme in user.seme_list:
            await user.fetch_seme_timetable(seme)
        await user.fetch_course_list()
        ui.navigate.to('/home')

    def handle_auto_login(isEnabled):
        app.storage.general["auto_login"] = isEnabled.value
    
    with ui.column().classes('w-full h-[calc(100vh-32px)] justify-center items-center'):
        with ui.card().classes('w-96 p-8 rounded-2xl shadow-2xl'):
            ui.label('歡迎回來').classes('text-2xl font-bold text-center w-full mb-4')

            student_id = ui.input(label='學號') \
                .props('outlined').classes('w-full')
            
            password = ui.input(label='密碼', password=True, password_toggle_button=True) \
                .props('outlined').classes('w-full')
            
            login_button = ui.button('登 入', on_click=handle_login, color='primary').classes('w-full mt-4 h-12')
            with ui.skeleton().classes("w-full mt-4 h-12 flex justify-center items-center") as skeleton:
                ui.spinner(size='lg')
            skeleton.set_visibility(False)

            ui.keyboard(on_key=lambda e: handle_login() if e.key == 'Enter' else None)
            ui.checkbox('啟動時自動登入', on_change=handle_auto_login, value=auto_login)

    if auto_login:
        student_id.value = app.storage.general["last_user_id"]
        password.value = user.credentials.load(student_id.value)
        await handle_login()
    