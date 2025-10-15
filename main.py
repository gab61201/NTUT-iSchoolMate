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
    setattr(app, "user", UserManager())

    tray_icon = TrayIconManager(8000)
    setattr(app, "tray_icon", tray_icon)
    asyncio.create_task(tray_icon.run_in_background())

    webbrowser.open(f"http://localhost:8000/login")


async def shutdown():

    if not app.storage.general["auto_login"]:
        app.storage.general["last_user_id"] = ""
        getattr(app, "credentials").delete(app.storage.general["last_user_id"])
    
    tray_icon = getattr(app, "tray_icon")
    if tray_icon:
        tray_icon.icon.notify("已成功退出", "退出")
        tray_icon.icon.stop()

app.on_startup(startup)
app.on_shutdown(shutdown)
ui.run(port=8000, show=False, reload=False, uvicorn_logging_level="warning")