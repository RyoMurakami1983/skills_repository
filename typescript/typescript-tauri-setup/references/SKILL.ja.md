---
name: typescript-tauri-setup
description: Set up Tauri v2 desktop app environment with MSVC, Rust, and Tauri CLI on top of a TypeScript project. Use when building a lightweight desktop app from an existing TypeScript/HTML/CSS codebase.
metadata:
  author: RyoMurakami1983
  tags: [tauri, rust, msvc, desktop, typescript, windows]
  invocable: false
---

# Tauriデスクトップアプリ環境をセットアップする

既存のTypeScriptプロジェクトにTauri v2デスクトップアプリ機能を追加するための単一ワークフローです。MSVC C++ビルドツール、Rustツールチェーン、Tauri CLIのインストール、プロジェクト初期化、Windows上での初回ビルド確認までをカバーします。

## このスキルを使うとき

このスキルは次のときに使います:
- TypeScript/HTML/CSSのWebプロジェクトをスタンドアロンのデスクトップアプリに変換するとき
- Windows開発マシンで初めてTauriをセットアップするとき
- Tauriアプリをローカルビルドする必要があるメンバーをオンボーディングするとき
- Tauriのビルド失敗（MSVC、Rust、WiX）をトラブルシューティングするとき
- 軽量デスクトップ配布でTauriとElectronの選択を検討しているとき

---

## Related Skills

- **`typescript-setup-dev-environment`** — **前提条件**: Node.js + TypeScriptツールチェーンの構築を先に完了すること
- **`git-initial-setup`** — 最初のコミット前にmainブランチを保護するときに使用
- **`git-commit-practices`** — Tauriセットアップ変更を原子的にコミットするときに使用

---

## Dependencies

- `typescript-setup-dev-environment` 完了済み（Node.js 20+, npm, TypeScript）
- Visual Studio 2022+ の C++ Desktop workload（MSVCリンカーに必要）
- Windows 10/11 + WebView2ランタイム（最新Windowsにはプリインストール済み）
- インターネット接続（Rustとクレートのダウンロードに必要）

---

## Core Principles

1. **前提条件チェーン** — 各ツールは前のツールに依存する。順序を厳守（基礎と型）
2. **各ステップで検証** — 次に進む前にインストールを確認し、連鎖的な失敗を防ぐ（基礎と型）
3. **最小限のRust知識** — Tauriプラグインがほとんどのネイティブ操作を処理。Rustコードはめったに必要ない（余白の設計）
4. **再現可能なビルド** — 正確なバージョンと設定をドキュメント化してチームの再現性を確保（温故知新）
5. **軽量設計** — TauriはOSのWebViewを使用し、~10MBのバイナリを生成（Electronの~200MBと比較）（成長の複利）

---

## Tauriの位置づけ: なぜTauriか

### C# / Python経験者向けの解説

Tauriは「**既存のWeb技術（HTML/CSS/TypeScript）をデスクトップアプリとして配布する器**」です。

| 比較 | C# + WPF | Python + Tkinter | TypeScript + Tauri |
|------|---------|-----------------|-------------------|
| UIの作り方 | XAML | Python GUI | HTML/CSS（Webと同じ） |
| バイナリサイズ | ~50MB | ~30MB (PyInstaller) | **~10MB** |
| 裏側の言語 | C# | Python | Rust（ほぼ触らない） |
| 配布方法 | MSIX/ClickOnce | PyInstaller/exe | **MSI/NSIS** |

**なぜRustを学ばなくてOK?**: Tauriプラグインが「ファイル保存」「ダイアログ表示」「クリップボード」等のネイティブ操作をTypeScript APIとして提供します。Rustを書くのは、プラグインにない独自機能が必要な場合だけです。

```
あなたが書くもの:
  TypeScript (95%) → UI、ロジック、描画
  tauri.conf.json (5%) → 設定

Tauriが担当するもの:
  Rust → セキュリティ、ネイティブAPI、バイナリ生成
  WebView2 → HTML/CSS/JSの表示
```

---

## Workflow: Tauriデスクトップアプリ環境のセットアップ

### Step 1: MSVC C++ビルドツールのインストール

Rustコンパイラのリンカーに必要なMicrosoft Visual C++ビルドツールをインストールします。C++コンパイラをネイティブ依存関係のためにインストールするのと同等です。

**方法A: Visual Studio Installer経由（GUI）**

1. Visual Studio Installerを開く
2. お使いのVisual Studioエディション → 変更 を選択
3. **「C++によるデスクトップ開発」** ワークロードにチェック
4. 変更をクリックしてインストール完了まで待つ

**方法B: コマンドライン**

```powershell
# Visual Studioのインストール
winget install Microsoft.VisualStudio.2022.Community

# その後、InstallerのGUIでC++ワークロードを追加
```

**確認:**

```powershell
# MSVCがアクセス可能か確認（パスはVSバージョンにより異なる）
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
cl.exe
```

**なぜMSVCが必要?**: Rustはコンパイル時にC/C++のリンカーを使います。Windows上ではMSVCのリンカー（`link.exe`）が標準。これがないとRustのコンパイルが失敗します。

新しい開発マシンでRust/Tauriのコンパイル環境を構築するときに使います。

> **Values**: 基礎と型 / 継続は力

### Step 2: Rustのインストール

`rustup`経由でRustツールチェーンをインストールします。RustはTauriが使用するバックエンド言語ですが、ほとんどのプロジェクトでは最小限の関わりです。

```powershell
# winget経由でインストール
winget install Rustlang.Rustup

# 重要: インストール後にPATHを更新
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 確認
rustc --version
cargo --version
```

**なぜRust?**: Tauriは軽量ランタイムとセキュリティモデルのためにRustを使用しています。直接Rustコードを書くことはめったにありません。プラグインがファイルI/O、ダイアログ、その他のネイティブ操作をTypeScript APIとして提供します。

**C#経験者向け**: Rustのインストールは`.NET SDK`のインストールに相当します。`cargo`は`dotnet` CLIに、`Cargo.toml`は`.csproj`に相当します。

開発マシンに初めてRustをインストールするときに使います。

> **Values**: 基礎と型 / 余白の設計

### Step 3: Tauri CLIのインストール

既存のTypeScriptプロジェクトにTauri CLIとAPIパッケージを追加します。

```powershell
# 開発依存: ビルド/開発コマンド用CLI
npm install --save-dev @tauri-apps/cli

# ランタイム依存: Tauri機能のTypeScript API
npm install @tauri-apps/api
```

**確認:**

```powershell
npx tauri --version
```

既存のTypeScriptプロジェクトにTauriを追加するときに使います。

> **Values**: 基礎と型 / 継続は力

### Step 4: Tauriプロジェクトの初期化

インタラクティブな初期化ツールを実行して`src-tauri/`ディレクトリ構造を作成します。

```powershell
npx tauri init
```

初期化ツールが聞いてくること:
1. **アプリ名** — アプリケーション名（例: `my-app`）
2. **ウィンドウタイトル** — 表示タイトル（例: `マイアプリケーション`）
3. **フロントエンドdistパス** — ビルドされたフロントエンドへの相対パス（例: `../dist`）
4. **フロントエンド開発URL** — 開発サーバーURL（例: `http://localhost:1420`）
5. **フロントエンドビルドコマンド** — フロントエンドのビルドコマンド（例: `npm run build`）
6. **フロントエンド開発コマンド** — 開発サーバー起動コマンド（空でもOK）

**生成される構造:**

```
src-tauri/
├── src/
│   ├── lib.rs          # Rustエントリポイント（自動生成）
│   └── main.rs         # Windowsエントリポイント
├── capabilities/
│   └── default.json    # セキュリティ許可設定
├── icons/              # アプリアイコン（デフォルトプレースホルダー）
├── Cargo.toml          # Rust依存関係
├── tauri.conf.json     # 中央設定ファイル
└── build.rs            # ビルドスクリプト
```

プロジェクトに初めてTauriを追加するときに使います。

> **Values**: 基礎と型 / 余白の設計

### Step 5: tauri.conf.jsonの設定

アプリケーションに合わせて中央設定ファイルをカスタマイズします。

```json
{
  "productName": "マイアプリケーション",
  "version": "0.1.0",
  "identifier": "com.example.my-app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:1420",
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": ""
  },
  "app": {
    "windows": [
      {
        "title": "マイアプリケーション",
        "width": 1200,
        "height": 900,
        "resizable": true
      }
    ]
  },
  "bundle": {
    "active": true,
    "targets": ["msi", "nsis"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/icon.ico"
    ]
  }
}
```

**重要な設定:**
- `frontendDist` — ビルド済みHTML/CSS/JSの場所（`src-tauri/`からの相対パス）
- `beforeBuildCommand` — Rustコンパイル前に実行（通常`npm run build`）
- `bundle.targets` — インストーラー形式（企業向け`msi`、一般向け`nsis`）

Tauriアプリを自分のプロジェクトに合わせてカスタマイズするときに使います。

> **Values**: 基礎と型 / ニュートラル

### Step 6: ビルドと確認

初回ビルドを実行してエンドツーエンドで動作することを確認します。

```powershell
# デバッグビルド（コンパイル速い、バイナリ大きめ）
npx tauri build --debug
```

**期待される出力:**

```
   Compiling my-app v0.1.0
    Finished `dev` profile target(s) in ~90s
        Info app.exe (approximately 10-15MB)
```

コンパイル済みバイナリの場所:
```
src-tauri/target/debug/my-app.exe
```

**初回ビルドは約90秒** かかります（Rustコンパイル）。2回目以降はキャッシュを使用し、フロントエンドのみの変更なら約10-20秒です。

ビルドパイプライン全体の動作確認に使います。

> **Values**: 成長の複利 / 継続は力

### Step 7: よくある問題のトラブルシューティング

ビルドが失敗した場合はこのステップを参照してください。頻度順に列挙しています。

**問題1: インストール後に`cargo`や`rustc`が見つからない**

```powershell
# ターミナルを再起動せずにPATHを更新
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
```

**問題2: MSVCリンカーが見つからない**

```
error: linker `link.exe` not found
```

修正: Visual Studio Installerで「C++によるデスクトップ開発」ワークロードがインストールされていることを確認。

**問題3: MSI生成時のWiXツールエラー**

```
error: failed to download WiX
```

修正: MSI生成が失敗してもアプリバイナリ自体は正常にビルドされます。MSIが必要な場合は[wixtoolset.org](https://wixtoolset.org/)からWiX Toolset v3を手動インストール。または、NSISターゲットを代替使用。

**問題4: `beforeBuildCommand`が失敗する**

修正: `npx tauri build`を実行する前に、`npm run build`が単独で動作することを確認。

**問題5: 起動時に空白ウィンドウ**

修正: `tauri.conf.json`の`frontendDist`パスが`index.html`を含むディレクトリを正しく指しているか確認。

ビルドまたはランタイムの問題を診断するときに使います。

> **Values**: 温故知新 / 基礎と型

---

## Best Practices

- 正確なインストール順序を守る: MSVC → Rust → Tauri CLI → init → build
- 各ツールをインストール直後に確認してから次へ進む
- ターミナル再起動の代わりにPATH更新コマンドを使う
- 開発ビルドには`--debug`フラグを使用（リリースより高速）
- `src-tauri/`をバージョン管理に含め、`src-tauri/target/`は`.gitignore`に追加
- カスタムRustコードの代わりにTauriプラグインを使う

---

## Common Pitfalls

1. **Rustインストール後のPATH更新忘れ**
修正: PATH更新コマンドを実行するか、ターミナルセッションを再起動。

2. **tauri.conf.jsonの`beforeBuildCommand`未設定**
修正: `npm run build`を設定し、Rustコンパイル前にフロントエンドがビルドされるようにする。

3. **`frontendDist`パスの間違い**
修正: パスは`src-tauri/`からの相対。ビルドファイルがプロジェクトルートの`dist/`にある場合は`../dist`。

4. **WiXなしでMSIが動くと期待する**
修正: NSISターゲットを使うか、WiX Toolsetを別途インストール。アプリバイナリ自体は問題なく動作。

---

## Anti-Patterns

- MSVCの前にRustをインストール（リンカーがないためコンパイル失敗）
- Tauriプラグインが既に提供している操作のためにカスタムRustを書く
- 日常の開発で`npx tauri build`（リリースモード）を使用 — 代わりに`--debug`を使用
- `Cargo.lock`をバージョン管理から除外（再現可能なRustビルドを保証）
- `tauri.conf.json`に絶対パスをハードコード

---

## Quick Reference

### インストール順序

```powershell
# 1. MSVC (Visual Studio Installer → C++ Desktop workload)
# 2. Rust
winget install Rustlang.Rustup
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
rustc --version

# 3. Tauri CLI
npm install --save-dev @tauri-apps/cli
npm install @tauri-apps/api

# 4. 初期化
npx tauri init

# 5. ビルド
npx tauri build --debug
```

### Decision Table

| 状況 | アクション | 理由 |
|------|----------|------|
| 新マシンセットアップ | MSVC → Rust → Tauri CLIの順にインストール | 前提条件チェーン |
| プロジェクトにTauri追加 | `npx tauri init` | src-tauri/をスキャフォールド |
| 日常開発 | `npx tauri build --debug` | リリースビルドより高速 |
| リリース準備 | `npx tauri build` | 最適化バイナリ + インストーラー |
| ビルド失敗 | Step 7のトラブルシューティング参照 | 体系的な診断 |

### Tauri vs Electron比較

| 観点 | Tauri | Electron |
|------|-------|----------|
| バイナリサイズ | ~10MB | ~200MB |
| メモリ使用量 | ~30-50MB | ~150MB以上 |
| 描画エンジン | OSのWebView | Chromiumを同梱 |
| バックエンド | Rust | Node.js |
| セキュリティ | 許可リスト（最小限） | Node.jsフルAPI |
| Windows前提条件 | MSVC + Rust | なし |

---

## FAQ

**Q: Rustを学ぶ必要がある?**
A: ほとんどのプロジェクトでは不要です。TauriプラグインがファイルI/O、ダイアログ、クリップボードなどのTypeScript APIを提供します。Rustが必要なのはカスタムネイティブ操作だけです。

**Q: 初回ビルドがなぜ遅い?**
A: 初回はRustの依存関係ツリー全体をコンパイルします（約90秒）。2回目以降はキャッシュを使用して大幅に高速化されます。

**Q: React/Vue/SvelteでもTauriは使える?**
A: はい。Tauriはフロントエンドに依存しません。フレームワークの開発サーバーURLを`devUrl`に、ビルド出力パスを`frontendDist`に設定してください。

**Q: macOS/Linuxは?**
A: Tauriはクロスプラットフォームビルドをサポートしています。このスキルはWindowsセットアップに焦点を当てています。macOSにはXcode CLT、Linuxにはシステムパッケージ（webkit2gtk等）が必要です。

**Q: なぜMSIとNSISの両方?**
A: MSIは企業/AD配布の標準。NSISはユーザーフレンドリーなインストーラーウィザードを提供。配布コンテキストに応じて選択してください。

---

## Resources

- [Tauri v2 ドキュメント](https://v2.tauri.app/)
- [Tauri 前提条件ガイド](https://v2.tauri.app/start/prerequisites/)
- [Rust インストールガイド](https://www.rust-lang.org/tools/install)
- [WiX Toolset](https://wixtoolset.org/)
- [WebView2 ランタイム](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)

---

## Changelog

### Version 1.0.0 (2026-02-25)
- 初版: Windows上のMSVC + Rust + Tauri CLIセットアップワークフロー
