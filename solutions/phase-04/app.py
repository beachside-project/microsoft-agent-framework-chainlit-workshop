"""
フェーズ 4: Microsoft Agent Framework の導入
実行方法: chainlit run app.py -w

このフェーズでは Agent Framework と Agent クラスを導入します。
フェーズ 3 との主な違い: Agent はタスクを推論しツールを使用できる高レベルの抽象クラスです。

導入する主なコンセプト:
- Agent: ツールサポート付きのエージェント抽象クラス
- AgentSession: 会話履歴の管理
- エージェントの推論: 次に何をすべきかを判断できる
- ツール統合の準備（フェーズ 5）

フェーズ 3 との違い:
- フェーズ 3: メッセージ履歴を使った直接 LLM 呼び出し
- フェーズ 4: エージェントループ（考える → 行動する → 観察する）

前提条件:
- フェーズ 3 完了済み
- agent-framework パッケージのインストール
"""

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
            "temperature": 0.7,
            "max_tokens": 3000,
            # "reasoning_effort": "none"  # reasoning model で指定可能 
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
        # "max_tokens": 200,
        "reasoning_effort": "medium"
    }

    stream = agent.run(message.content, stream=True, session=session, options=chat_options)
    async for update in stream:
        if update.text:
            await msg.stream_token(update.text)

    await stream.get_final_response()  # 会話履歴を session に自動保存
    await msg.send()
