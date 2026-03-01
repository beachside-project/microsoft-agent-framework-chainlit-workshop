# Phase 2: Microsoft Foundry への 接続

!!! info "所要時間"
    約10分

## 🎯 学習目標

- Microsoft Foundry が提供するモデルの機能を理解する
- Microsoft Foundry のモデルへ接続する情報を取得する
- Microsoft Agent Framework のライブラリで接続をテストする

---

## 📖 Microsoft Foundry とは？

Microsoft Foundry は、2025年11月に Azure AI Foundry から名称が変わりリブランディングした、Microsoft の AI の中核をなすプラットフォームです。
モデルのみならず AI エージェントやワークフローの作成・管理、監視などの機能を備えています。

過去バージョンとの互換のため、Microsoft Foundry はクラシックポータル (古いポータル) と new ポータル (最新バージョンのポータル) がありますが、今回は new ポータルを対象に進めます。

## 🔧 ステップ 1: Micorosoft Foundry のモデルの情報で .env を更新


=== "COGBOT 提供の API キーで接続"

    Connpass のイベントページに .env に追記するための情報があります。
    その情報で .env を更新してください。
    不明点がありましたら運営スタッフにお気軽にお声がけください。

=== "自身の API キーで接続する"

    自身の API キーでモデルに接続したい場合は、Microsoft Foundry のリソースが作成済み、かつ、利用するモデルのデプロイ済みであることを確認し、必要な情報を取得して .env を更新します。
    
    - [クイック スタート: Microsoft Foundry リソースを設定する - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/ja-jp/azure/ai-foundry/tutorials/quickstart-create-foundry-resources?view=foundry&tabs=portal)

    操作方法はここでは詳しく記載しませんが、ご不明点がありましたら COGBOT 運営スタッフまでお気軽にご質問ください。 

取得した値を .env の中の以下の値を更新します。

- `MSF_MODEL_ENDPOINT`
- `MSF_MODEL_API_KEY`
- `MSF_MODEL_DEPLOYMENT_NAME`

---

## 🔧 ステップ 3: 接続テスト用スクリプトの作成

まず、`phase-02` フォルダを作成します：

=== "macOS / Linux"

    ```bash
    mkdir -p phase-02
    cd phase-02
    touch microsoft_foundry_model_check.py
    ```

=== "Windows (PowerShell)"

    ```powershell
    mkdir phase-02
    cd phase-02
    New-Item microsoft_foundry_model_check.py
    ```

`microsoft_foundry_model_check.py` に以下のコードを記述します：

```python
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

```

## 🔧 ステップ 4: テストの実行

```bash
python microsoft_foundry_model_check.py
```

成功すると以下のような出力が表示されます：

```text
🔄 Microsoft Foundry Model へ接続中...
🔄 テストメッセージを送信中...
🤖 レスポンス:Hello from Microsoft Foundry
✅ 接続成功！
```

---

## 🔍 コードの解説

| コード | 説明 |
|--------|------|
| `AzureOpenAIChatClient` | 非同期リクエスト用の Azure OpenAI クライアントライブラリ。ほかに `AzureOpenAIResponsesClient` や Azure 以外で Ollama や Anthropic など多様なクライアントライブラリがあります。 |
| `chat_client.as_agent(...)` | chat client のオブジェクトから agent を生成するメソッド。Agent Framework の新しいバージョンで利用可能。 |
| `hello_agent.run(...)` | Agent Framework の Agent を実行する際の標準的なメソッドの一つ |

---

## 📁 プロジェクト構成

```text
agent-framework-workshop/
├── .venv/
├── .env
├── requirements.txt
└── phase-02/
    └── microsoft_foundry_model_check.py
```

---

## ✅ チェックポイント

以下を確認してください：

- [x] Microsoft Foundry のモデルの情報を取得した。
- [x] `.env` ファイルにモデルの情報を保存した。
- [x] `microsoft_foundry_model_check.py` を実行して「接続成功」が表示された。

ここまでで、Microsoft Foundry のモデルへの接続が確認できました！

---

## ❓ よくあるトラブルと解決方法

??? question "404: Resource not found エラー"
    - `.env` ファイルの `MSF_MODEL_ENDPOINT`, `MSF_MODEL_API_VERSION`, `MSF_MODEL_DEPLOYMENT_NAME` が正しいか確認してください。
    - `load_dotenv(override=True)` が呼び出されているか確認してください。

??? question "401 エラー"
    - `.env` の `MSF_MODEL_API_KEY` が正しいか確認してください。

---

??? example "完成コード（クリックで展開）"

    ```python
    --8<-- "solutions/phase-02/microsoft_foundry_model_check.py"
    ```

---

## ➡️ 次のステップ

次は、Chainlit を使ってチャットの UI

[Phase 3: Chainlit 基礎🏃‍♂️‍➡️:material-arrow-right:](03-chainlit-basics.md){ .md-button }
