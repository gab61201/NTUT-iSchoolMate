from .home.home import home_route
from .login import login_route
from .exit import exit_route
from .proxy import file_download, file_preview, video

__all__ = [
    "home_route",
    "login_route",
    "exit_route",
    "file_download",
    "file_preview",
    "video",
]