# Phase 3: Chainlit でチャットインターフェースを構築

!!! info "所要時間"
    約15分

---

## 🎯 学習目標

- Chainlit チャットアプリを作成する。
- AzureOpenAI ライブラリを使って Microsoft Foundry に接続する。
  - Microsoft Agent Framework は次の phase 04 で実装することで、AzureOpenAI などの LLM を呼ぶだけのライブラリとの違いやメリットを理解していただきます。
- ストリーミングレスポンスを追加する。
- メッセージ履歴を使った会話メモリを実装する。

---

## 📁 ステップ 1: プロジェクトフォルダを作成

phase-02 ディレクトリにいる場合は、`cd ..` でワークスペースのルートに戻りましょう。
そして以下のコマンドを実行します。

=== "macOS / Linux"

    ```bash
    mkdir -p phase-03
    cd phase-03
    touch app.py
    ```

=== "Windows (PowerShell)"

    ```powershell
    mkdir phase-03
    cd phase-03
    New-Item app.py
    ```

ここまでの手順が完了すると、プロジェクトは以下の構成になります。

```text
cogbot-handson/
├── .venv/
├── phase-02/
├── phase-03/
|     └── app.py
├── .env
├── .gitignore
└── requirements.txt
```

---

## 🔰 ステップ 2: 最小限のアプリ（エコーアプリ）

まずは最もシンプルなチャットアプリから始めましょう。ユーザーの入力をそのまま返すエコーアプリです。

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"あなたの発言: {message.content}").send()
```

以下のコマンドで動作確認できます：

```bash
chainlit run app.py -w
```

!!! tip "ヒント"
    `-w` フラグを付けると、ファイルを保存するたびにアプリが自動的にリロードされます。開発中に便利です。

ブラウザで `http://localhost:8000` を開くと、チャット画面が表示されます。メッセージを入力すると、そのまま返ってくることを確認してください。

---

## 🤖 ステップ 3: LLM に接続

次に、Microsoft Foundry の LLM に接続して、AI が応答するようにしましょう。会話メモリ（メッセージ履歴）も実装します。

**変更点：**

- `AsyncOpenAI` クライアントを使って Microsoft Foundry に接続
- `@cl.on_chat_start` でセッション初期化とシステムプロンプトの設定
- `cl.user_session` にメッセージ履歴を保存して会話の文脈を維持

`app.py` を以下の内容に置き換えてください：

```python
import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a helpful AI assistant named Aria.
Be friendly and concise."""


def get_azure_openai_client():
    """AsyncAzureOpenAI クライアントを作成"""
    return AsyncAzureOpenAI(
        azure_endpoint=os.environ["MSF_MODEL_ENDPOINT"],
        api_key=os.environ["MSF_MODEL_API_KEY"],
        api_version=os.environ["MSF_MODEL_API_VERSION"]
    )


@cl.on_chat_start
async def start():
    """チャットセッションを初期化"""
    # メッセージ履歴をセッションに保存
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    cl.user_session.set("messages", messages)

    await cl.Message(content="👋 こんにちは！Aria です。何かお手伝いできますか？").send()


@cl.on_message
async def main(message: cl.Message):
    """受信メッセージを処理"""
    client = get_azure_openai_client()
    messages = cl.user_session.get("messages")

    # ユーザーメッセージを履歴に追加
    messages.append({"role": "user", "content": message.content})

    # Chat Completions API を呼び出す
    response = await client.chat.completions.create(
        model=os.environ["MSF_MODEL_DEPLOYMENT_NAME"],
        messages=messages,
    )

    result_text = response.choices[0].message.content
    await cl.Message(content=result_text).send()

    # LLM からの応答を履歴に追加
    messages.append({"role": "assistant", "content": result_text})
    cl.user_session.set("messages", messages)

```

---

## ⚡ ステップ 4: ストリーミングを追加

最後に、レスポンスをストリーミングで表示するように改良します。ユーザーは応答が生成されるのをリアルタイムで確認できるようになります。

`@cl.on_message` 関数を以下のコードに置き換えてください：

```python
@cl.on_message
async def main(message: cl.Message):
    """ストリーミング対応のメッセージ処理"""
    client = get_azure_openai_client()
    messages = cl.user_session.get("messages")

    # ユーザーメッセージを履歴に追加
    messages.append({"role": "user", "content": message.content})

    # ストリーミング用の空メッセージを作成
    msg = cl.Message(content="")
    full_response = ""

    # OpenAI SDK でトークンごとにストリーミング
    stream = await client.chat.completions.create(
        model=os.environ["MSF_MODEL_DEPLOYMENT_NAME"],
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                full_response += delta_content
                await msg.stream_token(delta_content)

    await msg.send()

    # アシスタントの応答を履歴に追加
    messages.append({"role": "assistant", "content": full_response})
    cl.user_session.set("messages", messages)
```

**変更点：**

- `stream=True` — API 呼び出しでストリーミングを有効化
- `async for chunk in stream:` — チャンクを逐次処理
- `chunk.choices[0].delta.content` — 各チャンクのテキスト内容
- `msg.stream_token()` — 各チャンクを即座に表示
- 安全チェック: `if chunk.choices and len(chunk.choices) > 0:`

---

## ✅ チェックポイント

アプリを起動して、以下のテストを実行してください：

```bash
chainlit run app.py -w
```

| テスト | 入力 | 期待される結果 |
|--------|------|---------------|
| 基本的なチャット | 「こんにちは！」 | フレンドリーな挨拶 |
| メモリー | 「私は ANNA です」→「私の名前は？」 | 「ANNA」 |
| ストリーミング | 長い質問 (例: 「1000文字程度で面白い話をして」) | 文字がストリーミングで表示される |
| アイデンティティ | 「あなたの名前は？」 | 「Aria」 |

すべてが確認できたら、Ctrl + C などでターミナルの実行を停止します。

!!! tip "ストリーミングがスムーズじゃないときの改善方法"
    Microsoft Foundry ではコンテンツフィルターという機能がデフォルトで実装されています。  
    その中の設定で Streaming mode はデフォルト値が "Default" ですが、これを "Asynchronous" に変更すると、他のチャットサービスでみかけるようなスムーズなストリーミングを体験することができます。  
    詳細や注意点は以下のリンクをご確認ください。  
    - [Azure OpenAI でのコンテンツ ストリーミング - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/ja-jp/azure/ai-foundry/openai/concepts/content-streaming?view=foundry)

---

## ❗ よくあるトラブル

| 問題 | 原因 | 解決策 |
|------|------|--------|
| メモリが機能しない | `cl.user_session` にメッセージが保存されていない | `messages.append()` と `cl.user_session.set()` が正しく呼ばれているか確認 |
| ストリーミングが動作しない | `stream=True` が設定されていない | `client.chat.completions.create()` に `stream=True` を追加 |
| ストリーミングで `IndexError` | チャンクに `choices` が含まれていない | `if chunk.choices and len(chunk.choices) > 0:` で安全チェック |
| ポート 8000 が使用中 | 別のプロセスがポートを占有 | `chainlit run app.py -w --port 8001` で別ポートを指定 |

---

## 📝 完成コード

??? example "完成コード（クリックで展開）"

    ```python
    --8<-- "solutions/phase-03/app.py"
    ```

---

## ➡️ 次のステップ

Chainlit に Microsoft Agent Framework を組み込みましょう。

[Phase 4: Agent Framework🏃‍♂️‍➡️:material-arrow-right:](04-agent-framework.md){ .md-button }

