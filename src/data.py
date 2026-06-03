import numpy as np
import pandas as pd

DATA_PATH = "data/260422_trial-002-UpperBody_addAngle_v100.csv"
N_JOINTS = 59
MAX_EXPORT_FRAMES = 500

df = pd.read_csv(DATA_PATH)
total_frames = len(df)

_coord_cols = [f"{i}_{c}" for i in range(N_JOINTS) for c in ("x", "y", "z")]
coords_np: np.ndarray = df[_coord_cols].values.reshape(total_frames, N_JOINTS, 3)
times_np: np.ndarray = pd.to_numeric(df["date_time"], errors="coerce").values

try:
    import imageio_ffmpeg  # noqa: F401
    MP4_AVAILABLE = True
except ImportError:
    MP4_AVAILABLE = False
