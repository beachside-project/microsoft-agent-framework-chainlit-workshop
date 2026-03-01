"""
Phase 3: Chainlit を使ったストリーミング対応のチャット
実行方法: chainlit run app.py -w

このフェーズでは、OpenAI ライブラリを直接使用して Microsoft Foundry の Models から
ストリーミングレスポンスを受け取る、Web ベースのチャットインターフェースを
Chainlit で構築します。

主なコンセプト:
- Chainlit デコレーター (@cl.on_chat_start, @cl.on_message)
- セッション管理 (cl.user_session)
- OpenAI AsyncAzureOpenAI によるストリーミングレスポンス
- メッセージ履歴管理

前提条件:
- Phase 2 完了済み (Microsoft Foundry への接続確認)
- chainlit パッケージのインストール
"""

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
