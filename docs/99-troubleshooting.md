# トラブルシューティングガイド

!!! danger "問題が発生していますか？"
    このガイドでは、ワークショップ中に遭遇する可能性のある一般的な問題とその解決策を網羅しています。問題が発生した場合は、まず該当するセクションを確認してください。または、お気軽にスタッフにご質問ください。

---

## 🔧 一般的なセットアップの問題

??? warning "Python バージョンの問題"
    **問題:**
    ```
    Python 3.11 以上が必要ですが、古いバージョンがインストールされています。
    ```

    **解決策:**

    現在の Python バージョンを確認します：

    ```bash
    python --version
    ```

    Python 3.11 未満の場合は、最新版をインストールしてください：

    ```bash
    # pyenv を使用している場合
    pyenv install 3.11
    pyenv local 3.11
    ```

    複数のバージョンがインストールされている場合：

    ```bash
    # python3 コマンドを試す
    python3 --version
    ```

??? warning "仮想環境が有効化されていない"
    **問題:**
    パッケージをインストールしても見つからない、または間違った Python が使用されている。

    **解決策:**

    仮想環境を作成して有効化します：

    ```bash
    # 仮想環境を作成
    python -m venv .venv
    ```

    === "macOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

    === "Windows (PowerShell)"

        ```powershell
        .venv\Scripts\Activate.ps1
        ```

    有効化されると、プロンプトに `(.venv)` が表示されます。

    !!! tip "確認方法"
        ```bash
        # どの Python が使用されているか確認
        which python   # macOS / Linux
        where python   # Windows
        ```

---

## 📋 フェーズ別の問題

### フェーズ 2: Microsoft Foundry への接続

??? warning "404: Resource not found エラー"
    - `.env` ファイルの `MSF_MODEL_ENDPOINT`, `MSF_MODEL_API_VERSION`, `MSF_MODEL_DEPLOYMENT_NAME` が正しいか確認してください。
    - `load_dotenv(override=True)` が呼び出されているか確認してください。

??? warning "401 エラー"
    - `.env` の `MSF_MODEL_API_KEY` が正しいか確認してください。

??? warning "キーは正しいはずだが接続できない"
    **原因:**

    - インターネット接続の問題
    - ファイアウォールやプロキシの設定
    - GitHub Models サービスのダウンタイム

    **解決策:**

   会社の PC などでプロキシの設定がされている場合ははずしてお試しください。
    ```

??? warning "Module not found: openai"
    **問題:**
    ```
    ModuleNotFoundError: No module named 'openai'
    ```

    **解決策:**

    ```bash
    # 仮想環境が有効化されていることを確認してからインストール
    pip install openai
    ```

    それでも解決しない場合：

    ```bash
    # pip のパスを確認
    pip --version

    # 明示的に python -m pip を使用
    python -m pip install openai
    ```

### フェーズ 3: Chainlit チャットインターフェース

??? warning "ポート 8000 がすでに使用されている"
    **問題:**
    ```
    Address already in use: port 8000
    ```

    **解決策:**

    === "macOS / Linux"

        ```bash
        # ポート 8000 を使用しているプロセスを確認
        lsof -i :8000
        # プロセスを終了
        kill -9 <PID>
        ```

    === "Windows (PowerShell)"

        ```powershell
        # ポート 8000 を使用しているプロセスを確認
        netstat -ano | findstr :8000
        # プロセスを終了
        taskkill /PID <PID> /F
        ```

    または、別のポートで起動します：

    ```bash
    chainlit run app.py --port 8001
    ```

??? warning "ストリーミングが動作しない"
    **問題:**
    レスポンスが一度にすべて表示され、ストリーミング（逐次表示）されない。

    **解決策:**

    `stream=True` パラメータが設定されていることを確認します：

    ```python
    # ストリーミングを有効にする
    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        stream=True  # これが重要
    )
    ```

    Chainlit でストリーミングを処理する正しい方法：

    ```python
    import chainlit as cl

    @cl.on_message
    async def main(message: cl.Message):
        msg = cl.Message(content="")
        await msg.send()

        # ストリーミングレスポンスを処理
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": message.content}],
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                await msg.stream_token(chunk.choices[0].delta.content)

        await msg.update()
    ```

??? warning "ストリーム処理での IndexError"
    **問題:**
    ```
    IndexError: list index out of range
    ```

    **原因:**
    ストリーミングチャンクの `choices` が空の場合があります。

    **解決策:**

    ```python
    for chunk in response:
        # choices が存在するか確認
        if chunk.choices and chunk.choices[0].delta.content:
            await msg.stream_token(chunk.choices[0].delta.content)
    ```

??? warning "メッセージ履歴が動作しない"
    **問題:**
    ボットが前の会話を覚えていない。

    **解決策:**

    セッションにメッセージ履歴を保存していることを確認します：

    ```python
    import chainlit as cl

    @cl.on_chat_start
    async def start():
        # セッションにメッセージ履歴を初期化
        cl.user_session.set("messages", [
            {"role": "system", "content": "あなたは親切なアシスタントです。"}
        ])

    @cl.on_message
    async def main(message: cl.Message):
        # 履歴を取得
        messages = cl.user_session.get("messages")
        # 新しいメッセージを追加
        messages.append({"role": "user", "content": message.content})

        # API 呼び出し
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        assistant_message = response.choices[0].message.content
        # アシスタントの応答も履歴に追加
        messages.append({"role": "assistant", "content": assistant_message})
        # セッションを更新
        cl.user_session.set("messages", messages)

        await cl.Message(content=assistant_message).send()
    ```

### フェーズ 4: Agent Framework

??? warning "ModuleNotFoundError"
    **問題:**
    ```
    ModuleNotFoundError: No module named 'agent_framework'
    ```

    **解決策:**

    ```bash
    # Agent Framework をインストール
    pip install agent-framework
    ```

    パッケージ名とインポート名が異なる場合があります：

    ```python
    # 正しいインポート方法を確認
    import agent_framework
    print(agent_framework.__version__)
    ```

### フェーズ 5: Tool Calling

??? warning "WEATHER_API_KEY が設定されていない"
    **問題:**
    ```
    WEATHER_API_KEY が見つかりません。
    ```

    **解決策:**

    `.env` ファイルに天気 API キーを追加します：

    ```env
    WEATHER_API_KEY=your_weather_api_key
    ```

    コードで読み込みます：

    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    weather_api_key = os.getenv("WEATHER_API_KEY")
    if not weather_api_key:
        raise ValueError("WEATHER_API_KEY が .env ファイルに設定されていません")
    ```

??? warning "httpx.ConnectError"
    **問題:**
    ```
    httpx.ConnectError: [Errno 111] Connection refused
    ```

    **原因:**

    - 外部 API サーバーがダウンしている
    - URL が間違っている
    - ネットワーク接続の問題

    **解決策:**

    ```python
    import httpx

    async def call_api_safely(url: str):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            print(f"接続エラー: {url} に接続できません")
            return None
        except httpx.TimeoutException:
            print(f"タイムアウト: {url} からの応答がありません")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP エラー: {e.response.status_code}")
            return None
    ```

### フェーズ 6: MCP 統合

??? warning "MCP ツールが使用されない"
    **問題:**
    MCP ツールは一覧に表示されるが、モデルがそれを呼び出さない。

    **解決策:**

    1. ツールの `description` が十分に詳しいか確認：

    ```python
    # 良い例 - 詳細な説明
    tool = {
        "name": "search_database",
        "description": "データベースからキーワードに基づいてドキュメントを検索します。"
                       "全文検索をサポートし、最大10件の結果を返します。"
    }

    # 悪い例 - 説明が不十分
    tool = {
        "name": "search",
        "description": "検索する"
    }
    ```

---

## 🐛 よくあるコードの問題

??? tip "Async/Await のミス"
    **問題:**
    ```
    RuntimeWarning: coroutine was never awaited
    ```
    または
    ```
    TypeError: object Response can't be used in 'await' expression
    ```

    **解決策:**

    ```python
    # ❌ 間違い - await が不足
    async def main():
        result = some_async_function()  # await が必要！

    # ✅ 正しい - await を使用
    async def main():
        result = await some_async_function()

    # ❌ 間違い - 非同期でない関数に await を使用
    async def main():
        result = await sync_function()  # これは不要

    # ✅ 正しい - 同期関数はそのまま呼び出す
    async def main():
        result = sync_function()
    ```

    !!! tip "ヒント"
        関数が `async def` で定義されている場合は `await` が必要です。通常の `def` で定義されている場合は `await` は不要です。

??? tip "インポート順序の問題"
    **問題:**
    ```
    ImportError: cannot import name 'xxx' from 'yyy'
    ```

    **解決策:**

    Python のインポートは以下の順序で記述することを推奨します：

    ```python
    # 1. 標準ライブラリ
    import os
    import json
    import asyncio

    # 2. サードパーティライブラリ
    from openai import OpenAI
    import chainlit as cl
    import httpx
    from dotenv import load_dotenv

    # 3. ローカルモジュール
    from tools import get_weather
    from config import settings
    ```

    パッケージがインストールされているか確認：

    ```bash
    pip list | grep openai
    pip list | grep chainlit
    ```

??? tip "文字列フォーマットの問題"
    **問題:**
    f-string や文字列フォーマットが正しく動作しない。

    **解決策:**

    ```python
    # ❌ 間違い - 波括弧のエスケープ忘れ
    json_str = f"{"key": "value"}"  # SyntaxError

    # ✅ 正しい - 波括弧をエスケープ
    json_str = f'{{"key": "value"}}'

    # ❌ 間違い - 辞書への直接フォーマット
    data = {"name": "テスト"}
    msg = f"結果: {data["name"]}"  # SyntaxError

    # ✅ 正しい - 変数を使用
    data = {"name": "テスト"}
    name = data["name"]
    msg = f"結果: {name}"

    # ✅ またはシングルクォートを使用
    msg = f"結果: {data['name']}"
    ```

---

## 📊 パフォーマンスの問題

??? tip "レスポンスが遅い"
    **原因:**

    - モデルへのリクエストが多すぎる
    - コンテキストウィンドウが大きすぎる
    - ネットワークレイテンシ

    **解決策:**

    1. **ストリーミングを使用する** - ユーザーに部分的なレスポンスを早く表示できます：

    ```python
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True  # ストリーミングでレスポンスを高速化
    )
    ```

    2. **メッセージ履歴を制限する**：

    ```python
    # 最新の N 件のメッセージだけを送信
    MAX_MESSAGES = 20

    def trim_messages(messages):
        if len(messages) > MAX_MESSAGES:
            # システムメッセージは常に保持
            system_msg = messages[0]
            recent = messages[-MAX_MESSAGES + 1:]
            return [system_msg] + recent
        return messages
    ```

    3. **`max_tokens` を設定する**：

    ```python
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500  # 応答の最大トークン数を制限
    )
    ```

??? tip "トークン使用量が多い"
    **原因:**

    - システムプロンプトが長すぎる
    - メッセージ履歴が蓄積されている
    - 不必要に詳細な応答を要求している

    **解決策:**

    1. **トークン使用量を監視する**：

    ```python
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    # トークン使用量を表示
    usage = response.usage
    print(f"入力トークン: {usage.prompt_tokens}")
    print(f"出力トークン: {usage.completion_tokens}")
    print(f"合計トークン: {usage.total_tokens}")
    ```

    2. **システムプロンプトを簡潔にする**：

    ```python
    # ❌ 長すぎるシステムプロンプト
    system_prompt = """あなたは非常に知識豊富な...(500語以上の説明)..."""

    # ✅ 簡潔なシステムプロンプト
    system_prompt = "あなたは親切なアシスタントです。簡潔に回答してください。"
    ```

    3. **要約機能を実装する** - 会話が長くなったら古いメッセージを要約します。

---

## 🔐 セキュリティの問題

??? danger "トークンが Git にコミットされた"
    **問題:**
    `GITHUB_TOKEN` やその他のシークレットを誤って Git リポジトリにコミットしてしまった。

    **解決策:**

    1. **すぐにトークンを無効化する** - GitHub の設定画面でトークンを取り消してください。

    2. **Git の履歴からトークンを削除する**：

    ```bash
    # .env ファイルを .gitignore に追加
    echo ".env" >> .gitignore

    # Git の履歴から .env を削除
    git filter-branch --force --index-filter \
      'git rm --cached --ignore-unmatch .env' \
      --prune-empty --tag-name-filter cat -- --all

    # 強制プッシュ（注意して使用）
    git push origin --force --all
    ```

    3. **新しいトークンを生成する** - 古いトークンが漏洩した可能性があるため、必ず新しいトークンを作成してください。

    !!! danger "重要"
        一度公開リポジトリにプッシュされたトークンは、すでに第三者にスキャンされている可能性があります。**必ず**トークンを無効化してください。

    4. **予防策** - `.gitignore` に以下を追加：

    ```gitignore
    # 環境変数ファイル
    .env
    .env.local
    .env.*.local

    # シークレット
    *.pem
    *.key
    ```

??? danger "エラーメッセージにトークンが漏洩する"
    **問題:**
    エラーログやデバッグ出力にトークンが表示されてしまう。

    **解決策:**

    1. **トークンをログに記録しない**：

    ```python
    import os
    import logging

    logger = logging.getLogger(__name__)

    # ❌ 間違い - トークンがログに表示される
    token = os.getenv("GITHUB_TOKEN")
    logger.debug(f"Token: {token}")

    # ✅ 正しい - トークンをマスクする
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logger.debug(f"Token: {token[:4]}****")
    ```

    2. **例外処理でトークンを除外する**：

    ```python
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
    except Exception as e:
        # エラーメッセージからトークンを除去
        error_msg = str(e)
        token = os.getenv("GITHUB_TOKEN", "")
        if token and token in error_msg:
            error_msg = error_msg.replace(token, "****")
        logger.error(f"API エラー: {error_msg}")
    ```

---

## 📞 ヘルプを得る

上記の解決策で問題が解決しない場合は、以下の手順を試してください。

??? tip "デバッグモードを有効にする"
    より詳細なログを取得するために、デバッグモードを有効にします：

    ```python
    import logging

    # デバッグレベルのログを有効化
    logging.basicConfig(level=logging.DEBUG)

    # OpenAI のデバッグログを有効化
    logging.getLogger("openai").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    ```

    Chainlit のデバッグモード：

    ```bash
    # デバッグモードで起動
    chainlit run app.py --debug
    ```

??? tip "Chainlit のログを確認する"
    Chainlit は `.chainlit/logs` ディレクトリにログを出力します：

    ```bash
    # ログファイルを確認
    cat .chainlit/logs/app.log

    # リアルタイムでログを監視
    tail -f .chainlit/logs/app.log
    ```

??? tip "個々のコンポーネントをテストする"
    問題を切り分けるために、各コンポーネントを個別にテストします：

    ```python
    # 1. API 接続テスト
    import os
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()

    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=os.getenv("GITHUB_TOKEN")
    )

    # 簡単なテスト
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "テスト"}],
            max_tokens=10
        )
        print(f"✅ API 接続成功: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ API 接続失敗: {e}")
    ```

    ```python
    # 2. ツール呼び出しテスト
    import json

    tools = [
        {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "テスト用ツール",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string", "description": "テスト入力"}
                    },
                    "required": ["input"]
                }
            }
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "テストツールを使ってください"}],
            tools=tools
        )
        if response.choices[0].message.tool_calls:
            print(f"✅ ツール呼び出し成功: {response.choices[0].message.tool_calls[0].function.name}")
        else:
            print("⚠️ ツールが呼び出されませんでした")
    except Exception as e:
        print(f"❌ ツール呼び出し失敗: {e}")
    ```

### リソース

問題が解決しない場合は、以下の公式ドキュメントを参照してください：

- [Chainlit ドキュメント](https://docs.chainlit.io)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [GitHub Models ドキュメント](https://github.com/marketplace/models)

---

## ✅ クイックチェックリスト

問題のデバッグを始める前に、以下の項目を確認してください：

- [ ] Python 3.11 以上がインストール済み
- [ ] 仮想環境が有効化済み（プロンプトに `(.venv)` が表示）
- [ ] `.env` ファイルに GITHUB_TOKEN が設定済み
- [ ] 必要なパッケージがインストール済み
- [ ] 正しいフェーズのフォルダにいる
- [ ] コードがソリューションファイルと完全に一致
- [ ] import やファイル名にタイプミスがない
- [ ] ポート 8000 が利用可能
- [ ] インターネット接続が正常
- [ ] GitHub トークンが有効期限内

!!! tip "それでも解決しない場合"
    上記のチェックリストをすべて確認しても問題が解決しない場合は、エラーメッセージの全文をコピーして、インストラクターに相談してください。
