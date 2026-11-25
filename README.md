# DSH-Folotoy AI Passport

**Unofficial DSH agent preset for FoloToy AI Passport projects.**
**非官方 DSH Agent 预设，面向 FoloToy AI Passport 项目。**

[简体中文](#zh-cn) | [English](#english)

![DSH](https://img.shields.io/badge/DSH-%3E%3D0.2.2--rc.5-blue)
![Status](https://img.shields.io/badge/status-Windows%20beta-orange)
![License](https://img.shields.io/badge/license-MIT-green)
[![validate](https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/actions/workflows/validate.yml/badge.svg)](https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/actions/workflows/validate.yml)

---

<a id="zh-cn"></a>

## 简体中文

### 项目简介

**DSH-Folotoy AI Passport** 是一个基于 DeepSeek Harness（DSH）的 Agent 预设 /
bundle，用于辅助 FoloToy AI Passport 项目从工具链搭建、固件构建、调试、开发、
设备测试到商店发布前检查的完整工作流。

它把一组技能（skills）、一个预设和跨平台脚本打包成一个可本地安装的 DSH bundle。
安装后，在 DSH 中新建会话并选择 **AI Passport** 预设即可使用。

> **非官方项目。** 本项目由社区维护，不代表 FoloToy，也不包含 FoloToy 的固件、
> 封面、项目文件或官方发布授权。FoloToy、AI Passport 相关名称和素材归其各自
> 权利人所有。

### 当前状态

| 项目 | 状态 |
|---|---|
| 版本 | `0.2.3` |
| macOS | 已在 macOS 上完成回归测试 |
| Linux | 代码路径已实现，尚未做系统化验证 |
| Windows | **兼容代码已完成；CI 已在 windows-latest 通过 smoke test，但尚未在真实 Windows 桌面/设备上验证（beta）** |
| 商店发布 / 真机烧录 | 不在本仓库测试范围 |

Windows 兼容性的实现方式和未验证边界见
[Windows 测试说明](INSTALL-WINDOWS.md) 与 [Windows 验收清单](docs/WINDOWS.md)。

### 功能

| 技能 | 用途 |
|---|---|
| `passport-router` | 只读扫描项目，生成项目卡片（class、固件、封面、Git 状态） |
| `passport-setup` | 搭建 ESP-IDF 与 AI Passport 工具链 |
| `passport-build` | 构建、烧录、归档固件 |
| `passport-debug` | 串口/JTAG 调试与启动问题定位 |
| `passport-develop` | 在现有项目中开发功能与修复问题 |
| `passport-code-audit` | 固件完成后的严格合规与流畅性代码审计 |
| `passport-device-test` | 设备级验收与回归测试 |
| `passport-publish` | 发布前预检、商店文案检查、dry-run 和受控提交 |
| `passport-doctor` | 检查 DSH、Python、Git、技能和发布依赖是否就绪 |

### 默认行为

- **默认目标**：用户要求创建任何应用或游戏、但未指定其他平台时，默认实现
  **FoloToy AI Passport 固件**，不会静默改成桌面、网页或移动端应用。
- **文件夹跟随固件名**：固件／应用名称确定或变更后，自动把该应用的项目根
  目录改成规范名称；只改应用根目录，不改 DSH bundle、其他项目、链接式
  worktree、符号链接、用户主目录或文件系统根目录。拒绝时停止报告，不强行
  重命名；重命名后更新会话 cwd 并复查 Git 状态。
- **真实画面优先**：界面改动后默认通过 `FAP_SCREENSHOT_V1` 截取运行中固件的
  真实帧缓冲，打开实际 PNG 对照预期设计并修正；设计稿、源码、模拟器、手机
  照片或过期图片都不算真实截图。无法截取时标记 `NOT RUN`，不声称视觉通过。
- **完成前严格审计**：固件实现完成后默认执行 `passport-code-audit`，检查项目／
  安全合规与运行流畅性；P0/P1 问题阻塞完成和发布，必须附带构建门禁、真机
  测量和审计记录，不能以静态扫描干净代替。
- **三键完整使用**：每个应用或游戏必须使用 `UP`/`DOWN`/`OK` 三个功能键，
  为每个键定义明确、合乎逻辑的短按/长按/双击职责；屏幕提示必须与实体按键
  一致，禁止空置、重复或容易误触的绑定。专用电源键不当作应用功能键。
- **首次上传封面**：默认生成一张竖版 **3:4** 的实际游戏/应用渲染图作为封面，
  优先 `1152×1536`；不得使用占位图、通用设备照或无关图片。本包不内置图像
  生成模型，使用当前可用的图像工具；如果无法生成或渲染未完成，停下来请求
  用户，不上传。
- **更新封面**：更新默认**保留**已发布封面，不重新生成；只有用户明确要求
  换封面时才传新的。`publish.py` 会在 `--root` 下复用原 3:4 封面，或通过
  `--previous-cover` 指定。

### 不包含的内容

- 不包含 FoloToy 固件二进制、封面图片或具体项目文件。
- 不包含官方 `folotoy-ai-passport-publisher` 技能；该技能需要从 FoloToy 官方发布
  单独安装，并遵守其条款。
- 不包含账号授权码、token、Cookie、CSRF 或任何发布凭据。
- 不内置图像生成模型；首次上传封面需要当前可用的图像工具，无法生成时停止，
  不上传占位图。
- 不提供默认的真实发布路径：`publish.py` 默认 dry-run，不会自动加 `--auto`。

### 环境要求

- DSH `0.2.2-rc.5` 或更新版本。
- Python **3.10+**。
- Git（`passport-doctor` 和项目扫描会使用）。
- Windows 用户需要 PowerShell 5.1+；可以直接运行 `.py`，不要求 WSL/Git Bash。
- 构建固件仍然需要官方 ESP-IDF 工具链；Windows 上的 ESP-IDF 安装方式以官方文档为准。

### 安装

#### 方式 A：从 Release zip 安装

1. 从 [Releases](https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/releases)
   下载最新 zip。
2. 解压到稳定目录，例如：
   - Windows：`C:\DSH\plugins\DSH-Folotoy-AI-Passport`
   - macOS/Linux：`~/dsh-plugins/DSH-Folotoy-AI-Passport`
3. 打开 DSH，进入 **Plugins → Add plugin**，选择解压后的
   `DSH-Folotoy-AI-Passport` 仓库根目录。
4. 在 Full access 会话中也可以使用：

```text
plugin_manager action=install_bundle target="/绝对路径/DSH-Folotoy-AI-Passport"
```

5. 新建会话，在 Agent 选择器中选择 **AI Passport**。

> 这是**本地链接安装**。安装后不要直接移动或重命名目录；需要移动时先卸载，
> 再按新路径重新安装。

#### 方式 B：克隆仓库

```bash
git clone https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport.git
```

然后按方式 A 的第 3–5 步安装。仓库根目录就是 bundle 根目录，`package.json`、
`cordis.patch.yml` 和 `skills/` 都在这一层。

### 快速开始

macOS/Linux：

```bash
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root /path/to/project --json
```

Windows PowerShell：

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
py -3 skills\passport-router\scripts\scan_project.py --root C:\path\to\project --json
```

`.sh` 和 `.ps1` 是薄包装，分别定位 macOS/Linux 与 Windows 的 Python。
PowerShell 执行策略拦截 `.ps1` 时，直接运行对应的 `.py` 即可。

`passport-publish` 的预检、文案检查与发布流程见
[`skills/passport-publish/SKILL.md`](skills/passport-publish/SKILL.md)；
真实提交必须由用户在明确知情后手动授权，且官方 publisher 不包含在本仓库中。

### 平台支持

| 平台 | Python 入口 | 包装 | 验证状态 |
|---|---|---|---|
| macOS | `python3` | `.sh` | 已回归测试 |
| Linux | `python3` | `.sh` | 已实现，未系统验证 |
| Windows | `py -3` / `python` | `.ps1` | 已实现，**未实机验证** |

Windows 上的具体步骤、常见问题和反馈模板见
[INSTALL-WINDOWS.md](INSTALL-WINDOWS.md)。

### 安全边界

- `scan_project.py`、`preflight.py` 和文案检查是只读/本地操作，不上传文件。
- `publish.py` 默认 dry-run；只有 `--execute --confirmed` 才会调用 `submit`。
- 本仓库的任何脚本都不会传入 `--auto`。
- 不要在 issue、截图或日志中提交授权码、token、Cookie 或个人路径。
- 固件烧录、设备操作和商店提交都有真实风险；请先备份并自行确认。

### 仓库结构

```text
.
├── cordis.patch.yml          # DSH bundle 补丁：预设和技能发现
├── package.json              # bundle 元数据
├── INSTALL-WINDOWS.md        # Windows 测试说明（中文）
├── docs/WINDOWS.md           # Windows 验收清单（英文）
├── docs/DETAIL.md            # 设计与实现细节
├── skills/                   # 9 个技能
├── locale/                   # 中英文界面文案
├── LICENSE                   # MIT
├── NOTICE.md                 # 第三方技能与来源说明
├── LICENSES/                 # 上游许可证全文
└── .github/workflows/        # 跨平台 smoke test
```

### 开发与验证

```bash
python3 -m compileall -q skills tests
python3 -m unittest discover -s tests -v
npm pack --dry-run
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root . --json
```

上述命令应在 macOS 和 Linux 通过；Windows 的 PowerShell 包装由 CI 和人工验收
共同确认。发布相关脚本需要真实项目和 publisher 才能完整验证，不能把 dry-run
当作真实提交。

### 贡献、许可与免责声明

- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全问题：[SECURITY.md](SECURITY.md)
- 行为准则：[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 变更记录：[CHANGELOG.md](CHANGELOG.md)
- 许可证：[MIT](LICENSE)；内置的 5 个 FoloToy 技能按其 MIT 许可证分发，详见
  [NOTICE.md](NOTICE.md) 和 [LICENSES/FoloToy-MIT.txt](LICENSES/FoloToy-MIT.txt)。

本项目按“现状”提供，不附带任何明示或暗示担保。使用本预设进行固件构建、烧录、
设备测试或商店发布所造成的任何后果，由使用者自行承担。

---

<a id="english"></a>

## English

### Overview

**DSH-Folotoy AI Passport** is an unofficial DeepSeek Harness (DSH) agent preset /
bundle for FoloToy AI Passport projects. It supports the workflow from toolchain
setup and firmware builds through debugging, development, device testing, and
pre-publication checks.

The bundle combines a set of skills, an agent preset, and cross-platform scripts
into a locally installable DSH bundle. After installation, create a new DSH
session and select the **AI Passport** preset.

> **Unofficial project.** This repository is community-maintained, is not
> affiliated with or endorsed by FoloToy, and does not contain FoloToy firmware,
> cover images, project files, or publishing authorization. FoloToy and AI
> Passport names and assets belong to their respective owners.

### Status

| Item | Status |
|---|---|
| Version | `0.2.3` |
| macOS | Regression-tested on macOS |
| Linux | Code paths implemented; not systematically validated |
| Windows | **Compatibility implemented; CI smoke test passes on windows-latest, but real Windows desktop/device validation is still pending (beta)** |
| Store publishing / device flashing | Out of scope for this repository's tests |

See [INSTALL-WINDOWS.md](INSTALL-WINDOWS.md) and
[docs/WINDOWS.md](docs/WINDOWS.md) for the Windows implementation and
verification boundaries.

### Features

| Skill | Purpose |
|---|---|
| `passport-router` | Read-only project scan and project card (class, firmware, cover, Git state) |
| `passport-setup` | ESP-IDF and AI Passport toolchain setup |
| `passport-build` | Build, flash, and archive firmware |
| `passport-debug` | Serial/JTAG debugging and boot issue diagnosis |
| `passport-develop` | Feature development and fixes in existing projects |
| `passport-code-audit` | Strict compliance and smoothness audit after firmware completion |
| `passport-device-test` | Device-level acceptance and regression testing |
| `passport-publish` | Preflight, store-copy checks, dry-run, and controlled submission |
| `passport-doctor` | Check DSH, Python, Git, skills, and publishing prerequisites |

### Defaults

- **Default target:** when the user asks to create an application or game and
  names no other platform, build **FoloToy AI Passport firmware**. Do not
  silently substitute a desktop, web, or mobile app.
- **Folder follows the firmware name:** once the app/firmware name is final or
  changes, rename that app's project root to the normalized name. Rename only
  the app root, never the DSH bundle, another project, a linked worktree, a
  symlink, the home directory, or a filesystem root. If the helper refuses,
  stop and report; do not force it. After renaming, switch cwd and recheck Git
  status.
- **Real pixels first:** after a UI change, capture the running firmware
  framebuffer through `FAP_SCREENSHOT_V1`, open the actual PNG, compare every
  changed screen/state with the intended design, fix the firmware, and recapture.
  A mockup, source review, emulator, phone photo, or stale image is not a real
  capture. If capture is unavailable, mark it `NOT RUN`; never claim a visual pass.
- **Strict completion audit:** after firmware implementation, load
  `passport-code-audit` and audit project/security compliance and runtime
  smoothness before declaring done or publishing. P0/P1 findings block
  completion; build gates, real-device measurements, and an audit record are
  required, and a clean static scan is not enough.
- **Full button use:** every application/game must use all three function
  buttons (`UP`/`DOWN`/`OK`) with distinct, logical short/long/double actions.
  On-screen hints must match the real keys; no dead, duplicated, or accidental
  bindings. The dedicated power button is not an application key.
- **First-upload cover:** generate a portrait **3:4** render of the actual
  finished game/app as the cover by default, preferably `1152×1536`. Never use a
  placeholder, generic device photo, or unrelated image. This bundle does not
  include an image model; use available image tooling. If rendering is
  unavailable or unfinished, stop and ask the user rather than uploading.
- **Update cover:** preserve the published cover by default; do not regenerate
  it. Replace it only when the user explicitly asks. `publish.py` reuses the
  existing exact 3:4 cover found under `--root`, or the path passed with
  `--previous-cover`.

### Not included

- No FoloToy firmware binaries, cover images, or project files.
- No official `folotoy-ai-passport-publisher` skill. Install it separately from
  FoloToy's official release and follow its terms.
- No authorization codes, tokens, cookies, CSRF values, or publishing credentials.
- No bundled image-generation model. A first-upload cover uses available image
  tooling; when generation is unavailable, stop instead of uploading a placeholder.
- No automatic publishing path: `publish.py` is dry-run by default and never adds
  `--auto`.

### Requirements

- DSH `0.2.2-rc.5` or newer.
- Python **3.10+**.
- Git (used by `passport-doctor` and project scans).
- Windows: PowerShell 5.1+; the `.py` entry points work without WSL or Git Bash.
- Firmware builds still require the official ESP-IDF toolchain. Follow FoloToy and
  Espressif's official installation guidance on Windows.

### Installation

#### Option A: Release zip

1. Download the latest zip from
   [Releases](https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/releases).
2. Extract it to a stable directory, for example:
   - Windows: `C:\DSH\plugins\DSH-Folotoy-AI-Passport`
   - macOS/Linux: `~/dsh-plugins/DSH-Folotoy-AI-Passport`
3. In DSH, open **Plugins → Add plugin** and select the extracted repository root
   (the directory containing `package.json` and `cordis.patch.yml`).
4. Alternatively, from a Full access session:

```text
plugin_manager action=install_bundle target="/absolute/path/DSH-Folotoy-AI-Passport"
```

5. Create a new session and select the **AI Passport** agent preset.

> This is a **local link installation**. Do not move or rename the directory after
> installation. Remove the bundle, move the directory, and reinstall it instead.

#### Option B: Clone the repository

```bash
git clone https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport.git
```

Then follow steps 3–5 above. The repository root is the bundle root: `package.json`,
`cordis.patch.yml`, and `skills/` live at the top level.

### Quick start

macOS/Linux:

```bash
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root /path/to/project --json
```

Windows PowerShell:

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
py -3 skills\passport-router\scripts\scan_project.py --root C:\path\to\project --json
```

The `.sh` and `.ps1` files are thin launchers that locate Python on macOS/Linux and
Windows respectively. If execution policy blocks a `.ps1`, run the corresponding
`.py` directly.

The publishing preflight, copy checks, and controlled workflow are documented in
[`skills/passport-publish/SKILL.md`](skills/passport-publish/SKILL.md). A real
submission requires explicit, informed user authorization; the official publisher
is not bundled here.

### Platform support

| Platform | Python entry | Launcher | Validation |
|---|---|---|---|
| macOS | `python3` | `.sh` | Regression-tested |
| Linux | `python3` | `.sh` | Implemented; not systematically tested |
| Windows | `py -3` / `python` | `.ps1` | Implemented; **not yet tested on real Windows** |

See [INSTALL-WINDOWS.md](INSTALL-WINDOWS.md) for the Windows steps, known issues,
and the feedback template.

### Security boundaries

- `scan_project.py`, `preflight.py`, and copy checks are read-only/local and do not
  upload files.
- `publish.py` is dry-run by default. Only `--execute --confirmed` invokes `submit`.
- No script in this repository adds `--auto`.
- Never include authorization codes, tokens, cookies, or personal paths in issues,
  screenshots, or logs.
- Firmware flashing, device operations, and store submissions carry real risk.
  Back up first and verify before acting.

### Repository layout

```text
.
├── cordis.patch.yml          # DSH bundle patch: preset and skill discovery
├── package.json              # bundle metadata
├── INSTALL-WINDOWS.md        # Windows test guide (Chinese)
├── docs/WINDOWS.md           # Windows acceptance checklist (English)
├── docs/DETAIL.md            # design and implementation details
├── skills/                   # 9 skills
├── tests/                    # publish cover-policy regression tests
├── locale/                   # Chinese/English UI strings
├── LICENSE                   # MIT
├── NOTICE.md                 # third-party skills and provenance
├── LICENSES/                 # upstream license texts
└── .github/workflows/        # cross-platform smoke test
```

### Development and validation

```bash
python3 -m compileall -q skills tests
python3 -m unittest discover -s tests -v
npm pack --dry-run
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root . --json
```

These commands should pass on macOS and Linux. Windows PowerShell launchers are
covered by CI and manual acceptance. Publishing scripts require a real project and
the external publisher for full validation; a dry-run must not be treated as a real
submission.

### Contributing, license, and disclaimer

- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security: [SECURITY.md](SECURITY.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- License: [MIT](LICENSE). The five upstream FoloToy skills are distributed under
  their MIT license; see [NOTICE.md](NOTICE.md) and
  [LICENSES/FoloToy-MIT.txt](LICENSES/FoloToy-MIT.txt).

This project is provided "as is", without any express or implied warranty. Users
are responsible for any consequences of firmware builds, flashing, device tests,
or store submissions performed with this preset.
