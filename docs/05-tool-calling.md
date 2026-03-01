# 🔧 Phase 5: エージェントにツールを追加する

!!! info "所要時間"
    約20分

## 🎯 学習目標

- 関数定義を使って tools を作成する
- エージェントに tools を追加する
- UI で Tool calling (ツール呼び出し) を処理する
- チャットでリアルタイムの天気データを確認する

---

## 🤔 ツール呼び出しとは？

ツール呼び出し（Tool Calling）とは、エージェントが外部の関数や API を呼び出して情報を取得する仕組みです。以下のフローで動作します：

```text
ユーザーが質問する
       ↓
エージェントが考える（ツールが必要か判断）
       ↓
エージェントが行動する（ツールを呼び出す）
       ↓
ツールが結果を返す
       ↓
エージェントが応答する（結果を自然言語にまとめる）
```

例えば、「東京の天気は？」と聞くと、エージェントは `get_weather` ツールを呼び出し、リアルタイムの天気データを取得して回答します。

---

## 📁 ステップ 1: プロジェクトフォルダの作成

phase-03 ディレクトリにいる場合は、`cd ..` でワークスペースのルートに戻りましょう。
そして以下のコマンドを実行します。

=== "macOS / Linux"

    ```bash
    mkdir -p phase-05
    cd phase-05
    touch app.py tools.py
    ```

=== "Windows (PowerShell)"

    ```powershell
    mkdir phase-05
    cd phase-05
    New-Item app.py, tools.py
    ```

ここまでの手順が完了すると、プロジェクトは以下の構成になります。

```text
cogbot-handson/
├── .venv/
├── phase-02/
├── phase-03/
├── phase-04/
├── phase-05/
|     └── app.py
|     └── tools.py
├── .env
├── .gitignore
└── requirements.txt
```

---

## 🔑 ステップ 2: Weather API キーを取得する

!!! tip "ヒント"
    [weatherapi.com](https://www.weatherapi.com/) で無料アカウントを作成し、API キーを取得してください。無料プランで十分です。

`.env` ファイルに以下を追加します：

```env
WEATHER_API_KEY=your_api_key_here
```

---

## 🛠️ ステップ 3: tools.py の作成

天気情報を取得するツール関数を作成します。

```python
import os
from typing import Annotated
import httpx
from pydantic import Field


def get_weather(
    city: Annotated[str, Field(description="The name of the city (e.g., 'London', 'Tokyo')")]
) -> str:
    """
    指定された都市の現在の天気を取得します。

    気温、天候、湿度などの情報を返します。
    """
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return "エラー: .env に WEATHER_API_KEY が設定されていません"

    try:
        response = httpx.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": api_key, "q": city},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]

        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C
☁️ Condition: {condition}
💧 Humidity: {humidity}%"""

    except httpx.HTTPStatusError:
        return f"'{city}' の天気情報を取得できませんでした"
    except Exception as e:
        return f"エラー: {e}"


# エージェントに渡すツールのリスト
TOOLS = [get_weather]
```

### ツール定義の解説

| 要素 | 目的 |
|------|------|
| `Annotated[str, Field(...)]` | LLM にパラメータを説明 |
| ドキュメント文字列 | LLM がツールの使用タイミングを判断するために読む |
| 戻り値の文字列 | エージェントが受け取る結果 |

---
## 🚀 ステップ 4: app.py の作成

ツール呼び出しに対応した `Agent` を作成します。

```python
import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from tools import TOOLS

load_dotenv(override=True)

SYSTEM_PROMPT = f"""あなたは、Aria という名の役に立つ AI アシスタントです。

あなたのできること：
- あらゆるトピックに関する質問に答える
- コーディングや技術的な問題のサポート
- 説明と分析を提供する
- フレンドリーで会話的な態度

ガイドライン：
- 簡潔かつ綿密に伝える
- わからないことがあれば認める
- 必要に応じて、より明確な質問をする

現在時刻: {date.today().strftime("%B %d, %Y")}
"""


def get_chat_client():
    """Azure OpenAI Chat クライアント"""
    return AzureOpenAIChatClient(
        endpoint=os.environ["MSF_MODEL_ENDPOINT"],
        api_key=os.environ["MSF_MODEL_API_KEY"],
        api_version=os.environ["MSF_MODEL_API_VERSION"],
        deployment_name=os.environ["MSF_MODEL_DEPLOYMENT_NAME"]
    )


def create_agent():
    """設定済みの Agent を作成"""
    chat_client = get_chat_client()
    # Agent を作成
    agent: Agent = chat_client.as_agent(
        name="Aria",
        description="天気予報の機能を備えた便利なAIアシスタント",
        instructions=SYSTEM_PROMPT,
        tools=TOOLS,  # ツールを追加
        default_options={
            # "temperature": 0.7,
            "max_completion_tokens": 3000,
            "reasoning_effort": "none" # reasoning model で指定可能
        }
    )

    return agent


@cl.on_chat_start
async def start():
    """チャットセッションを初期化"""
    agent = create_agent()
    session = agent.create_session()

    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)

    await cl.Message(content="👋 こんにちは🌞Aria です。天気を調べられます！例えば「パリの天気は？」と聞いてみてください！").send()


@cl.on_message
async def main(message: cl.Message):
    agent: Agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")

    msg = cl.Message(content="")

    stream = agent.run(message.content, stream=True, session=session)
    async for update in stream:
        if update.text:
            await msg.stream_token(update.text)

    await stream.get_final_response()  # 会話履歴を session に自動保存
    await msg.send()

```

### 🔑 主な変更点

- `tools.py`: 天気予報の API を呼ぶ関数の実装
- `tools=TOOLS`: Agent の初期化時に tools を指定

---

## ▶️ ステップ 5: 実行とテスト

アプリを起動します：

```bash
chainlit run app.py -w
```

「東京の天気は？」「パリとシアトルの天気は」などの質問で tools を使って正しく回答できるか確認しましょう。

---

## 🚀 ステップ 6: Tool calling の状況をストリーミング

Tool calling の開始時と結果を出力するよう `Agent` を更新します。コードの全体は以下になります。

```python
import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent, Content
from agent_framework.azure import AzureOpenAIChatClient
from tools import TOOLS

load_dotenv(override=True)

SYSTEM_PROMPT = f"""あなたは、Aria という名の役に立つ AI アシスタントです。

あなたのできること：
- あらゆるトピックに関する質問に答える
- コーディングや技術的な問題のサポート
- 説明と分析を提供する
- フレンドリーで会話的な態度

ガイドライン：
- 簡潔かつ綿密に伝える
- わからないことがあれば認める
- 必要に応じて、より明確な質問をする

現在時刻: {date.today().strftime("%B %d, %Y")}
"""


def get_chat_client():
    """Azure OpenAI Chat クライアント"""
    return AzureOpenAIChatClient(
        endpoint=os.environ["MSF_MODEL_ENDPOINT"],
        api_key=os.environ["MSF_MODEL_API_KEY"],
        api_version=os.environ["MSF_MODEL_API_VERSION"],
        deployment_name=os.environ["MSF_MODEL_DEPLOYMENT_NAME"]
    )


def create_agent():
    """設定済みの Agent を作成"""
    chat_client = get_chat_client()
    # Agent を作成
    agent: Agent = chat_client.as_agent(
        name="Aria",
        description="天気予報の機能を備えた便利なAIアシスタント",
        instructions=SYSTEM_PROMPT,
        tools=TOOLS,  # ツールを追加
        default_options={
            # "temperature": 0.7,
            "max_completion_tokens": 3000,
            "reasoning_effort": "none" # reasoning model で指定可能
        }
    )

    return agent


@cl.on_chat_start
async def start():
    """チャットセッションを初期化"""
    agent = create_agent()
    session = agent.create_session()

    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)

    await cl.Message(content="👋 こんにちは🌞Aria です。天気を調べられます！例えば「パリの天気は？」と聞いてみてください！").send()


@cl.on_message
async def main(message: cl.Message):
    agent: Agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")

    msg = cl.Message(content="")
    tool_steps = {}

    stream = agent.run(message.content, stream=True, session=session)
    async for update in stream:
        # Tool calling のストリーミング
        if update.contents:
            for content in update.contents:
                # Tool calling 開始時
                if isinstance(content, Content) and content.type == "function_call":
                    if content.name and content.call_id not in tool_steps:
                        tool_steps[content.call_id] = cl.Message(content=f"🔧 ツールを呼び出し中: {content.name}...")
                        step = cl.Step(
                            name=f"🔧 {content.name}",
                            type="tool"
                        )
                        await step.send()
                        tool_steps[content.call_id] = step
                # Tool calling 後の結果
                elif isinstance(content, Content) and content.type == "function_result":
                    if content.call_id in tool_steps:
                        step = tool_steps[content.call_id]
                        step.output = str(content.result)
                        await step.update()
        # テキストの応答のストリーミング
        if update.text:
            await msg.stream_token(update.text)

    await stream.get_final_response()  # 会話履歴を session に自動保存
    await msg.send()

```

### 🔑 主な変更点

- `if isinstance(content, Content) and content.type == "function_call":`: tool calling 開始時のチェック
- `elif isinstance(content, Content) and content.type == "function_result":`: tool calling の結果をチェック
- `content.call_id`: tool step 追跡用の一意な識別子
- `tool_steps`: `call_id` をキーにステップ参照を保存

---

## ▶️ ステップ 6: 実行とテスト

アプリを起動していない場合は起動します：

```bash
chainlit run app.py -w
```

### テストシナリオ

**テスト 1: 天気（ツール使用）**

```
あなた: ロンドンの天気は？
[ツールステップ表示]
Aria: ロンドンの天気は7°Cで曇りです...
```

**テスト 2: 天気以外（ツールなし）**

```
あなた: Pythonとは？
Aria: Python はプログラミング言語で...
（ツール呼び出しなし）
```

**テスト 3: 複数都市**

```
あなた: 東京とシドニーの天気を比較して
[2つのツール呼び出し]
Aria: 東京は8°C、シドニーは22°C...
```

---

## 📄 完成コード

??? example "完成コード: tools.py（クリックで展開）"

    ```python
    --8<-- "solutions/phase-05/tools.py"
    ```

??? example "完成コード: app.py（クリックで展開）"

    ```python
    --8<-- "solutions/phase-05/app.py"
    ```

---

## 💡 ポイント

- **ツールは普通の Python 関数**: 型ヒントとドキュメント文字列で LLM が使い方を理解します
- **エージェントが判断する**: どのツールをいつ使うかはエージェントが自動的に決定します
- **`call_id`**: 複数のツール呼び出しを正しく追跡するための識別子です

---

## ✅ チェックポイント

以下を確認してください：

- [x] `tools.py` に `get_weather` 関数が定義されている
- [x] `app.py` でエージェントにツールが追加されている
- [x] 天気の質問でツールが呼び出される
- [x] 天気以外の質問にはツールなしで回答される
- [x] 複数都市の天気を比較できる
- [x] UI にツールステップが表示される

---

## ❗ よくある問題

| 問題 | 解決方法 |
|------|----------|
| `WEATHER_API_KEY` エラー | `.env` ファイルに正しい API キーが設定されているか確認 |
| 天気データが取得できない | API キーが有効か、都市名が正しいか確認 |
| ツールが呼び出されない | システムプロンプトにツールの説明が含まれているか確認 |
| `ImportError` | `pip install httpx pydantic` で必要なパッケージをインストール |

---

次のステップ: [Phase 6: MCP 連携](06-mcp-integration.md)
