"""
フェーズ 5: Tool callを備えたエージェント
実行方法: chainlit run app.py -w

このフェーズでは、エージェントに tools を追加し、
外部 API からリアルタイムデータを取得できるようにします。

主要概念：
- Agent へのツール追加
- Tool call のフロー（思考 → 実行 → 観察）
- Chainlit UI でのツールステップ表示
- LLM の知識と外部データの組み合わせ

前提条件：
- フェーズ 4 の完了
- .env に WEATHER_API_KEY を設定済みであること
"""

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
            "reasoning_effort": "none"  # reasoning model で指定可能
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
        # Tool call のストリーミング
        if update.contents:
            for content in update.contents:
                # Tool call 開始時
                if isinstance(content, Content) and content.type == "function_call":
                    if content.name and content.call_id not in tool_steps:
                        tool_steps[content.call_id] = cl.Message(content=f"🔧 ツールを呼び出し中: {content.name}...")
                        step = cl.Step(
                            name=f"🔧 {content.name}",
                            type="tool"
                        )
                        await step.send()
                        tool_steps[content.call_id] = step
                # Tool call 後の結果
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
