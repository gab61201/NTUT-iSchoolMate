import asyncio
import webbrowser
import logging
from nicegui import app, ui
from modules import *
from views import *

logging.basicConfig(
    level=logging.ERROR
)

async def startup():
    # init
    app.storage.general["login_status"] = False
    app.storage.general.setdefault("auto_login", False)
    app.storage.general.setdefault("last_user_id", "")

    tray_icon = TrayIconManager(8000)
    setattr(app, "tray_icon", tray_icon)
    asyncio.create_task(tray_icon.run_in_background())

    credentials = CredentialsManager()
    setattr(app, "credentials", credentials)

    scraper = WebScraper()
    setattr(app, "scraper", scraper)

    user = UserManager(scraper)
    setattr(app, "user", user)

    # auto login service
    auto_login = app.storage.general["auto_login"]
    last_user_id = app.storage.general["last_user_id"]
    password = credentials.load(last_user_id)

    if not (last_user_id and password):
        credentials.delete(last_user_id)
        app.storage.general["last_user_id"] = ""
        webbrowser.open(f"http://localhost:8000/login")

    elif auto_login and await scraper.login(last_user_id, password):
        ui.notify('錯誤的帳號或密碼，錯誤達五次後鎖定帳號15分鐘', color='negative')
        if not await scraper.oauth("aa_0010-oauth"):
            ui.notify("登入課程系統失敗", color='negative')
        elif not await scraper.oauth("ischool_plus_oauth"):
            ui.notify("登入課程系統失敗", color='negative')
        elif not await user.fetch_year_seme_list():
            ui.notify("登入課程系統失敗", color='negative')
        else:
            for seme in user.seme_list:
                await user.fetch_seme_timetable(seme)
                
            await user.fetch_course_list()
        app.storage.general["login_status"] = True
        user.student_id = last_user_id
        webbrowser.open(f"http://localhost:8000/home")
    
    else:
        webbrowser.open(f"http://localhost:8000/login")
    

async def shutdown():

    app.storage.general["login_status"] = False

    if not app.storage.general["auto_login"]:
        app.storage.general["last_user_id"] = ""
        getattr(app, "credentials").delete(app.storage.general["last_user_id"])
    
    tray_icon = getattr(app, "tray_icon")
    if tray_icon:
        tray_icon.icon.notify("已成功退出 北科 i 學園 Pro", "退出")
        tray_icon.icon.stop()

app.on_startup(startup)
app.on_shutdown(shutdown)
ui.run(port=8000, show=False, reload=False, uvicorn_logging_level="warning")