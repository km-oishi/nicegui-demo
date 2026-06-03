import matplotlib
matplotlib.use('Agg')  # スレッド内レンダリング用（他の matplotlib インポートより前に必要）

import tempfile
from pathlib import Path

import imageio.v2 as iio
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (3D projection の登録に必要)

from config import ALL_CONNECTIONS
from data import N_JOINTS, coords_np, times_np

_REGION_COLORS = [
    (range(17),     '#4A90D9'),  # 上半身・頭部
    (range(17, 38), '#27AE60'),  # 左手
    (range(38, 59), '#E74C3C'),  # 右手
]


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

    # エクスポート範囲をサンプリングして軸範囲を固定（全フレーム走査を避ける）
    sample_idx = frame_indices[:: max(1, total // 20)]
    sample_coords = coords_np[sample_idx].reshape(-1, 3)
    valid = sample_coords[~np.isnan(sample_coords).any(axis=1)]
    x_lim = (float(valid[:, 0].min()), float(valid[:, 0].max()))
    y_lim = (float(valid[:, 1].min()), float(valid[:, 1].max()))
    z_lim = (float(valid[:, 2].min()), float(valid[:, 2].max()))

    suffix = ".gif" if fmt == "GIF" else ".mp4"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    out_path = Path(tmp.name)
    tmp.close()

    try:
        writer = iio.get_writer(str(out_path), fps=fps)

        fig = Figure(figsize=(8, 6), dpi=80)
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111, projection="3d")

        try:
            for i, frame_idx in enumerate(frame_indices):
                ax.cla()

                data = coords_np[frame_idx]
                xs, ys, zs = data[:, 0], data[:, 1], data[:, 2]

                for a, b in ALL_CONNECTIONS:
                    if not (np.isnan(xs[a]) or np.isnan(xs[b])):
                        ax.plot(
                            [xs[a], xs[b]], [ys[a], ys[b]], [zs[a], zs[b]],
                            color="gray", linewidth=0.8, alpha=0.6,
                        )

                for indices, color in _REGION_COLORS:
                    idx = np.array(list(indices))
                    mask = ~np.isnan(xs[idx])
                    ax.scatter(xs[idx[mask]], ys[idx[mask]], zs[idx[mask]],
                               c=color, s=15, depthshade=True)

                ax.set_xlim(x_lim)
                ax.set_ylim(y_lim)
                ax.set_zlim(z_lim)
                t = times_np[frame_idx]
                ax.set_title(
                    f"Frame {frame_idx} | t={t:.3f}s" if not np.isnan(t) else f"Frame {frame_idx}",
                    fontsize=9,
                )
                ax.set_xlabel("X", fontsize=7)
                ax.set_ylabel("Y", fontsize=7)
                ax.set_zlabel("Z", fontsize=7)

                canvas.draw()
                arr = np.asarray(canvas.buffer_rgba())[:, :, :3]
                writer.append_data(arr)

                progress_dict["value"] = (i + 1) / total
        finally:
            writer.close()

        progress_dict["done"] = True
        progress_dict["path"] = out_path

    except Exception as e:
        progress_dict["error"] = str(e)
        progress_dict["done"] = True

    return out_path
