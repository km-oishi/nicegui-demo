import numpy as np
import plotly.graph_objects as go

from config import ALL_CONNECTIONS, body_name_list
from data import N_JOINTS, coords_np, times_np

_JOINT_COLORS = ['#4A90D9'] * 17 + ['#27AE60'] * 21 + ['#E74C3C'] * 21


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
    scatter = go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers',
        marker=dict(size=5, color=_JOINT_COLORS, opacity=0.9),
        text=body_name_list[:N_JOINTS],
        hovertemplate='<b>%{text}</b><br>x=%{x:.3f}<br>y=%{y:.3f}<br>z=%{z:.3f}<extra></extra>',
        name='Joints',
    )

    title = f'Frame {frame_idx}  |  time = {time_val:.3f} s' if not np.isnan(time_val) else f'Frame {frame_idx}'
    fig = go.Figure(data=[lines, scatter])
    fig.update_layout(
        title=dict(text=title, x=0.5),
        scene=dict(
            xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig
