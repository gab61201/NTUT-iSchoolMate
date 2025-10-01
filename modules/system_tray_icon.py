import asyncio
from nicegui import app
import pystray
from PIL import Image
from pystray import MenuItem
import webbrowser
import logging


IMAGE_PATH = "static/images/icon.png"


class TrayIconManager:
    """管理系統匣圖示"""

    def __init__(self, port: int):
        """
        初始化管理器。
        :param port: NiceGUI 應用程式運行的埠號。
        """
        self.port = port
        self.icon = None  # 先將 icon 初始化為 None

    def _on_open(self):
        is_logged_in = app.storage.general.get("login_status", False)
        
        if is_logged_in:
            webbrowser.open(f"http://localhost:{self.port}/home")
        else:
            webbrowser.open(f"http://localhost:{self.port}/login")
            

    def _on_exit(self):
        print("正在從系統匣退出...")
        if self.icon:
            self.icon.notify("正在退出...", "退出")

        app.shutdown()


    async def run_in_background(self):
        """
        在背景執行緒中設定並運行系統匣圖示。
        這是主要的非同步進入點。
        """
        try:
            image = Image.open(IMAGE_PATH)
            menu = pystray.Menu(
                MenuItem(text='開啟視窗', action=self._on_open, default=True),
                MenuItem(text='退出', action=self._on_exit)
                )
            
            # 建立 icon 實例並存到 self.icon
            self.icon = pystray.Icon("NTUTiSchoolPro", image, "北科 i 學園 Pro", menu)

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.icon.run)
            print("系統匣圖示執行緒已結束。")

        except FileNotFoundError:
            logging.error(f"系統匣圖示錯誤：找不到圖示檔案於 {IMAGE_PATH}")
            app.shutdown()

        except Exception as e:
            logging.critical(f"系統匣發生未預期的嚴重錯誤: {e}", exc_info=True)
            app.shutdown()