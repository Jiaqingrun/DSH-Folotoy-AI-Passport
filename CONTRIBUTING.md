# Contributing

[简体中文](#简体中文) | [English](#english)

---

<a id="简体中文"></a>

## 简体中文

感谢你帮助改进 DSH-Folotoy AI Passport。这个项目是社区维护的非官方 DSH bundle，
重点是让 AI Passport 的开发流程更可审计、更安全、更可移植。

### 可以贡献什么

- 修复跨平台脚本问题（macOS、Linux、Windows）。
- 改进技能说明、发布前检查和项目扫描。
- 补充 Windows 实机验证结果和可复现的 issue。
- 改进中英文文档、测试步骤和安全边界说明。

### 不要提交什么

- 不要提交固件二进制、固件构建产物、封面图片或真实项目文件。
- 不要提交 FoloToy 官方 publisher 技能或其授权材料。
- 不要提交授权码、token、Cookie、CSRF、账号截图或任何凭据。
- 不要修改五个上游 FoloToy 技能的许可证或来源说明；如需调整行为，优先在本仓库
  的 `passport-router`、`passport-publish`、`passport-doctor` 或包装层实现。

### 开发流程

1. 从 `main` 创建分支，例如 `fix/windows-path` 或 `docs/zh-readme`。
2. 修改后至少运行：

```bash
python3 -m compileall -q skills
npm pack --dry-run
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root . --json
```

Windows 相关改动请同时验证：

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
powershell -NoProfile -ExecutionPolicy Bypass -File skills\passport-doctor\scripts\doctor.ps1
```

3. 不要用 dry-run 冒充真实发布测试；发布相关改动必须明确说明未执行真实
   `submit`。
4. 提交 PR，描述改动、平台、测试命令和结果；Windows 未实机验证时要明确写出。

### 提交信息

建议使用 Conventional Commits：

```text
feat: add Windows PowerShell launcher
fix: resolve Python path on spaces
docs: clarify Windows validation status
```

### 许可

提交即表示你同意以本仓库的 MIT 许可证贡献代码；第三方材料沿用其原始许可证，
并在 `NOTICE.md` / `LICENSES/` 中保留归属。

---

<a id="english"></a>

## English

Thank you for improving DSH-Folotoy AI Passport. This is a community-maintained,
unofficial DSH bundle focused on an auditable, safer, and more portable workflow
for AI Passport projects.

### What to contribute

- Cross-platform script fixes (macOS, Linux, Windows).
- Improvements to skills, preflight checks, and project scanning.
- Windows validation reports and reproducible issues.
- Better Chinese/English documentation, test steps, and safety boundaries.

### What not to submit

- No firmware binaries, build outputs, cover images, or real project files.
- No official FoloToy publisher skill or its authorization material.
- No authorization codes, tokens, cookies, CSRF values, account screenshots, or
  credentials.
- Do not change the license or provenance of the five upstream FoloToy skills.
  Prefer implementing behavior changes in this repository's `passport-router`,
  `passport-publish`, `passport-doctor`, or wrapper layers.

### Development workflow

1. Branch from `main`, for example `fix/windows-path` or `docs/zh-readme`.
2. Before opening a PR, run at least:

```bash
python3 -m compileall -q skills
npm pack --dry-run
python3 skills/passport-doctor/scripts/doctor.py
python3 skills/passport-router/scripts/scan_project.py --root . --json
```

For Windows changes, also verify:

```powershell
py -3 skills\passport-doctor\scripts\doctor.py
powershell -NoProfile -ExecutionPolicy Bypass -File skills\passport-doctor\scripts\doctor.ps1
```

3. Do not present a dry-run as a real publishing test. Publishing changes must
   explicitly state that a real `submit` was not executed.
4. In the pull request, describe the change, platform, test commands, and results.
   If Windows was not tested on real hardware, say so explicitly.

### Commit messages

Conventional Commits are preferred:

```text
feat: add Windows PowerShell launcher
fix: resolve Python path on spaces
docs: clarify Windows validation status
```

### License

By contributing, you agree that your contribution is licensed under this
repository's MIT license. Third-party material remains under its original license,
with attribution preserved in `NOTICE.md` and `LICENSES/`.
