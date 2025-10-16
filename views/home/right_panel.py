from nicegui import app, ui
from typing import Literal, Any
from modules.course import Course


def render_default():
    ...


async def render_course(course: Course):
    with ui.skeleton().classes("w-full h-full rounded-2xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')
    await course.fetch_syllabus()
    await course.fetch_description()
    loading.delete()
    with ui.row().classes("w-full h-[10%] items-center"):
        ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl")

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
            .on_click(lambda: render_right_panel.refresh("bulletin", course))
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


async def render_recordings(course:Course):
    if not await course.fetch_files():
        ui.label("無法獲取檔案").classes("text-lg w-full")
        return

    async def on_expand(event, identifier):
        if event.args:
            await course.fetch_video(identifier)
            videos.refresh(True)

    @ui.refreshable
    def videos(content):
        if content == None:
            with ui.skeleton().classes("w-full rounded-xl flex justify-center items-center"):
                ui.spinner(size='lg')
            return

        with ui.grid(rows=1, columns=2).classes("w-full gap-8 mb-4"):
            ui.button("CH1", icon='open_in_new', on_click=lambda: ui.navigate.to("/video?channel=1", new_tab=True))\
                .classes("w-full h-full text-black bg-white")
            ui.button("CH2", icon='open_in_new', on_click=lambda: ui.navigate.to("/video?channel=2", new_tab=True))\
                .classes("w-full h-full text-black bg-white")
            # ui.video("/video?channel=1").classes("w-full h-full")
            # ui.video("/video?channel=2").classes("w-full h-full")

    with ui.scroll_area().classes("w-full h-[90%]"):
        for video in course.video_dict.values():
            with ui.expansion(f"{video["text"]}", group='group').classes("w-full border border-gray-300 rounded-lg").props('header-class="bg-gray-200 rounded-lg"') \
                .on('update:modelValue', lambda e, identifier=video["identifier"]: on_expand(e, identifier)):
                videos(None)


async def render_bulletin(course: Course):
    with ui.skeleton().classes("w-full h-[90%] rounded-xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')

    if not await course.fetch_files():
        loading.delete()
        with ui.row().classes('w-full h-[90%] justify-center items-center'):
            ui.label("無法獲取檔案").classes("text-lg")
        return
    
    loading.delete()
    bulletin = await course.get_bulletin()
    if not bulletin:
        with ui.row().classes('w-full h-[90%] justify-center items-center'):
            ui.label("無法獲取公告").classes("text-lg")
            return
        

    async def render_replies(boardid, nid):
        with ui.skeleton().classes("w-full h-[90%] rounded-xl flex justify-center items-center") as loading:
            ui.spinner(size='lg')
        reply = await course.get_bulletin_reply(nid)
        loading.delete()
        if not reply:
            with ui.row().classes('w-full justify-center items-center'):
                ui.label("無法獲取回覆").classes("text-lg")
            return

        if not reply.get(f"{boardid}|{nid}", None):
            return
        
        for data in reply[f"{boardid}|{nid}"]["data"].values():
            ui.separator()
            with ui.row().classes('w-full'):
                ui.space()
                ui.separator().props('vertical')
                with ui.column().classes('w-[90%]'):
                    ui.html(data["postcontent"])
                    title = f'{data["realname"]} ({data.get("poster", "")})    {data["postdate"]}'
                    ui.label(title).classes('w-full text-gray-600 text-right')

    with ui.scroll_area().classes('w-full h-[90%]'):
        for data in bulletin.values():
            title = data["subject"]
            caption = f'{data["realname"]} ({data.get("poster", "")})    {data["postdate"]}'
            with ui.expansion(title, caption=caption).props('switch-toggle-side header-class="bg-gray-200 rounded-lg"')\
                .classes("w-full border border-gray-300 rounded-lg") as post:
                with post.add_slot('header'):
                    with ui.row().classes("w-full items-end"):
                        ui.label(title).classes('text-xl')
                        ui.space()
                        ui.label(caption).classes('text-gray-600')
                ui.html(data["postcontent"]).classes("w-full p-6")
                await render_replies(data["boardid"], data["node"])




async def render_ischool_files(course: Course):
    with ui.skeleton().classes("w-full h-[90%] rounded-xl flex justify-center items-center") as loading:
        ui.spinner(size='lg')
    if not await course.fetch_files():
        loading.delete()
        with ui.row().classes('w-full h-[90%] justify-center items-center'):
            ui.label("無法獲取檔案").classes("text-lg")
        return
    else:
        loading.delete()

    if not course.file_tree:
        with ui.row().classes('w-full h-[90%] justify-center items-center'):
            ui.label("沒有上傳檔案").classes("text-lg")
        return

    async def on_select(e):
        """
        若非葉節點，則開啟節點
        若為葉節點，則開啟預覽
        """
        if not course.file_dict.get(e.value) or not course.file_dict[e.value].get("leaf"):
            return
        href: str = course.file_dict[e.value].get("href")
        href = href.lower()
        supported_preview_type = ['.pdf', '.txt', '.png', '.jpg', 'html']
        if (href.startswith("https://istudy.ntut.edu.tw") and any(href.endswith(suffix) for suffix in supported_preview_type))\
            or (href != "about:blank" and not href.startswith("https://istudy.ntut.edu.tw")):
            render_right_panel.refresh('file_preview', course, course.file_dict[e.value]["text"], e.value)
    
    with ui.scroll_area().classes("w-full h-full"):
        tree = ui.tree(course.file_tree, label_key='text', children_key="item", node_key='identifier', on_select=lambda e:on_select(e))\
        .classes("text-lg w-full").expand()

        body_template = r'''
        <div v-if="props.node.leaf && props.node.href !== 'about:blank'" :props="props" class="flex flex-nowrap items-start justify-between px-8 py-1 gap-2 w-full text-grey">
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
        <div class="flex items-center w-full px-4 py-1 gap-4 rounded bg-gray-200 hover:bg-gray-300"
            style="background-color: #f3f4f6 !important; /* 確保覆蓋預設樣式 */">
            <span class="flex-grow text-lg">
                {{ props.node.text }}
            </span>
            <a v-if="
                    props.node.href && props.node.href !== 'about:blank' &&
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
                :href="!props.node.href.startsWith('https://istudy.ntut.edu.tw')
                    ? props.node.href 
                    : '/file_preview?url=' + props.node.href"
                target="_blank" 
                rel="noopener noreferrer"
                @click.stop 
                class="text-sm cursor-pointer text-primary hover:text-blue-700 underline"
            >
                <q-icon name="open_in_new" size="md" /> 
                <q-tooltip>在新分頁開啟</q-tooltip>
            </a>
            
            <template v-if="props.node.href && props.node.href.startsWith('https://istudy.ntut.edu.tw') && props.node.href !== 'about:blank'">
                <a 
                    :href="'/file_download?url=' + props.node.href"
                    target="_blank" 
                    rel="noopener noreferrer"
                    @click.stop 
                    class="text-accent hover:text-green-700 cursor-pointer p-1 rounded-full"
                >
                    <q-icon name="download" size="md" /> 
                    <q-tooltip>下載檔案</q-tooltip>
                </a>
            </template>
            <template v-else>
                <span class="w-8 h-8 flex-shrink-0"></span>
            </template>
        </div>
        '''
        tree.add_slot('default-header', header_template)


async def render_preview(course: Course, page_name:str, identifier: str):

    with ui.row().classes("w-full h-[10%] items-center"):
        ui.label(f"{course.seme}_{course.name}_{course.id}").classes("text-2xl hover:underline cursor-pointer")\
            .on('click', lambda: render_right_panel.refresh("course", course))
        ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
        ui.label("i學園檔案").classes("text-2xl hover:underline cursor-pointer")\
            .on('click', lambda: render_right_panel.refresh("ischool_files", course))
        ui.icon("chevron_right").classes("text-2xl text-black bg-white").props("rounded flat")
        ui.label(page_name).classes("text-2xl")

    proxy_url: str = course.file_dict[identifier]["href"]
    ui.element('iframe').props(f'src="/file_preview?url={proxy_url}&title={page_name}"') \
        .classes('w-full h-full border-2 rounded-lg')


@ui.refreshable
async def render_right_panel(render_type: Literal["default",
                                                  "course",
                                                  "recordings",
                                                  "description",
                                                  "bulletin",
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
        await render_recordings(arg[0])

    elif render_type == "bulletin":
        render_title(arg[0], "i學園公告")
        await render_bulletin(arg[0])
        
    elif render_type == "ischool_files":
        render_title(arg[0], "i學園檔案")
        await render_ischool_files(arg[0])
    
    elif render_type == "file_preview":
        await render_preview(*arg)