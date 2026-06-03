import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from nicegui import ui

import pages.home    # noqa: F401 - / ルートを登録
import pages.export  # noqa: F401 - /export ルートを登録

ui.run(title="関節3Dプロット", reload=False)
