## Plan: GitBook → MkDocs Material 変換 + 日本語化

**TL;DR**: `.origin-source/` の GitBook ハンズオンコンテンツを Material for MkDocs 構成に変換する。ソースは純粋な標準 Markdown（GitBook 固有構文なし）のため、主な作業は (1) MkDocs プロジェクト構造の作成、(2) callout → admonition 変換、(3) OS 別コマンドのタブ化、(4) solutions コードの snippets インライン埋め込み、(5) GitHub Pages デプロイ設定、(6) 全コンテンツの日本語化 の6段階になる。

---

**Steps**

### Step 1: MkDocs プロジェクト骨格の作成

1. ワークスペースルート `c:\repos\temp\cogbot49\` に以下の構造を作成:
   ```
   mkdocs.yml
   docs/
     index.md              ← ワークショップ紹介（README.md 前半から）
     01-environment.md
     02-github-models.md
     03-chainlit-basics.md
     04-agent-framework.md
     05-tool-calling.md
     06-mcp-integration.md
     99-troubleshooting.md
   solutions/               ← snippets 用にプロジェクトルートに配置
     phase-02/test_github_models.py
     phase-03/app.py
     phase-04/app.py
     phase-05/app.py, tools.py
     phase-06/app.py, tools.py
   CLAUDE.md                ← README.md 後半のアーキテクチャガイド（nav 外）
   .env.example
   requirements.txt         ← ハンズオン用（元のまま）
   requirements-docs.txt    ← MkDocs ビルド用（mkdocs-material 等）
   ```
2. SUMMARY.md の構造を `mkdocs.yml` の `nav:` セクションにマッピング

### Step 2: `mkdocs.yml` の作成

以下の設定を含める:

- **テーマ**: `material` — `palette` でライト/ダークモード切替、`language: ja`（最終ステップで設定）
- **Extensions**:
  - `pymdownx.tabbed` (alternate スタイル) — OS 別コマンド切り替え
  - `pymdownx.superfences` — コードブロック
  - `pymdownx.highlight` + `pymdownx.inlinehilite` — シンタックスハイライト
  - `admonition` + `pymdownx.details` — callout (⚠️/💡/⏱️) の変換先
  - `pymdownx.snippets` — solutions/ コードの埋め込み
  - `attr_list` + `pymdownx.emoji` — アイコン類
- **Plugins**: `search`, `gh-deploy` 関連
- **nav**: SUMMARY.md と同等のナビゲーション構成

### Step 3: Markdown コンテンツの変換

各ドキュメントファイルに対して以下の変換を適用:

#### 3a. Callout → Admonition 変換 (全ドキュメント共通)

| 元の形式 | 変換先 |
|---------|--------|
| `> ⏱️ **Time to complete**: X minutes` | `!!! info "Time to complete"` |
| `> 💡 **Tip:**` | `!!! tip` |
| `> ⚠️ **Important:**` | `!!! warning` |
| `> 🆘 **Having issues?**` | `!!! danger "Having issues?"` |

#### 3b. OS 別コマンドのタブ化 (6箇所以上)

以下のパターンを `pymdownx.tabbed` 形式に変換:

- **venv activation** (01-environment.md, 99-troubleshooting.md): 現在のテーブル形式を `=== "macOS/Linux"` / `=== "Windows (PowerShell)"` タブに
- **`touch` コマンド** (01〜05): `=== "macOS/Linux"` → `touch file` / `=== "Windows (PowerShell)"` → `New-Item file`
- **`mkdir -p`** (02〜06): `=== "macOS/Linux"` → `mkdir -p dir` / `=== "Windows (PowerShell)"` → `mkdir dir`（`-p` 不要）
- **`cp` コマンド** (06-mcp-integration.md): `=== "macOS/Linux"` → `cp` / `=== "Windows (PowerShell)"` → `Copy-Item`
- **プロセス kill** (99-troubleshooting.md): `lsof`/`kill` vs `netstat`/`taskkill`
- **PowerShell 実行ポリシー**: Windows タブ専用の注意書き

#### 3c. Solutions コードの snippets 埋め込み

各フェーズのドキュメント末尾にある「完成コード参照」セクションで、`--8<--` snippets 構文を使い solutions/ 内のファイルを自動インクルード:

```markdown
??? example "完成コード (クリックで展開)"
    ```python
    --8<-- "solutions/phase-03/app.py"
    ```
```

### Step 4: README.md の分割

- README.md の前半（プロジェクト概要、学習目標、前提条件）→ docs/index.md としてワークショップのランディングページに
- 後半のアーキテクチャガイド、コードパターン、検証チェックリスト → `CLAUDE.md` としてリポジトリルートに配置（MkDocs nav には含めない）

### Step 5: 内部リンクの調整

- 各ドキュメント間の相対リンク（例: `[Phase 2](02-github-models.md)`）は、ファイルが全て `docs/` 配下にフラットに配置されるため**そのまま動作する**
- `SUMMARY.md` からのリンク（`docs/01-environment.md` 形式）は不要になる（`mkdocs.yml` の `nav:` に置き換え）

### Step 6: GitHub Pages デプロイ設定

1. `mkdocs.yml` に `site_url` と `repo_url` を設定
2. `.github/workflows/deploy-docs.yml` を作成 — push 時に `mkdocs gh-deploy` を自動実行する GitHub Actions ワークフロー
3. `requirements-docs.txt` に `mkdocs-material` 等のビルド依存を記載

### Step 7: 日本語化 (最終タスク)

全ステップ完了後、最後に実施:

1. **`mkdocs.yml`**: `language: ja` 設定（UIラベル「次へ」「前へ」「検索」等が日本語に）
2. **全 `.md` ファイルの翻訳**:
   - 見出し、本文、手順説明、コメントを日本語化
   - コードブロック内のコメントも日本語化
   - コマンド自体は英語のまま維持
   - 変数名・ファイル名は英語のまま維持
3. **admonition のタイトル日本語化**: `!!! info "所要時間"`, `!!! tip "ヒント"`, `!!! warning "重要"` 等
4. **nav のタイトル日本語化**: `mkdocs.yml` の nav 内表示名を日本語に

---

**Verification**

1. `pip install mkdocs-material` 後 `mkdocs serve` でローカルプレビュー起動し全ページ表示確認
2. 各ページで OS タブ（macOS/Linux / Windows PowerShell）の切り替えが正常動作するか確認
3. admonition（info/tip/warning/danger）が正しくレンダリングされるか確認
4. snippets で solutions/ のコードが正しくインライン展開されるか確認
5. 全ての内部リンク・外部リンクが動作するか確認
6. `mkdocs gh-deploy` で GitHub Pages にデプロイ成功するか確認
7. 日本語化後、UI ラベル・本文が全て日本語表示されるか確認

---

**Decisions**

- **テーマ**: Material for MkDocs を採用（タブ・admonition・検索を標準サポート）
- **Solutions 配置**: `pymdownx.snippets` でインライン埋め込み（`solutions/` はプロジェクトルートに配置し `base_path` で参照）
- **README 分割**: 紹介部分 → `index.md`、アーキテクチャガイド → `CLAUDE.md`（nav 外）
- **デプロイ**: GitHub Pages（GitHub Actions ワークフロー付き）
- **日本語化**: 全変換作業の最終ステップとして実施（英語版で構造を確定してから翻訳）
- **OS タブ**: PowerShell と bash の2タブ構成（CMD は省略、PowerShell に統一）
