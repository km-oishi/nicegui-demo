# nicegui-demo

NiceGUI を使った人体関節の 3D ビジュアライザ。

## プロジェクト構成

```
nicegui-demo/
├── main.py              # アプリ本体（UI・描画ロジック）
├── config/
│   └── config.py        # 関節名リスト・スケルトン接続定義
├── data/
│   └── 260422_trial-002-UpperBody_addAngle_v100.csv  # 関節座標データ
├── pyproject.toml
└── uv.lock
```

## データ仕様

| 項目 | 内容 |
|------|------|
| フレーム数 | 27,088 フレーム |
| 関節数 | 59 点（顔・上半身・両手指） |
| カラム | `date_time`, `{i}_x`, `{i}_y`, `{i}_z`（i = 0〜58）, 各関節角度 |
| 関節定義 | `config/config.py` の `body_name_list` 参照 |

## アプリの機能

- **3D 散布図**：59 関節を Plotly でインタラクティブに表示
  - 上半身・頭部：青　／　左手：緑　／　右手：赤
- **スケルトン描画**：顔・腕・体幹・脚・両手の指を線で接続（58 エッジ）
- **フレームスライダー**：スライダーで任意のフレームに移動
- **ホバー表示**：関節名と xyz 座標を表示

## 動かし方

### 前提

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/) がインストールされていること

### セットアップ

```bash
# 依存関係のインストール
uv sync
```

### 起動

```bash
uv run python main.py
```

ブラウザで `http://localhost:8080` を開くとアプリが表示されます。

## 依存パッケージ

| パッケージ | 用途 |
|-----------|------|
| nicegui | Web UI フレームワーク |
| plotly | 3D インタラクティブグラフ |
| pandas | CSV データ読み込み |
| numpy | 数値処理（NaN チェック等） |
