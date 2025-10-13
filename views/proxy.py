from nicegui import app
from fastapi.responses import StreamingResponse
from fastapi import Request, Response
from starlette.background import BackgroundTask
from urllib.parse import urlparse
import httpx

from modules.user import UserManager


@app.get("/file_download")
async def file_download(url: str):
    user: UserManager = getattr(app, "user")
    scraper_session = user.scraper.session
    parsed_url = urlparse(url)
    filename = parsed_url.path.split('/')[-1]

    if not filename:
        filename = "downloaded_file"
    try:
        from urllib.parse import quote
        filename = quote(filename)
    except Exception:
        pass

    async def stream_file():
        async with scraper_session.stream("GET", url) as resp:
            async for chunk in resp.aiter_bytes():
                yield chunk

    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}

    return StreamingResponse(
        stream_file(),
        media_type="application/octet-stream", # 通用二進制類型
        headers=headers
    )


@app.get("/file_preview")
async def file_preview(url: str):
    user: UserManager = getattr(app, "user")
    
    async def stream_file():
        scraper_session = user.scraper.session
        async with scraper_session.stream("GET", url) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            async for chunk in resp.aiter_bytes():
                yield chunk

    return StreamingResponse(
        stream_file(),
        headers={"Content-Disposition": "inline"}  # 關鍵：讓瀏覽器預覽，而非下載
    )


@app.get('/video')
async def video(channel: str, request: Request):
    user = getattr(app, "user")
    client: httpx.AsyncClient = user.scraper.session
    range_header = request.headers.get("range")
    headers_to_send = {}
    if range_header:
        headers_to_send["Range"] = range_header

    url = f'https://istream.ntut.edu.tw/videoplayer/lectureStream.php?channel={channel}'
    req = client.build_request("GET", url, headers=headers_to_send)
    
    try:
        r = await client.send(req, stream=True)
        setattr(app, "video_session", r)
    except httpx.HTTPStatusError as e:
        return Response(status_code=e.response.status_code, content=e.response.text)

    
    media_type = r.headers.get("content-type", "video/mp4")
    
    response_headers = {
        "Content-Length": r.headers.get("content-length", ""),
        "Accept-Ranges": r.headers.get("accept-ranges", "bytes"), # 確保返回 Accept-Ranges
        "Content-Range": r.headers.get("content-range", ""), # 傳回 Content-Range
    }
    
    final_headers = {k: v for k, v in response_headers.items() if v}

    return StreamingResponse(
        r.aiter_raw(), 
        status_code=r.status_code, # 必須使用遠端伺服器返回的狀態碼 (可能是 200 或 206)
        media_type=media_type,
        headers=final_headers,
        background=BackgroundTask(r.aclose)
    )

