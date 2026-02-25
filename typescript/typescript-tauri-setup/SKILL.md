---
name: typescript-tauri-setup
description: Set up Tauri v2 desktop app environment with MSVC, Rust, and Tauri CLI on top of a TypeScript project. Use when building a lightweight desktop app from an existing TypeScript/HTML/CSS codebase.
metadata:
  author: RyoMurakami1983
  tags: [tauri, rust, msvc, desktop, typescript, windows]
  invocable: false
---

# Set Up a Tauri Desktop App Environment

Single-workflow guide for adding Tauri v2 desktop application capabilities to an existing TypeScript project. Covers MSVC C++ build tools, Rust toolchain, Tauri CLI installation, project initialization, and first build verification on Windows.

## When to Use This Skill

Use this skill when:
- Converting a TypeScript/HTML/CSS web project into a standalone desktop app
- Setting up Tauri for the first time on a Windows development machine
- Onboarding a team member who needs to build Tauri apps locally
- Troubleshooting Tauri build failures (MSVC, Rust, WiX)
- Choosing between Tauri and Electron for a lightweight desktop distribution

---

## Related Skills

- **`typescript-setup-dev-environment`** — **Prerequisite**: Complete this skill first to establish Node.js + TypeScript toolchain
- **`git-initial-setup`** — Protect main branch before first commit
- **`git-commit-practices`** — Commit Tauri setup changes as atomic units

---

## Dependencies

- `typescript-setup-dev-environment` completed (Node.js 20+, npm, TypeScript)
- Visual Studio 2022+ with C++ Desktop workload (required for MSVC linker)
- Windows 10/11 with WebView2 runtime (pre-installed on modern Windows)
- Internet access for Rust and crate downloads

---

## Core Principles

1. **Prerequisite chain** — Each tool depends on the previous one; follow the exact order (基礎と型)
2. **Verify each step** — Confirm installation before proceeding to avoid cascading failures (基礎と型)
3. **Minimal Rust knowledge** — Tauri plugins handle most native operations; Rust code is rarely needed (余白の設計)
4. **Reproducible builds** — Document exact versions and configuration for team reproducibility (温故知新)
5. **Lightweight by design** — Tauri uses the OS WebView, producing ~10MB binaries vs Electron's ~200MB (成長の複利)

---

## Why Tauri: Context for C# and Python Developers

Tauri is a **container that ships your existing web UI (HTML/CSS/TypeScript) as a desktop application**.

| Comparison | C# + WPF | Python + Tkinter | TypeScript + Tauri |
|-----------|---------|-----------------|-------------------|
| UI approach | XAML | Python GUI | HTML/CSS (same as web) |
| Binary size | ~50MB | ~30MB (PyInstaller) | **~10MB** |
| Backend language | C# | Python | Rust (rarely touched) |
| Distribution | MSIX/ClickOnce | PyInstaller/exe | **MSI/NSIS** |

**Why you don't need to learn Rust**: Tauri plugins provide TypeScript APIs for file saving, dialog display, clipboard, and other native operations. You only write Rust for custom features not covered by plugins.

```
What you write:
  TypeScript (95%) → UI, logic, rendering
  tauri.conf.json (5%) → configuration

What Tauri handles:
  Rust → security, native APIs, binary generation
  WebView2 → HTML/CSS/JS display
```

---

## Workflow: Set Up Tauri Desktop App Environment

### Step 1: Install MSVC C++ Build Tools

Install the Microsoft Visual C++ build tools required by the Rust compiler's linker. This is equivalent to installing a C++ compiler for native dependencies.

**Option A: Via Visual Studio Installer (GUI)**

1. Open Visual Studio Installer
2. Select your Visual Studio edition → Modify
3. Check **"Desktop development with C++"** workload
4. Click Modify and wait for installation

**Option B: Via command line**

```powershell
# Download and run the Visual Studio Installer
winget install Microsoft.VisualStudio.2022.Community

# Then add the C++ workload via Installer GUI
```

**Verification:**

```powershell
# Confirm MSVC is accessible (path varies by VS version)
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
cl.exe
```

Use when setting up a new development machine for Rust/Tauri compilation.

> **Values**: 基礎と型 / 継続は力

### Step 2: Install Rust

Install the Rust toolchain via `rustup`. Rust is the backend language Tauri uses — but for most projects, you interact with it minimally.

```powershell
# Install via winget
winget install Rustlang.Rustup

# CRITICAL: Refresh PATH after installation
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Verify
rustc --version
cargo --version
```

**Why Rust?** Tauri uses Rust for its tiny runtime and security model. You rarely write Rust code directly — plugins provide TypeScript APIs for file I/O, dialogs, and other native operations.

Use when installing Rust for the first time on a development machine.

> **Values**: 基礎と型 / 余白の設計

### Step 3: Install Tauri CLI

Add the Tauri CLI and API packages to your existing TypeScript project.

```powershell
# Dev dependency: CLI for build/dev commands
npm install --save-dev @tauri-apps/cli

# Runtime dependency: TypeScript API for Tauri features
npm install @tauri-apps/api
```

**Verification:**

```powershell
npx tauri --version
```

Use when adding Tauri to an existing TypeScript project.

> **Values**: 基礎と型 / 継続は力

### Step 4: Initialize Tauri Project

Run the interactive initializer to create the `src-tauri/` directory structure.

```powershell
npx tauri init
```

The initializer asks:
1. **App name** — Your application name (e.g., `my-app`)
2. **Window title** — Display title (e.g., `My Application`)
3. **Frontend dist path** — Relative path to built frontend (e.g., `../dist`)
4. **Frontend dev URL** — Dev server URL (e.g., `http://localhost:1420`)
5. **Frontend build command** — Command to build frontend (e.g., `npm run build`)
6. **Frontend dev command** — Command to start dev server (can be empty)

**Result structure:**

```
src-tauri/
├── src/
│   ├── lib.rs          # Rust entry point (auto-generated)
│   └── main.rs         # Windows entry point
├── capabilities/
│   └── default.json    # Security permissions
├── icons/              # App icons (default placeholders)
├── Cargo.toml          # Rust dependencies
├── tauri.conf.json     # Central configuration
└── build.rs            # Build script
```

Use when adding Tauri to a project for the first time.

> **Values**: 基礎と型 / 余白の設計

### Step 5: Configure tauri.conf.json

Customize the central configuration file for your application.

```json
{
  "$schema": "https://raw.githubusercontent.com/nicbarker/tauri/dev/.schema/config.schema.json",
  "productName": "My Application",
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
        "title": "My Application",
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

**Key settings:**
- `frontendDist` — Where your built HTML/CSS/JS lives (relative to `src-tauri/`)
- `beforeBuildCommand` — Runs before Rust compilation (typically `npm run build`)
- `bundle.targets` — Installer formats (`msi` for enterprise, `nsis` for general)

Use when customizing the Tauri app for your specific project.

> **Values**: 基礎と型 / ニュートラル

### Step 6: Build and Verify

Run the first build to confirm everything works end-to-end.

```powershell
# Debug build (faster compilation, larger binary)
npx tauri build --debug
```

**Expected output:**

```
   Compiling my-app v0.1.0
    Finished `dev` profile target(s) in ~90s
        Info app.exe (approximately 10-15MB)
```

The compiled binary is at:
```
src-tauri/target/debug/my-app.exe
```

**First build takes ~90 seconds** (Rust compilation). Subsequent builds use cache and are much faster (~10-20s for frontend-only changes).

Use when verifying the complete build pipeline works.

> **Values**: 成長の複利 / 継続は力

### Step 7: Troubleshoot Common Issues

Reference this step when builds fail. Issues are listed by frequency.

**Issue 1: `cargo` or `rustc` not found after install**

```powershell
# Refresh PATH without restarting terminal
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
```

**Issue 2: MSVC linker not found**

```
error: linker `link.exe` not found
```

```powershell
# ❌ Wrong: Rust installed before MSVC — linker missing
rustc --version  # works
cargo build      # fails: linker `link.exe` not found

# ✅ Correct: Install MSVC first, then Rust
# Visual Studio Installer → "Desktop development with C++" → Modify
cargo build      # succeeds
```

Fix: Ensure "Desktop development with C++" workload is installed in Visual Studio Installer.

**Issue 3: WiX tools error during MSI generation**

```
error: failed to download WiX
```

Fix: The app binary builds fine even if MSI generation fails. For MSI, install WiX Toolset v3 manually from [wixtoolset.org](https://wixtoolset.org/). Alternatively, use NSIS target instead.

**Issue 4: `beforeBuildCommand` fails**

Fix: Ensure `npm run build` works independently before running `npx tauri build`.

**Issue 5: Blank window on launch**

Fix: Verify `frontendDist` path in `tauri.conf.json` points to the directory containing your `index.html`.

Use when diagnosing build or runtime failures.

> **Values**: 温故知新 / 基礎と型

---

## Best Practices

- Follow the exact installation order: MSVC → Rust → Tauri CLI → init → build
- Verify each tool immediately after installation before proceeding
- Refresh PATH after Rust installation instead of restarting the terminal
- Use `--debug` flag for development builds (faster than release)
- Keep `src-tauri/` in version control but add `src-tauri/target/` to `.gitignore`
- Use Tauri plugins for native operations instead of writing custom Rust code

---

## Common Pitfalls

1. **Forgetting to refresh PATH after Rust install**
Fix: Run the PATH refresh command or restart the terminal session.

2. **Missing `beforeBuildCommand` in tauri.conf.json**
Fix: Set to `npm run build` so frontend is built before Rust compilation.

3. **Wrong `frontendDist` path**
Fix: The path is relative to `src-tauri/`. If your built files are in `dist/` at project root, use `../dist`.

4. **Expecting MSI to work without WiX**
Fix: Use NSIS target or install WiX Toolset separately. The app binary works regardless.

---

## Anti-Patterns

- Installing Rust before MSVC (compilation will fail without a linker)
- Writing custom Rust for operations that Tauri plugins already provide
- Using `npx tauri build` (release mode) for daily development — use `--debug` instead
- Ignoring `Cargo.lock` in version control (it ensures reproducible Rust builds)
- Hardcoding absolute paths in `tauri.conf.json`

---

## Quick Reference

### Installation order

```powershell
# 1. MSVC (via Visual Studio Installer → C++ Desktop workload)
# 2. Rust
winget install Rustlang.Rustup
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
rustc --version

# 3. Tauri CLI
npm install --save-dev @tauri-apps/cli
npm install @tauri-apps/api

# 4. Initialize
npx tauri init

# 5. Build
npx tauri build --debug
```

### Decision Table

| Situation | Action | Why |
|-----------|--------|-----|
| New machine setup | Install MSVC → Rust → Tauri CLI in order | Prerequisite chain |
| Adding Tauri to project | `npx tauri init` | Scaffolds src-tauri/ |
| Daily development | `npx tauri build --debug` | Faster than release build |
| Preparing release | `npx tauri build` | Optimized binary + installer |
| Build fails | Check Step 7 troubleshooting | Systematic diagnosis |

### Tauri vs Electron comparison

| Aspect | Tauri | Electron |
|--------|-------|----------|
| Binary size | ~10MB | ~200MB |
| Memory usage | ~30-50MB | ~150MB+ |
| Rendering engine | OS WebView | Bundled Chromium |
| Backend | Rust | Node.js |
| Security model | Allowlist (minimal) | Full Node.js API |
| Windows prerequisite | MSVC + Rust | None |

---

## FAQ

**Q: Do I need to learn Rust?**
A: For most projects, no. Tauri plugins provide TypeScript APIs for file I/O, dialogs, clipboard, and more. You only need Rust for custom native operations.

**Q: Why is the first build so slow?**
A: The first build compiles the entire Rust dependency tree (~90s). Subsequent builds use cached artifacts and are much faster.

**Q: Can I use Tauri with React/Vue/Svelte?**
A: Yes. Tauri is frontend-agnostic. Set your framework's dev server URL as `devUrl` and build output path as `frontendDist`.

**Q: What about macOS/Linux support?**
A: Tauri supports cross-platform builds. This skill focuses on Windows setup. macOS requires Xcode CLT; Linux requires system packages (webkit2gtk, etc.).

**Q: Why MSI and NSIS as bundle targets?**
A: MSI is standard for enterprise/AD deployment. NSIS provides a more user-friendly installer wizard. Choose based on your distribution context.

---

## Resources

- [Tauri v2 documentation](https://v2.tauri.app/)
- [Tauri prerequisites guide](https://v2.tauri.app/start/prerequisites/)
- [Rust installation guide](https://www.rust-lang.org/tools/install)
- [WiX Toolset](https://wixtoolset.org/)
- [WebView2 runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)

---

## Changelog

### Version 1.0.0 (2026-02-25)
- Initial release: MSVC + Rust + Tauri CLI setup workflow for Windows
