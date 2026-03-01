"""
フェーズ 6: MCP 統合を備えたエージェント
実行方法: chainlit run app.py -w

このフェーズでは、ローカルツールと外部サーバーの
MCP（Model Context Protocol）ツールを組み合わせます。

主要概念：
- 外部ツールサーバー向け MCPStreamableHTTPTool
- ローカルツールと MCP ツールの組み合わせ
- ツール統合のための拡張可能なアーキテクチャ

前提条件：
- フェーズ 5 の完了
- MCP の理解
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent, Content, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient
from tools import TOOLS

load_dotenv(override=True)

SYSTEM_PROMPT = f"""あなたは、Aria という名の役に立つ AI アシスタントです。

複数のツールにアクセスできます。
- ローカルツール: 天気予報のクエリには get_weather をご利用ください。
- MCP ツール: 技術的な質問には Microsoft Learn ドキュメントをご利用ください。

ガイドライン:
- 天気予報には get_weather を使用してください。
- Azure、クラウド、Microsoft の技術に関する質問には、利用可能な MCP ツールをご利用ください。

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


def get_mcp_tools():
    """
    外部サーバーから MCP ツールを取得。

    MCP により外部ツールサーバーに接続可能。
    エージェントにツールを提供する MCP サーバーを設定します。
    """
    mcp_tools = []

    try:
        # Microsoft Learn のドキュメントを検索可能な Microsoft Learn MCP サーバーを追加
        mcp_tools.append(
            MCPStreamableHTTPTool(
                name="microsoft_learn",
                description="Microsoft Learn ドキュメントを検索するツール。Azure、クラウド、Microsoft の技術に関する質問に使用してください。",
                url="https://learn.microsoft.com/api/mcp"
            )
        )
    except Exception as e:
        print(f"警告: Microsoft Learn MCP サーバーに接続できませんでした: {e}")

    return mcp_tools


def create_agent():
    """設定済みの Agent を作成"""
    chat_client = get_chat_client()
    mcp_tools = get_mcp_tools()
    # Agent を作成
    agent: Agent = chat_client.as_agent(
        name="Aria",
        description="Tools を備えた便利なAIアシスタント",
        instructions=SYSTEM_PROMPT,
        tools=[*TOOLS, *mcp_tools],  # ローカルと MCP の tools を追加
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

    await cl.Message(content="👋 こんにちは🌞Aria です。").send()


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
