from pathlib import Path

from nicegui import run, ui

from data import MAX_EXPORT_FRAMES, MP4_AVAILABLE, total_frames
from exporter import render_video


@ui.page("/export")
def export():
    state: dict = {"value": 0.0, "done": False, "path": None, "error": None}
    timer_ref: dict = {"t": None}

    with ui.column().classes("w-full items-center p-4 gap-4"):
        with ui.row().classes("w-full max-w-2xl justify-between items-center"):
            ui.label("動画エクスポート").classes("text-2xl font-bold")
            ui.link("← 3D ビジュアライザ", "/").classes("text-blue-600 underline")

        with ui.card().classes("w-full max-w-2xl"):
            ui.label("エクスポート設定").classes("text-lg font-semibold mb-2")

            with ui.grid(columns=4).classes("gap-4 items-end"):
                start_in = ui.number("開始フレーム", value=0,
                                     min=0, max=total_frames - 1, step=1)
                end_in   = ui.number("終了フレーム", value=min(99, total_frames - 1),
                                     min=0, max=total_frames - 1, step=1)
                step_in  = ui.number("フレーム間隔", value=1, min=1, max=100, step=1,
                                     ).tooltip("1 = 全フレーム、2 = 1フレームおき")
                fps_in   = ui.number("FPS", value=10, min=1, max=60, step=1)

            with ui.row().classes("items-center gap-4 mt-3"):
                ui.label("形式:").classes("font-medium")
                fmt_opts = ["GIF", "MP4"] if MP4_AVAILABLE else ["GIF"]
                fmt_radio = ui.radio(fmt_opts, value="GIF").props("inline")
                if not MP4_AVAILABLE:
                    ui.label("（MP4 は imageio-ffmpeg が必要です）").classes("text-xs text-gray-400")

            frame_count_label = ui.label("").classes("text-xs text-gray-500 mt-1")

        def update_count():
            s  = int(start_in.value or 0)
            e  = int(end_in.value or 0)
            st = max(1, int(step_in.value or 1))
            n  = len(range(s, e + 1, st))
            warn = f" ⚠️ 上限 {MAX_EXPORT_FRAMES} フレームを超えています" if n > MAX_EXPORT_FRAMES else ""
            frame_count_label.text = f"出力フレーム数: {n}{warn}"

        for inp in (start_in, end_in, step_in):
            inp.on_value_change(lambda _: update_count())
        update_count()

        status_label = ui.label("").classes("text-sm text-gray-600 max-w-2xl")
        progress_bar = ui.linear_progress(value=0).props("instant-feedback").classes("w-full max-w-2xl")
        progress_bar.visible = False
        download_btn = ui.button("📥 ダウンロード", color="green").classes("hidden")

        async def start_export():
            start    = int(start_in.value)
            end      = int(end_in.value)
            step     = max(1, int(step_in.value))
            fps      = max(1, int(fps_in.value))
            fmt      = fmt_radio.value
            n_frames = len(range(start, end + 1, step))

            if start >= end:
                ui.notify("開始フレームは終了フレームより小さくしてください", type="warning")
                return
            if n_frames > MAX_EXPORT_FRAMES:
                ui.notify(f"フレーム数が上限（{MAX_EXPORT_FRAMES}）を超えています。間隔を広げてください", type="warning")
                return

            state.update({"value": 0.0, "done": False, "path": None, "error": None})
            export_btn.props("disabled")
            download_btn.classes(add="hidden")
            progress_bar.visible = True
            progress_bar.set_value(0)
            status_label.text = f"レンダリング中… 0 / {n_frames} フレーム"

            def poll():
                v = state["value"]
                progress_bar.set_value(v)
                status_label.text = f"レンダリング中… {int(v * n_frames)} / {n_frames} フレーム"
                if state["done"]:
                    if timer_ref["t"]:
                        timer_ref["t"].cancel()
                    export_btn.props(remove="disabled")
                    if state.get("error"):
                        progress_bar.set_value(0)
                        status_label.text = f"❌ エラー: {state['error']}"
                    else:
                        progress_bar.set_value(1.0)
                        status_label.text = "✅ 完成！ダウンロードボタンを押してください。"
                        if state["path"]:
                            download_btn.classes(remove="hidden")

            timer_ref["t"] = ui.timer(0.5, poll)

            try:
                await run.io_bound(render_video, start, end, step, fps, fmt, state)
            except Exception as e:
                state["error"] = str(e)
                state["done"] = True

        export_btn = ui.button("▶ 変換開始", on_click=start_export).props("color=primary")

        def do_download():
            path: Path = state["path"]
            if path and path.exists():
                fmt      = fmt_radio.value
                filename = f"skeleton_export.{'gif' if fmt == 'GIF' else 'mp4'}"
                with open(path, "rb") as f:
                    ui.download(f.read(), filename=filename)

        download_btn.on_click(do_download)
