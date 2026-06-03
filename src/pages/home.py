from nicegui import ui

from data import total_frames
from visualizer import build_plotly_figure


@ui.page("/")
def home():
    with ui.column().classes("w-full items-center p-4 gap-4"):
        with ui.row().classes("w-full max-w-5xl justify-between items-center"):
            ui.label("人体関節 3D ビジュアライザ").classes("text-2xl font-bold")
            ui.link("🎬 動画エクスポート →", "/export").classes("text-blue-600 underline")

        frame_label = ui.label(f"0 / {total_frames - 1}").classes("text-sm text-gray-500")
        plot = ui.plotly(build_plotly_figure(0)).classes("w-full").style("height: 720px")

        def on_frame_change(e):
            idx = int(e.value)
            frame_label.text = f"Frame {idx} / {total_frames - 1}"
            plot.update_figure(build_plotly_figure(idx))

        ui.slider(
            min=0, max=total_frames - 1, value=0, step=1, on_change=on_frame_change
        ).classes("w-full max-w-5xl")
