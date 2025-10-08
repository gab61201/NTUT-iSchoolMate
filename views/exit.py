from nicegui import ui

@ui.page('/exit', title='離開')
async def exit_page():
    with ui.column().classes('w-full h-[calc(100vh-32px)] justify-center items-center'):
        with ui.card().classes('w-96 p-8 rounded-2xl justify-center items-center'):
            ui.label('已關閉').classes('text-2xl font-bold text-center w-full mb-4')
