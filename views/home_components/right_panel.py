from nicegui import app, ui
from fastapi.responses import StreamingResponse, HTMLResponse
from urllib.parse import urlparse, parse_qs
from typing import Literal, Any
from modules.course import Course
from modules.web_scraper import WebScraper
from modules.user import UserManager


def render_default():
    ...


async def render_course(course: Course):
    with ui.skeleton().classes("w-full h-full rounded-2xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')
    await course.fetch_syllabus()
    await course.fetch_description()
    loading.delete()

    ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl w-full h-[10%] items-center")

    with ui.grid(rows=3, columns=4).classes("w-full h-[40%]"):
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"學分 : {course.data.get("學分")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"必/選 : {course.data.get("必/選")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"修課人數 : {course.data.get("修課人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"撤選人數 : {course.data.get("撤選人數")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"教師 : {course.data.get("教師")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl"):
            ui.label(f"班級 : {course.data.get("班級")}")
        with ui.card().classes("w-full h-full justify-center rounded-xl col-span-2 py-1"):
            ui.label(f"備註 : {course.data.get("備註")}")

        ui.button("課程資訊", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("description", course))
        ui.button("課程錄影", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("recordings", course))
        ui.button("i學園公告", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("announcement", course))
        ui.button("i學園檔案", color="white").classes("w-full h-full text-lg rounded-xl")\
            .on_click(lambda: render_right_panel.refresh("ischool_files", course))

    

    with ui.card().tight().classes("w-full h-[50%] rounded-lg"):
        user = getattr(app, "user")
        user_notes_dict = app.storage.general.setdefault(user.student_id, {})

        def close_edit():
            e.set_visibility(False)
            preview.set_visibility(True)
        with ui.scroll_area().classes("w-full h-full rounded-xl").props('content-class="p-0"') as e:
            editor = ui.editor(placeholder='在此輸入 Markdown 語法，按 esc 退出編輯模式').on('keydown.esc', close_edit)\
                .classes('w-full h-full').props('toolbar=[]').bind_value(user_notes_dict, course.id)
        e.set_visibility(False)

        def open_edit():
            e.set_visibility(True)
            preview.set_visibility(False)
        with ui.scroll_area().classes("w-full h-full rounded-lg cursor-pointer").props('content-class="p-0"')\
            .on("dblclick", open_edit).tooltip("雙擊以編輯") as preview:
            ui.markdown().classes("w-full h-full select-none").bind_content_from(editor, 'value')


def render_description(course:Course):
    ...


def render_recordings(course:Course):
    ...


def render_announcement(course: Course):
    ...


async def render_ischool_files(course: Course):
    user = getattr(app, "user")
    with ui.skeleton().classes("w-full h-[90%] rounded-xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')
    if not await course.fetch_files():
        ui.label("無法獲取檔案").classes("text-2xl w-full")
        return
    loading.delete()

    if not course.file_tree:
        ui.label("沒有上傳檔案").classes("text-2xl w-full")
        return

    def open_in_new(e):
        """在新分頁中開啟連結"""
        node_data = e.args
        print(node_data)

        url = node_data.get('href')
        if url and url.startswith('http'):
            ui.navigate.to(f"/file_preview?url={url}", new_tab=True)
            ui.notify(f"正在開啟：{node_data.get('text')}", type='positive')
        else:
            ui.notify(f"無法開啟無效的連結：{url}", type='warning')

    async def download(e):
        node_data = e.args
        print(node_data)

        original_url = e.args.get('href', '')
        text = e.args.get('text', 'Unknown File')
        
        if original_url:
            download_url = f"/file_download?url={original_url}"
            ui.navigate.to(download_url)
            ui.notify(f'開始下載: {text}', type='info')
        else:
            ui.notify(f'錯誤: 找不到下載連結 ({text})', type='negative')

    async def on_select(e):
        """
        若非葉節點，則開啟節點
        若為葉節點，則開啟預覽
        """
        if course.file_dict[e.value].get("leaf"):
            render_right_panel.refresh('file_preview', course, course.file_dict[e.value]["text"], e.value)
    
    with ui.scroll_area().classes("w-full h-full"):
        tree = ui.tree(course.file_tree, label_key='text', children_key="item", node_key='identifier', on_select=lambda e:on_select(e))\
        .classes("text-lg w-full").expand()

        body_template = r'''
        <div v-if="props.node.leaf" :props="props" class="flex flex-nowrap items-start justify-between px-8 py-1 gap-2 w-full text-grey">
            <span class="text-sm break-words">
                {{
                props.node.href
                    ? (
                        props.node.href.startsWith('https://istudy.ntut.edu.tw')
                            ? decodeURIComponent(props.node.href.split('/').pop())
                            : props.node.href
                    )
                    : ''
                }}
            </span>
        </div>
        '''
        tree.add_slot('default-body', body_template)

        header_template = r'''
        <div class="flex items-center w-full px-4 py-1 rounded bg-gray-200 hover:bg-gray-300"
            style="background-color: #f3f4f6 !important; /* 確保覆蓋預設樣式 */">
            <span class="flex-grow text-lg">
                {{ props.node.text }}
            </span>
            <a v-if="
                    props.node.href && 
                    (
                        !props.node.href.startsWith('https://istudy.ntut.edu.tw') || /* 非 istudy 連結 (純外部連結) */
                        props.node.href.toLowerCase().endsWith('.pdf') ||               /* istudy 連結且可瀏覽 */
                        props.node.href.toLowerCase().endsWith('.txt') ||
                        props.node.href.toLowerCase().endsWith('.png') ||
                        props.node.href.toLowerCase().endsWith('.jpg') ||
                        props.node.href.toLowerCase().endsWith('.html')
                        /* ... 可以在此處加入更多可瀏覽類型 */
                    )
                "
                :href="'/file_preview?url=' + props.node.href"
                target="_blank" 
                rel="noopener noreferrer"
                @click.stop 
                class="text-sm cursor-pointer text-primary hover:text-blue-700 underline"
            >
                在新分頁開啟
            </a>
            
            <a v-if="
                    props.node.href && 
                    props.node.href.startsWith('https://istudy.ntut.edu.tw')
                "
                :href="'/file_download?url=' + props.node.href"
                target="_blank" 
                rel="noopener noreferrer"
                @click.stop 
                class="text-sm cursor-pointer text-primary hover:text-blue-700 underline"
            >
               下載
            </a>
            
        </div>
        '''
        tree.add_slot('default-header', header_template)


async def render_preview(course: Course, page_name:str, identifier: str):
    proxy_url = course.file_dict[identifier]["href"]

    with ui.row().classes("w-full h-[10%] items-center"):
        ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl hover:underline cursor-pointer")\
            .on('click', lambda: render_right_panel.refresh("course", course))
        ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
        ui.label("i學園檔案").classes("text-2xl hover:underline cursor-pointer")\
            .on('click', lambda: render_right_panel.refresh("ischool_files", course))
        ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
        ui.label(page_name).classes("text-2xl")

    ui.element('iframe').props(f'src="/file_preview?url={proxy_url}"') \
        .classes('w-full h-full border-2 rounded-lg')


@app.get("/file_preview")
async def file_preview(url: str):
    user: UserManager = getattr(app, "user")
    
    async def stream_file():
        scraper_session = user.scraper.session
        async with scraper_session.stream("GET", url) as resp:
            async for chunk in resp.aiter_bytes():
                yield chunk

    return StreamingResponse(
        stream_file(),
        headers={"Content-Disposition": "inline"}  # 關鍵：讓瀏覽器預覽，而非下載
    )


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


@ui.refreshable
async def render_right_panel(render_type: Literal["default",
                                                  "course",
                                                  "recordings",
                                                  "description",
                                                  "announcement",
                                                  "ischool_files",
                                                  "file_preview"], *arg: Any):
    
    def render_title(course:Course, file_name: str):
        with ui.row().classes("w-full h-[10%] items-center"):
            ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl hover:underline cursor-pointer")\
                .on('click', lambda: render_right_panel.refresh("course", course))
            ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
            ui.label(file_name).classes("text-2xl")

    if render_type == "default":
        render_default()

    elif render_type == "course":
        await render_course(arg[0])

    elif render_type == "description":
        render_title(arg[0], "課程資訊")
        render_description(arg[0])

    elif render_type == "recordings":
        render_title(arg[0], "課程錄影")
        render_recordings(arg[0])

    elif render_type == "announcement":
        render_title(arg[0], "i學園公告")
        render_announcement(arg[0])
        
    elif render_type == "ischool_files":
        render_title(arg[0], "i學園檔案")
        await render_ischool_files(arg[0])
    
    elif render_type == "file_preview":
        await render_preview(*arg)