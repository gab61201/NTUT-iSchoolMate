from nicegui import app, ui
from .home_tab import render_home_tab
from .search_empty_classroom import render_search_empty_classroom


@ui.page('/home', title='NTUT iSchoolMate')
async def home_route():
    user = getattr(app, 'user')
    ui.add_head_html('<style>body { background-color: #f3f4f6 !important; }</style>')

    with ui.left_drawer().props('width=180'):
        with ui.tabs().classes('w-full text-gray-600')\
            .props("vertical indicator-color=transparent active-color=blue-9 active-bg-color=sky-100") as tabs:
            ui.tab('home_tab', '首頁').classes("text-lg rounded-md")#.style("border-radius: 100000px;")
            ui.tab('course_list_tab', '課程清單').classes("text-lg rounded-md")
            ui.tab('course_search_tab', '課程查詢').classes("text-lg rounded-md")
            ui.tab('search_empty_classroom', '找空教室').classes("text-lg rounded-md")
            ui.tab('schedule_tab', '行事曆').classes("text-lg rounded-md")
            ui.tab('student_info_tab', '個人資訊').classes("text-lg rounded-md")


    with ui.tab_panels(tabs, animated=False, value='home_tab')\
    .classes('w-full h-[calc(100vh-32px)] bg-gray-200 shadow-lg').props("vertical") as panel:
        with ui.tab_panel('home_tab').classes('p-0'):
            render_home_tab(user)
        with ui.tab_panel('course_list_tab'):
            ui.label('2')
        with ui.tab_panel('course_search_tab'):
            ui.label('3')
        with ui.tab_panel('search_empty_classroom').classes('p-0'):
            render_search_empty_classroom()
        with ui.tab_panel('schedule_tab'):
            ui.label('5')
        with ui.tab_panel('student_info_tab'):
            ui.label('6')
