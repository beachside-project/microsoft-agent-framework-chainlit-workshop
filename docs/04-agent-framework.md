# 🤖 Phase 4: Microsoft Agent Framework を理解する

!!! info "所要時間"
    約15分

## 🎯 学習目標

- Agent class のアーキテクチャを理解する
- セッションとメッセージ管理について学ぶ
- エージェントのパラメータを設定する
- tools との統合の準備をする

---

## 🧠 Microsoft Agent Framework とは？

Microsoft Agent Framework は、AI エージェントを構築するためのオープンソースフレームワークです。エージェントは以下のループで動作します：

```
┌─────────────────────────────────────────┐
│           エージェントループ              │
│                                         │
│   🤔 Think (考える)                     │
│      ↓                                  │
│   🛠️ Act (行動する)                     │
│      ↓                                  │
│   👀 Observe (観察する)                  │
│      ↓                                  │
│   🔄 Repeat (繰り返す)                  │
│                                         │
│   Think → Act → Observe → Repeat        │
└─────────────────────────────────────────┘
```

このフレームワークを使うことで、LLM を直接呼び出す代わりに、構造化されたエージェントパターンを活用できます。

---

## 📁 ステップ 1: プロジェクトフォルダの作成

phase-03 ディレクトリにいる場合は、`cd ..` でワークスペースのルートに戻りましょう。
そして以下のコマンドを実行します。

=== "macOS / Linux"

    ```bash
    mkdir -p phase-04
    cd phase-04
    touch app.py
    ```

=== "Windows (PowerShell)"

    ```powershell
    mkdir phase-04
    cd phase-04
    New-Item app.py
    ```

ここまでの手順が完了すると、プロジェクトは以下の構成になります。

```text
cogbot-handson/
├── .venv/
├── phase-02/
├── phase-03/
├── phase-04/
|     └── app.py
├── .env
├── .gitignore
└── requirements.txt
```

---

## 🔍 ステップ 2: Agent class を理解する

`Agent` は Agent Framework の中心的なクラスです。以下の主要パラメータで構成されます：

| パラメータ | 説明 |
|-----------|------|
| `chat_client` | 必須: LLM クライアント |
| `instructions` | システムプロンプト |
| `name` | エージェント名 |
| `description` | エージェントの説明 |
| `tools` | エージェントが呼び出せる関数のリスト |
| `default_options` | temperature や response_formatなど LLM へ付与するデフォルトのオプションのパラメーターを設定可能。 |

!!! tip "ポイント"
    `tools=[]` を空のリストとして渡すことで、ツールなしのエージェントを作成できます。Phase 5 でツールを追加します！

---

## 🛠️ ステップ 3: 洗練されたエージェントを作成する

`app.py` に以下のコードを記述します：

```python
import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient

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
        description="A helpful AI assistant",
        instructions=SYSTEM_PROMPT,
        tools=[],  # ツールなし — Phase 5 で追加します！
        default_options={
            # "temperature": 0.7,
            "max_completion_tokens": 100,
            # "reasoning_effort": "none" # reasoning model で指定可能 
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

    await cl.Message(content="👋 こんにちは🌞Aria です。何かお手伝いできますか？").send()


@cl.on_message
async def main(message: cl.Message):
    agent: Agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")

    msg = cl.Message(content="")

    # run 時に options を指定して上書き可能
    chat_options = {
        "max_completion_tokens": 5000,
    }

    stream = agent.run(message.content, stream=True, session=session, options=chat_options)
    async for update in stream:
        if update.text:
            await msg.stream_token(update.text)

    await stream.get_final_response()  # 会話履歴を session に自動保存
    await msg.send()

```

---

## 🧵 ステップ 4: セッションを理解する

`AgentSession` は会話履歴を管理するオブジェクトです。

- 各ユーザーセッションに独自の session を持たせる
- session は自動的に全メッセージを保存する
- 同じ session を渡すことで会話コンテキストを維持

前述で追加したコード内だと、以下の部分で、セッション開始時に新しいスレッドを作成しています。

```python
session = agent.create_session()
```

また、以下の部分で、毎回同じスレッドを渡すことで会話履歴を保持して会話ができています。

```python
async for update in agent.run(message.content, stream=True, session=session):
    ...
```

実際に会話が session に保存されるタイミングは以下になります。

```python
await stream.get_final_response()  # 会話履歴を session に自動保存
```

!!! note "Phase 3 との違い"
    Phase 3 ではメッセージ履歴を手動でリストに管理していました。Agent Framework では `AgentSession` が自動的に管理してくれます。

---

## ▶️ ステップ 5: 実行とテスト

アプリケーションを起動します：

```bash
chainlit run app.py -w
```

以下を試してみましょう：

1. 「こんにちは」と入力して挨拶を確認
2. 質問をして回答を確認
3. 連続した会話で、過去の会話を覚えているか (メモリ機能であるセッション 
が機能するか) を確認
4. 「今日の日付は？」と聞いてシステムプロンプトの日付を確認

---

## 💡 何が変わったのか？

Phase 3 と動作は似ているように見えますが、アーキテクチャが大きく変わりました：

| 観点 | Phase 3（直接 API） | Phase 4（Agent Framework） |
|------|---------------------|---------------------------|
| ツール統合 | 手動実装が必要 | リストに追加するだけ（Phase 5！） |
| 推論 | 自分でロジックを書く | エージェントが次の行動を判断 |
| コードの整理 | メッセージフローを手動管理 | エージェントが管理 |
| 会話履歴 | リストで手動管理 | セッションで自動管理 |

!!! success "Agent Framework の利点"
    - **ツール統合が容易** — リストに追加するだけ（Phase 5！）
    - **組み込みの推論** — エージェントが次の行動を判断
    - **クリーンなコード** — エージェントがメッセージフローを管理
    - **セッションの管理** — 自動的な会話履歴の管理

---

## 補足: LLM へ渡すパラメーターについて

GPT-5.2 などの reasoning model (推論モデル) では `reasoning_effort` がサポートされています。

`reasoning_effort` を設定すると `temperature` や `top_p` の設定の取り扱いが異なりますのでご注意ください。
ここでは、`reasoning_effort` と `temperature` の関係を例にモデルごとの設定の違いをまとめています。

| モデル | temperature の設定 | `reasoning_effort` との関連 |
|--------|-----------------|------|
| GPT-4.1 / GPT-4o | 0〜2 で自由に設定可 | 非推論モデルのため `reasoning_effort` の設定不可。 |
| GPT-5.1 / GPT-5.2 | `reasoning_effort: "none"` の場合のみ 0〜2 | デフォルト値 (`none`) 以外 を指定した場合（`low`/`medium`/`high`/`xhigh`）では `temperature` を指定するとエラー |
| GPT-5 / GPT-5-mini / GPT-5-nano | 設定不可 | `reasoning_effort` に `none` がないため `temperature` 設定時は常にエラー。ただし `reasoning_effort` に `none` 設定すると `reasoning_tokens` が0になるのは確認できているが...  |

reasoning model で `reasoning_effort` を有効にしつつ出力を制御したい場合は、temperature の代わりに以下を使います：

- `reasoning_effort`: none / low / medium / high / xhigh — 推論の深さ
- `verbosity`: low / medium / high — 出力の冗長さ
- `max_output_tokens`: 出力トークン数の上限

## ✅ チェックポイント

- [ ] `Agent` クラスを使用している
- [ ] `tools=[]`（空リスト）を設定している
- [ ] ストリーミングが動作している
- [ ] セッション経由のメモリが動作している
- [ ] 日付が正しく表示される

---

## ❗よくある問題

!!! warning "トラブルシューティング"

    **`ModuleNotFoundError: No module named 'agent_framework'`**

    Agent Framework がインストールされていません：

    ```bash
    pip install -r requirements.txt
    ```

    **ストリーミングが動作しない**

    `run` メソッドで `stream=True` を構成しているか使用しているか確認してください。

    **会話コンテキストが保持されない**

    `AgentSession` オブジェクトをセッションに保存し、毎回同じものを渡しているか確認してください。また、自動保存されるのは `await stream.get_final_response()` 実行時になります。

---

## 📝 完成コード

??? example "完成コード（クリックで展開）"

    ```python
    --8<-- "solutions/phase-04/app.py"
    ```

---

## ➡️ 次のステップ

Agent Framework のアーキテクチャを理解したので、次はエージェントにツールを追加します！

[Phase 5: ツール呼び出し](05-tool-calling.md){ .md-button .md-button--primary }
