from nicegui import app, ui

@ui.page('/login', title='登入')
async def login_page():

    async def handle_login():
        """處理登入邏輯"""
        login_button.set_visibility(False)
        skeleton.set_visibility(visible=True)

        scraper = getattr(app, "scraper")
        user = getattr(app, "user")

        if not await scraper.login(student_id.value, password.value):
            ui.notify('錯誤的帳號或密碼，錯誤達五次後鎖定帳號15分鐘', color='negative')
        elif not await scraper.oauth("aa_0010-oauth"):
            ui.notify("登入課程系統失敗", color='negative')
        elif not await scraper.oauth("ischool_plus_oauth"):
            ui.notify("登入課程系統失敗", color='negative')
        else:
            await user.fetch_year_seme_list()
            for seme in user.seme_list:
                print(seme)
                await user.fetch_seme_timetable(seme)
                
            await user.fetch_course_list()
            app.storage.general["login_status"] = True
            user.student_id = student_id.value
            ui.navigate.to('/home')
            return
        
        login_button.set_visibility(True)
        skeleton.set_visibility(visible=False)
            

    def handle_auto_login(isEnabled):
        app.storage.general["auto_login"] = isEnabled.value
    
    # 使用一個 flex 容器將卡片在頁面中置中
    with ui.column().classes('w-full h-[calc(100vh-32px)] justify-center items-center'):
        # 卡片作為登入表單的背景
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
            ui.checkbox('啟動時自動登入', on_change=handle_auto_login, value=app.storage.general["auto_login"])
            # ui.separator()
            # with ui.row().classes('w-full justify-between mt-2'):
            #     ui.link('入口', NPORTAL_INDEX_URL).classes('text-lg text-gray-500')
            #     ui.link('系統', COURSE_SYSTEM_URL).classes('text-lg text-gray-500')