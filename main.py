from nicegui import ui

ui.label("Hello")
ui.button("Click me", on_click=lambda: ui.notify("clicked"))
ui.run()
