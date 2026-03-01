# Phase 1: 環境セットアップ

!!! info "所要時間"
    約10分

---

## 🎯 学習目標

- Python 仮想環境を作成する
- 必要なパッケージをインストールする
- プロジェクト構成をセットアップする

---

## 📋 前提条件

| 要件 | 説明 |
|------|------|
| Python 3.11 以上 | インストール済みであること |
| コードエディター | VS Code 推奨 |
| ターミナル / コマンドライン | アクセスできること |
| GitHub アカウント | 作成済みであること |

---

## 🐍 ステップ 1: Python のバージョン確認

Python がインストールされていることを確認します。

```bash
python --version
```

!!! warning "重要"
    Python **3.11 以上** が必要です。バージョンが古い場合は、[python.org](https://www.python.org/downloads/) から最新版をインストールしてください。

---

## 📁 ステップ 2: プロジェクトディレクトリの作成

ワークショップ用のディレクトリを作成し、移動します。

```bash
mkdir cogbot-handson && cd cogbot-handson
```

---

## 🏗️ ステップ 3: 仮想環境の作成

Python の仮想環境を作成します。

```bash
python -m venv .venv
```

作成した仮想環境を有効化します。

=== "macOS / Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows (PowerShell)"

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

!!! warning "PowerShell で実行ポリシーエラーが出る場合"
    PowerShell のスクリプト実行が制限されている場合があります。以下のコマンドで一時的に許可してください。

    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

!!! tip "ヒント"
    仮想環境が有効化されると、ターミナルのプロンプトに `(.venv)` と表示されます。

---

## 📦 ステップ 4: requirements.txt の作成

依存パッケージの一覧ファイルを作成します。

=== "macOS / Linux"

    ```bash
    touch requirements.txt
    ```

=== "Windows (PowerShell)"

    ```powershell
    New-Item requirements.txt
    ```

作成した `requirements.txt` に、以下の内容を記述してください。

```text
agent-framework==1.0.0rc2
chainlit>=2.9.6
python-dotenv>=1.2.1
httpx>=0.28.1
opentelemetry-semantic-conventions-ai==0.4.13
```

---

## ⬇️ ステップ 5: 依存パッケージのインストール

パッケージをインストールします。

=== "pip"

    ```bash
    pip install -r requirements.txt
    ```

=== "uv"

    ```bash
    uv pip install -r requirements.txt
    ```

!!! tip "ヒント"
    `uv` は高速なパッケージインストーラーです。未インストールの場合は `pip` を使用してください。

---

## 🔑 ステップ 6: 環境変数ファイルの作成

API キーなどの秘密情報を管理するための `.env` ファイルを作成します。

=== "macOS / Linux"

    ```bash
    touch .env
    ```

=== "Windows (PowerShell)"

    ```powershell
    New-Item .env
    ```

作成した `.env` ファイルに、以下のテンプレートを記述してください。

```bash
MSF_MODEL_API_VERSIOn=2025-04-01-preview
MSF_MODEL_ENDPOINT=
MSF_MODEL_API_KEY=
MSF_MODEL_DEPLOYMENT_NAME=

WEATHER_API_KEY=your_key_here
```

※ WEATHER_API_KEY は Phase 5 で使用しますので、それまではこの値で OK です。

## ステップ 7: .gitignore の作成

前のステップで作成した `.env` ファイルには秘密情報が含まれます。**Git にコミットしないよう** Python の汎用の `.gitignore` を作成し `.env` がコミットに含まれないようにします。

=== "macOS / Linux"

    ```bash
    curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
    ```

=== "Windows (PowerShell)"

    ```powershell
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore" -OutFile ".gitignore"
    ```

## 📂 プロジェクト構成の確認

ここまでの手順が完了すると、プロジェクトは以下の構成になります。

```text
cogbot-handson/
├── .venv/
├── .env
├── .gitignore
└── requirements.txt
```

---

## ✅ チェックポイント

以下を確認します：

- [x] Python 3.11 以上がインストールされている
- [x] プロジェクトディレクトリが作成されている
- [x] 仮想環境が作成・有効化されている
- [x] `requirements.txt` が作成されている
- [x] 依存パッケージがインストールされている
- [x] `.env` ファイルが作成されている
- [x] `.gitignore` ファイルが作成されている

---

## ❓ よくあるトラブルと解決方法

??? tip "Python が見つからない (`python: command not found`)"
    Python がインストールされていないか、PATH に追加されていない可能性があります。

    - [python.org](https://www.python.org/downloads/) から Python 3.11 以上をインストールしてください。
    - インストール時に **「Add Python to PATH」** にチェックを入れてください。
    - インストール後、ターミナルを再起動してから再度お試しください。

??? tip "pip が見つからない (`pip: command not found`)"
    `pip` の代わりに以下を試してください。

    ```bash
    python -m pip install -r requirements.txt
    ```

??? tip "仮想環境が有効化できない（PowerShell 実行ポリシー）"
    PowerShell でスクリプトの実行が制限されている場合は、以下のコマンドを実行してください。

    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

    その後、再度仮想環境の有効化を試してください。

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

---

## 🌞 NEXT STEP 🌞

環境セットアップが完了しました！次は Microsoft Foundry のモデルの設定に進みましょう。

[Phase 2: Microsoft Foundry models🏃‍♂️‍➡️:material-arrow-right:](02-microsoft-foundry-models.md){ .md-button }
