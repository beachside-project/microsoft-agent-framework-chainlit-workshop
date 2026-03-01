import asyncio
import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient

# 環境変数の読み込み
load_dotenv(override=True)


async def main():
    """Microsoft Foundry Model への接続テスト"""
    print("🔄 Microsoft Foundry Model へ接続中...")

    # Azure OpenAI Chat クライアントの初期化
    chat_client = AzureOpenAIChatClient(
        endpoint=os.environ["MSF_MODEL_ENDPOINT"],
        api_key=os.environ["MSF_MODEL_API_KEY"],
        api_version=os.environ["MSF_MODEL_API_VERSION"],
        deployment_name=os.environ["MSF_MODEL_DEPLOYMENT_NAME"]
    )

    # エージェントの作成
    hello_agent = chat_client.as_agent(
        name="HelloAgent",
        instructions="""あなたは親切なアシスタントです。
        挨拶をされたら Hello from Microsoft Foundry と回答してください
        """
    )

    # 接続テスト
    print("🔄 テストメッセージを送信中...")
    response = await hello_agent.run("こんにちは")
    print(f"🤖 レスポンス:{response.text}")
    print("✅ 接続成功！")


if __name__ == "__main__":
    asyncio.run(main())
