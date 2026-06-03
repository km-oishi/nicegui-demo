import sys
sys.path.insert(0, '.')

import matplotlib
matplotlib.use('Agg')  # インタラクティブバックエンドを使わない（スレッド内レンダリング用）

import tempfile
from pathlib import Path

import imageio.v2 as iio
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (3D projection の登録に必要)
from nicegui import app, run, ui

from config.config import ALL_CONNECTIONS, body_name_list

# ------------------------------------------------------------------ #
# データ読み込み・前処理
# ------------------------------------------------------------------ #
DATA_PATH = "data/260422_trial-002-UpperBody_addAngle_v100.csv"
df = pd.read_csv(DATA_PATH)
total_frames = len(df)
N_JOINTS = 59

# 全フレームの座標を numpy 配列に変換（shape: frames × joints × 3）
_coord_cols = [f"{i}_{c}" for i in range(N_JOINTS) for c in ("x", "y", "z")]
coords_np: np.ndarray = df[_coord_cols].values.reshape(total_frames, N_JOINTS, 3)
times_np: np.ndarray = df["date_time"].values

MAX_EXPORT_FRAMES = 500  # エクスポート上限フレーム数

# MP4 可否チェック
try:
    import imageio_ffmpeg  # noqa: F401
    MP4_AVAILABLE = True
except ImportError:
    MP4_AVAILABLE = False


# ------------------------------------------------------------------ #
# Plotly 図（3D ビジュアライザ用）
# ------------------------------------------------------------------ #
def build_plotly_figure(frame_idx: int) -> go.Figure:
    data = coords_np[frame_idx]  # (59, 3)
    xs, ys, zs = data[:, 0].tolist(), data[:, 1].tolist(), data[:, 2].tolist()
    time_val = times_np[frame_idx]

    lx, ly, lz = [], [], []
    for a, b in ALL_CONNECTIONS:
        if not (np.isnan(xs[a]) or np.isnan(xs[b])):
            lx.extend([xs[a], xs[b], None])
            ly.extend([ys[a], ys[b], None])
            lz.extend([zs[a], zs[b], None])

    lines = go.Scatter3d(
        x=lx, y=ly, z=lz,
        mode='lines',
        line=dict(color='rgba(120,120,120,0.6)', width=2),
        hoverinfo='skip',
        name='Skeleton',
    )
    colors = ['#4A90D9'] * 17 + ['#27AE60'] * 21 + ['#E74C3C'] * 21
    scatter = go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers',
        marker=dict(size=5, color=colors, opacity=0.9),
        text=body_name_list[:N_JOINTS],
        hovertemplate='<b>%{text}</b><br>x=%{x:.3f}<br>y=%{y:.3f}<br>z=%{z:.3f}<extra></extra>',
        name='Joints',
    )
    fig = go.Figure(data=[lines, scatter])
    fig.update_layout(
        title=dict(text=f'Frame {frame_idx}  |  time = {time_val:.3f} s', x=0.5),
        scene=dict(
            xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


# ------------------------------------------------------------------ #
# 動画レンダリング（バックグラウンドスレッド内で実行）
# ------------------------------------------------------------------ #
def render_video(
    start: int,
    end: int,
    step: int,
    fps: int,
    fmt: str,
    progress_dict: dict,
) -> Path:
    """matplotlib で各フレームを描画し、動画ファイルを生成して Path を返す。"""
    frame_indices = list(range(start, end + 1, step))
    total = len(frame_indices)

    # エクスポート範囲をサンプリングして軸範囲を計算（全フレームは重いため間引く）
    sample_idx = frame_indices[:: max(1, total // 20)]
    sample_coords = coords_np[sample_idx].reshape(-1, 3)
    valid = sample_coords[~np.isnan(sample_coords).any(axis=1)]
    x_lim = (float(valid[:, 0].min()), float(valid[:, 0].max()))
    y_lim = (float(valid[:, 1].min()), float(valid[:, 1].max()))
    z_lim = (float(valid[:, 2].min()), float(valid[:, 2].max()))

    suffix = ".gif" if fmt == "GIF" else ".mp4"
    out_path = Path(tempfile.mktemp(suffix=suffix))

    writer = iio.get_writer(str(out_path), fps=fps)

    fig = Figure(figsize=(8, 6), dpi=80)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111, projection="3d")

    try:
        for i, frame_idx in enumerate(frame_indices):
            ax.cla()

            data = coords_np[frame_idx]
            xs, ys, zs = data[:, 0], data[:, 1], data[:, 2]

            # スケルトン
            for a, b in ALL_CONNECTIONS:
                if not (np.isnan(xs[a]) or np.isnan(xs[b])):
                    ax.plot(
                        [xs[a], xs[b]], [ys[a], ys[b]], [zs[a], zs[b]],
                        color="gray", linewidth=0.8, alpha=0.6,
                    )

            # 関節点（部位ごとに色分け）
            for indices, color in [
                (range(17), "#4A90D9"),
                (range(17, 38), "#27AE60"),
                (range(38, 59), "#E74C3C"),
            ]:
                idx = np.array(list(indices))
                mask = ~np.isnan(xs[idx])
                ax.scatter(xs[idx[mask]], ys[idx[mask]], zs[idx[mask]],
                           c=color, s=15, depthshade=True)

            ax.set_xlim(x_lim)
            ax.set_ylim(y_lim)
            ax.set_zlim(z_lim)
            ax.set_title(f"Frame {frame_idx} | t={times_np[frame_idx]:.3f}s", fontsize=9)
            ax.set_xlabel("X", fontsize=7)
            ax.set_ylabel("Y", fontsize=7)
            ax.set_zlabel("Z", fontsize=7)

            canvas.draw()
            # buffer_rgba() でメモリコピーなし numpy 変換、RGB に変換して書き出し
            arr = np.asarray(canvas.buffer_rgba())[:, :, :3]
            writer.append_data(arr)

            progress_dict["value"] = (i + 1) / total
    finally:
        writer.close()

    progress_dict["done"] = True
    progress_dict["path"] = out_path
    return out_path


# ================================================================== #
# ページ定義
# ================================================================== #

@ui.page("/")
def main_page():
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


@ui.page("/export")
def export_page():
    # ページインスタンスごとの状態
    state = {"value": 0.0, "done": False, "path": None, "running": False}
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
            s = int(start_in.value or 0)
            e = int(end_in.value or 0)
            st = max(1, int(step_in.value or 1))
            n = len(range(s, e + 1, st))
            warn = f" ⚠️ 上限 {MAX_EXPORT_FRAMES} フレームを超えています" if n > MAX_EXPORT_FRAMES else ""
            frame_count_label.text = f"出力フレーム数: {n}{warn}"

        for inp in (start_in, end_in, step_in):
            inp.on_value_change(lambda _: update_count())
        update_count()

        status_label   = ui.label("").classes("text-sm text-gray-600 max-w-2xl")
        progress_bar   = ui.linear_progress(value=0).props("instant-feedback").classes("w-full max-w-2xl")
        progress_bar.visible = False
        download_btn   = ui.button("📥 ダウンロード", color="green").classes("hidden")

        async def start_export():
            start = int(start_in.value)
            end   = int(end_in.value)
            step  = max(1, int(step_in.value))
            fps   = max(1, int(fps_in.value))
            fmt   = fmt_radio.value
            n_frames = len(range(start, end + 1, step))

            if start >= end:
                ui.notify("開始フレームは終了フレームより小さくしてください", type="warning")
                return
            if n_frames > MAX_EXPORT_FRAMES:
                ui.notify(f"フレーム数が上限（{MAX_EXPORT_FRAMES}）を超えています。間隔を広げてください", type="warning")
                return

            state.update({"value": 0.0, "done": False, "path": None, "running": True})
            export_btn.props("disabled")
            download_btn.classes(add="hidden")
            progress_bar.visible = True
            progress_bar.set_value(0)
            status_label.text = f"レンダリング中… 0 / {n_frames} フレーム"

            def poll():
                v = state["value"]
                progress_bar.set_value(v)
                done_n = int(v * n_frames)
                status_label.text = f"レンダリング中… {done_n} / {n_frames} フレーム"
                if state["done"]:
                    if timer_ref["t"]:
                        timer_ref["t"].cancel()
                    progress_bar.set_value(1.0)
                    status_label.text = "✅ 完成！ダウンロードボタンを押してください。"
                    export_btn.props(remove="disabled")
                    if state["path"]:
                        download_btn.classes(remove="hidden")

            timer_ref["t"] = ui.timer(0.5, poll)

            await run.io_bound(render_video, start, end, step, fps, fmt, state)

        export_btn = ui.button("▶ 変換開始", on_click=start_export).props("color=primary")

        def do_download():
            path: Path = state["path"]
            if path and path.exists():
                fmt = fmt_radio.value
                filename = f"skeleton_export.{'gif' if fmt == 'GIF' else 'mp4'}"
                with open(path, "rb") as f:
                    ui.download(f.read(), filename=filename)

        download_btn.on_click(do_download)


ui.run(title="関節3Dプロット", reload=False)


