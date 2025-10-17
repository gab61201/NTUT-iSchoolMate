import asyncio
import webbrowser
import logging
import re
from nicegui import app, ui, native
from modules import *
from views import *

logging.basicConfig(
    level=logging.ERROR
)

async def startup():
    # init
    setattr(app, "user", UserManager())

    port = 8080
    for url in app.urls:
        result = re.search(r"http://127.0.0.1:(\d{4})", url)
        if result:
            port = int(result.group(1))
            setattr(app, "port", port)
            break

    tray_icon = TrayIconManager(port)
    setattr(app, "tray_icon", tray_icon)
    asyncio.create_task(tray_icon.run_in_background())
    webbrowser.open(f"http://127.0.0.1:{port}/login")


async def shutdown():

    tray_icon = getattr(app, "tray_icon")
    if tray_icon:
        tray_icon.icon.notify("已成功退出", "退出")
        tray_icon.icon.stop()

app.on_startup(startup)
app.on_shutdown(shutdown)
ui.run(port=native.find_open_port(8000), host="127.0.0.1", show=False, reload=False, uvicorn_logging_level="warning")