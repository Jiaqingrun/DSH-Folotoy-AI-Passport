# AI Passport DSH 插件：Windows 测试包

版本：`0.2.5`（Windows 兼容 beta）

这是一个给群友测试 **Windows 兼容性** 的本地 DSH 插件包。macOS 已回归测试；
GitHub Actions 已配置 `windows-latest` smoke test（含 `.cmd`，本轮未重跑），并且已在
**Windows 11 家庭中文版 / PowerShell 5.1 + pwsh 7.7.0 / Python 3.13.5 / Git 2.56.1 / DSH Desktop 0.2.2-rc.5**
实机上跑过安装、doctor、scanner、preflight、Git 端到端、324 字符路径、UNC 和 publish dry-run
（结果见 `docs/WINDOWS-REPORT.md`）。0.2.3 适配版另在真机上完成构建、烧录、实屏截图和社区发布；
0.2.4 只复验了发布链路，不等于新的真实发布。仍需要更多机器验证，请按下面的清单跑一遍并反馈。

测试时不要发布、不要授权、不要上传任何东西。

## 1. 前置条件

- Windows 10/11。
- DSH Desktop **0.2.2-rc.5 或更新版本**。
- Python **3.10+**，建议从 python.org 安装并勾选 **py launcher**；`python --version` 或 `py -3 --version` 至少一个可用。启动器会先探测 `py -3`，失败时回退 `python`。
- Git for Windows（安装后 `git --version` 可用；doctor/scanner 会用到）。
  没装时先装：`winget install --id Git.Git -e --source winget`，然后**重开终端**。
  注意 Windows 上通常**没有** `python3` 命令，文档里的 `python3` 一律换成 `py -3`。
- 不需要安装官方 publisher；本包不包含它，也不要尝试提交。

## 2. 解压

建议解压到简单路径，例如：

```text
C:\DSH\plugins\DSH-Folotoy-AI-Passport
```

路径有空格或中文通常也可以，但第一次测试建议用简单英文路径，减少变量。

安装后这是 **本地链接插件**：不要移动或重命名这个文件夹；要移动就先卸载再按新路径安装。

## 3. 安装插件

打开 DSH：

**Plugins → Add plugin → 选择 `DSH-Folotoy-AI-Passport` 文件夹**。

或者在 Full access 会话中执行：

```text
plugin_manager action=install_bundle target="C:\DSH\plugins\DSH-Folotoy-AI-Passport"
```

期望看到 `application: applied`、`warnings: []`。如果提示需要重启，重启 DSH Web/桌面端。

安装后可以用 `plugin_manager action=list_plugins` 自查：条目里应出现
`preset-ai-passport`，`enabled: true`、`fiberPhase: active`。

然后：

1. **新建会话**；
2. 在 Agent 选择器选 **AI Passport**；
3. 如果选择器没有它，先重启 DSH，再新建会话。

## 4. 必测 5 项

### 4.1 Python 和 Git

```powershell
py -3 --version
git --version
```

### 4.2 新会话能选到 AI Passport

新会话选择 **AI Passport**，输入：

```text
列出可用技能，并加载 passport-router，报告 base directory
```

期望：

- 能看到 9 个 Passport 技能（router / setup / build / debug / develop /
  device-test / doctor / publish / code-audit）；
- `passport-router` 的 base directory 指向解压目录下的 `...\skills\passport-router`。

### 4.3 直接运行 Python scanner

```powershell
cd C:\DSH\plugins\DSH-Folotoy-AI-Passport
py -3 skills\passport-router\scripts\scan_project.py --root . --json
```

期望：输出 JSON，`class` 为 `C`（插件目录没有固件/封面），不出现 traceback。

> 如果你手头有 AI Passport 项目，也可以把 `--root .` 换成项目目录，把 JSON 发给我；不要发 token。

### 4.4 直接运行 doctor

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
```

期望：9 个技能 PASS；publisher skill 未安装、没有 `--root` 是 WARN。
装了 Git、版本达标时退出码 0；缺 Git 时退出码 1 并给出安装提示，这是预期行为。
不要出现 `ModuleNotFoundError` 或编码错误。

### 4.5 PowerShell / cmd 包装（重点）

**先跑 `.cmd`**，它不受执行策略影响：

```powershell
skills\passport-doctor\scripts\doctor.cmd
```

再验证 `.ps1`。Windows 客户端**默认执行策略是 Restricted**，直接
`.\doctor.ps1` 会被拒绝（`因为在此系统上禁止运行脚本`），必须显式放开：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills\passport-doctor\scripts\doctor.ps1
```

两种包装都应打印同样的 PASS/WARN/FAIL，并带正确的退出码。

## 5. 反馈模板

请把下面内容贴回群里/发我：

```text
Windows 版本：
DSH 版本：
py -3 --version：
git --version：
安装结果 application/warnings：
list_plugins 里是否有 preset-ai-passport / active：
Agent 选择器是否有 AI Passport：
9 个技能是否都在：
passport-router base directory：
scanner 退出码/JSON 或报错：
doctor 退出码/输出最后 10 行：
.cmd 包装是否正常：
.ps1 是否被 ExecutionPolicy 拦截：
截图（不要包含 token/授权码）：
```

## 6. 已知边界

- 本包不包含官方 publisher skill；不要执行 `authorize`、`submit` 或上传。
- 官方 ESP-IDF 工具链可能要求 WSL 或 ESP-IDF PowerShell 终端；这是固件构建环境的要求，不是本插件脚本的要求。
- `remove_bundle` 可能残留 `node_modules/dsh-folotoy-ai-passport` 的本地链接；卸载后如遇到，删除这个单个链接再重装。
- 本测试包只做 dry-run/validate，不包含官方 publisher；真实设备/商店记录来自 0.2.3 现场验证，不能当作 0.2.4 的新发布。
- Windows 默认控制台代码页是 936/932，不是 UTF-8。本包的 Python 入口已强制按 UTF-8 输出，
  但如果你用**别的**工具（不是本包脚本）读这些输出，请按 UTF-8 解码。
- DSH Desktop 不把 `dsh` 放进 PATH，`doctor.py` 会退化读取
  `%USERPROFILE%\.dsh\dsh-runtimes\*\runtime.json` 里的 `desktopVersion`；
  也可以用 `DSH_VERSION` / `DSH_CLI` 环境变量显式指定。
- 重命名项目文件夹时，Windows 若有程序（编辑器、终端、资源管理器）占着该目录，
  会报“另一个程序正在使用此文件”；helper 会重试数次，仍失败就停下并提示，不会半途改名。
