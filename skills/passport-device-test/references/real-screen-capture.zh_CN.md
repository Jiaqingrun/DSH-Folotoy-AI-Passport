# 截取固件真实画面

默认使用运行中固件的帧缓冲截图作为视觉证据。设计稿、源码审查、模拟器窗口或
手机拍照都不能替代面板实际收到的像素。

## 前提

- 设备通过支持数据传输的 USB 线连接，端口已确认，用户已授权观察。截图是
  只读操作，不得复位、擦除、烧录或更改设置。
- 固件实现 publisher 的 `FAP_SCREENSHOT_V1` 协议，或项目有等价的只读帧缓冲
  截取路径。没有时，只能在获得实现授权后补协议；否则视觉验证标记
  `NOT RUN`。
- 二进制负载传输期间串口日志必须静默；任何混入的日志字节都会破坏图像。

## 使用官方 publisher 截取

优先使用已安装的 `folotoy-ai-passport-publisher` 技能的 `capture-screen`
命令。它会写出 PNG 及相邻的 `.fap-capture.json` 回执，包含哈希、尺寸、端口、
协议和截取时间。

```bash
capture-screen --list-ports
capture-screen --port <端口> --output docs/evidence/<候选版本>-screen.png
```

独立命令不在 `PATH` 时，直接调用 publisher 脚本：

```bash
python3 <publisher-skill>/scripts/publisher.py capture-screen --list-ports
python3 <publisher-skill>/scripts/publisher.py capture-screen --port <端口> --output <PNG>
```

Windows 使用 `py -3` 和 publisher 脚本的 Windows 路径。不得从任意设备猜测
端口；多个或不确定设备须与用户确认。保留截图命令的 stderr 和回执，不得
伪造回执。

## 协议与校验

主机发送 ASCII 行 `FAP_SCREENSHOT_V1\n`。设备回复一行头信息及恰好声明长度
的负载：

```text
FAP_SCREENSHOT_V1 <宽> <高> RGB565LE|PNG <字节数>\n
<负载>
```

`RGB565LE` 长度必须等于 `宽 * 高 * 2`；`PNG` 必须是尺寸匹配的完整 PNG。校验
保存文件：

- PNG 与回执尺寸和设备头信息一致；
- 回执哈希与 PNG 一致；
- 用 `read_image` 打开实际 PNG 检查；
- 提交或公开附件前确认不含设备密钥、凭据、token 或个人数据。

## 对比与修正

每个改动页面和状态都要截图，不只第一帧。对照预期设计及已接受参考，检查
标题、文字／字形、布局、对比度、HUD、按键提示和失败／占位状态。发现差异
应修改固件、重新构建／安装并再次截图；不得修改截图来让检查通过。最终图像
和回执与候选记录一起保存。

## 限制

截图只证明静态像素，不能证明动画连续性、输入延迟、音频、射频、温度或持续
流畅性。这些事实使用 `passport-code-audit` 的真机测量计划和项目验收指南。
端口、协议、授权或新鲜截图不可用时报告 `NOT RUN` 及剩余动作；绝不把模拟器、
设计稿或过期图片称为真实截图。
