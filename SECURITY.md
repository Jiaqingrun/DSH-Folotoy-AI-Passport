# Security Policy

[简体中文](#简体中文) | [English](#english)

---

<a id="简体中文"></a>

## 简体中文

### 支持范围

当前维护版本为 `0.2.x`。Windows 兼容代码仍处于 beta，尚未在 Windows 实机验证；
安全报告和平台问题都欢迎。

### 报告安全问题

请不要在公开 issue 中粘贴授权码、token、Cookie、CSRF、账号截图、个人路径或
真实发布凭据。

优先使用 GitHub 的 **Private vulnerability reporting**：

<https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/security/advisories/new>

如果无法使用私密报告，请先通过 GitHub 联系 `@Jiaqingrun`，只提供最小复现信息，
不要附带凭据。我们会尽快确认并给出处理方式。

### 安全模型

- `scan_project.py`、`preflight.py` 和文案检查是只读/本地操作，不上传项目文件。
- `publish.py` 默认 dry-run；只有 `--execute --confirmed` 才调用外部 publisher 的
  `submit`。
- 本仓库不会自动添加 `--auto`，不保存授权码，不读取或打印 token/Cookie。
- 官方 `folotoy-ai-passport-publisher` 不在本仓库中；它的安装、授权和提交行为受
  FoloToy 的条款和安全模型约束。
- 使用者仍需自行审查 publisher、确认目标项目、备份固件，并对真机操作负责。

### 不在范围内

- FoloToy 官方 publisher 自身的安全问题。
- 用户自行安装的 ESP-IDF、Python、Git 或第三方工具。
- 因用户绕过确认、泄露凭据或误操作真实发布造成的问题。

---

<a id="english"></a>

## English

### Supported versions

The maintained version is `0.2.x`. Windows compatibility remains beta and has not
yet been validated on real Windows hardware; security reports and platform issues
are welcome.

### Reporting a vulnerability

Do not paste authorization codes, tokens, cookies, CSRF values, account
screenshots, personal paths, or live publishing credentials into a public issue.

Prefer GitHub **Private vulnerability reporting**:

<https://github.com/Jiaqingrun/DSH-Folotoy-AI-Passport/security/advisories/new>

If private reporting is unavailable, contact `@Jiaqingrun` on GitHub first and
provide only the minimum reproduction details without credentials. We will
acknowledge and coordinate as soon as possible.

### Security model

- `scan_project.py`, `preflight.py`, and copy checks are read-only/local and do not
  upload project files.
- `publish.py` is dry-run by default; only `--execute --confirmed` invokes the
  external publisher's `submit`.
- This repository never adds `--auto`, never stores authorization codes, and never
  reads or prints tokens or cookies.
- The official `folotoy-ai-passport-publisher` is not included. Its installation,
  authorization, and submission behavior are governed by FoloToy's terms and
  security model.
- Users must review the publisher, confirm the target project, back up firmware,
  and remain responsible for real-device operations.

### Out of scope

- Security issues in FoloToy's official publisher.
- User-installed ESP-IDF, Python, Git, or other third-party tools.
- Problems caused by bypassing confirmation, leaking credentials, or accidentally
  performing a real submission.
