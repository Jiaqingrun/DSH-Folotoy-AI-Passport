# AI Passport DSH 插件：Windows 测试包

版本：`0.2.0`（Windows 兼容 beta）

这是一个给群友测试 **Windows 兼容性** 的本地 DSH 插件包。当前只在 macOS 上做过回归测试，**Windows 实机尚未验证**，所以需要你按下面的清单跑一遍并反馈。

测试时不要发布、不要授权、不要上传任何东西。

## 1. 前置条件

- Windows 10/11。
- DSH Desktop **0.2.2-rc.5 或更新版本**。
- Python **3.10+**，建议从 python.org 安装并勾选 **py launcher**；命令行里 `py -3 --version` 应可用。
- Git for Windows（安装后 `git --version` 可用；doctor/scanner 会用到）。
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

- 能看到 8 个 Passport 技能（router / setup / build / debug / develop / device-test / doctor / publish）；
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

期望：8 个技能 PASS；publisher skill 未安装、没有 `--root` 是 WARN；退出码 0。不要出现 `ModuleNotFoundError` 或编码错误。

### 4.5 PowerShell 包装（重点）

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills\passport-doctor\scripts\doctor.ps1
```

如果被 ExecutionPolicy 拦住，改用：

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
```

并告诉我你遇到的具体报错。

## 5. 反馈模板

请把下面内容贴回群里/发我：

```text
Windows 版本：
DSH 版本：
py -3 --version：
git --version：
安装结果 application/warnings：
Agent 选择器是否有 AI Passport：
8 个技能是否都在：
passport-router base directory：
scanner 退出码/JSON 或报错：
doctor 退出码/输出最后 10 行：
.ps1 是否被 ExecutionPolicy 拦截：
截图（不要包含 token/授权码）：
```

## 6. 已知边界

- Windows 实机尚未验证；这个包就是用来补这一步的。
- 本包不包含官方 publisher skill；不要执行 `authorize`、`submit` 或上传。
- 官方 ESP-IDF 工具链可能要求 WSL 或 ESP-IDF PowerShell 终端；这是固件构建环境的要求，不是本插件脚本的要求。
- `remove_bundle` 可能残留 `node_modules/dsh-folotoy-ai-passport` 的本地链接；卸载后如遇到，删除这个单个链接再重装。
- 插件图标、商店发布、真实设备烧录不在本次测试范围。
