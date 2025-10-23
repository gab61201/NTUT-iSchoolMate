from nicegui import ui


def render_search_empty_classroom():
    with ui.row().classes('w-full h-full p-0 justify-between'):
        with ui.grid(columns='minmax(0, 1fr)'+' 2fr'*7 , rows='1fr'+' 2fr'*12).classes('w-[49%] h-full gap-1 p-0'):
            for days in ['', '日', '一', '二', '三', '四', '五', '六']:
                with ui.card().classes('w-full h-full justify-center items-center'):
                    ui.label(days)
            
            for row in range(1, 13):
                with ui.card().classes('w-full h-full justify-center items-center'):
                    ui.label(str(row))
                for column in range(1, 8):
                    ui.button().classes('w-full h-full')

        with ui.card().classes('w-[49%] h-full'):
            ui.label('123')