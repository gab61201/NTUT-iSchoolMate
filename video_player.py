from nicegui import ui, app
from fastapi.responses import StreamingResponse
import httpx
VIDEO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"

# 代理影片串流
@app.get("/proxy")
async def proxy_video(url: str):
    async with httpx.AsyncClient(timeout=None) as client:
        # 開啟串流請求
        resp = await client.get(url, follow_redirects=True)
        # 傳回串流給使用者
        return StreamingResponse(
            resp.aiter_bytes(),
            media_type=resp.headers.get("content-type", "video/mp4"),
            headers={"Cache-Control": "no-store"}
        )

# NiceGUI 頁面
with ui.card():
    ui.label("🎬 Video Proxy Player")
    video = ui.video(f"/proxy?url={VIDEO_URL}").props("controls autoplay").classes("w-full mt-4")

ui.run(reload=False)
