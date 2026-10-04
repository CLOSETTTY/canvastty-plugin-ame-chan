https://github.com/user-attachments/assets/6900ae77-6dd2-4d47-8ac7-bf090f33ad92

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ru.md">Русский</a> ·
  <a href="README.zh-CN.md"><strong>简体中文</strong></a>
</p>

# 💜 CanvasTTY 的 Ame-chan 插件

<p align="center">
  <strong>画布上的像素动画伙伴。</strong><br>
  ✨ 19 个动作 · 🎲 随机轮播 · 🪟 Windows · 🐧 Linux · 🍎 macOS<br>
  <a href="https://github.com/CLOSETTTY/canvastty-plugin-ame-chan/releases/tag/v1.0.0">1.0 版本</a> ·
  <a href="INSTALL.md">通过 AI 助手安装</a> ·
  <a href="NOTICE.md">图片来源</a>
</p>

为 [CanvasTTY](https://github.com/howdeploy/CanvasTTY) 画布制作的像素动画角色。Ame-chan 会呼吸、眨眼、跳舞、看手机、自拍、听音乐，还有更多动作。

<p align="center">
  <img src="assets/preview.webp" width="300" alt="透明背景上的 Ame-chan 动画预览">
</p>

## ✨ 项目概览

| 项目 | 内容 |
| --- | --- |
| 类型 | CanvasTTY 画布应用 |
| 版本 | 1.0.0 |
| 动画 | 19 个可选动作，以及 **All actions** 模式 |
| 权限 | 无需额外权限 |
| 平台 | Windows、Linux 和 Apple Silicon macOS 上的 CanvasTTY；各平台均有透明卡片补丁 |

Ame-chan 在待机时会呼吸，动作以逐帧动画播放。透明背景让角色自然地显示在画布上。可以循环播放单个动作，也可以选择 **All actions** 随机轮播。

## 🚀 安装

仓库公开后，可以直接通过链接安装插件。CanvasTTY 不支持从私有仓库链接安装。

1. 打开 **CanvasTTY → Settings → Plugins**。
2. 粘贴 https://github.com/CLOSETTTY/canvastty-plugin-ame-chan 并点击 **Inspect**。
3. 检查清单和权限，然后确认 **Install**。
4. 在 Ame-chan 插件卡片上点击 **Open**。

在角色右上方的菜单中选择动作。插件卡片可以在画布上移动和调整大小。

**通过 Codex 安装？** 将公开仓库链接发送给助手，并要求：“在 CanvasTTY 中安装 Ame-chan，按 INSTALL.md 为我的操作系统应用透明卡片补丁。” 助手需要访问本机 CanvasTTY。

## 🫧 透明卡片

动画插件使用 Windows、Linux 和 macOS 版 CanvasTTY 支持的浏览器 API，插件自身的背景透明。CanvasTTY 默认会给每个插件绘制不透明的卡片；要达到截图中的外观，还需要修改本机 CanvasTTY 的样式。补丁只影响 Ame-chan，并保留卡片、移动、缩放以及悬停控制按钮。

应用补丁前先关闭 CanvasTTY。没有补丁时动画仍可运行，但会显示 CanvasTTY 的标准卡片背景和标题栏。

### 🪟 Windows

1. 将本仓库下载为 ZIP 并解压。
2. 运行 `frameless\install-frameless.cmd`。
3. 重新打开 Ame-chan；将鼠标移到角色上即可显示控制按钮。

运行 `frameless\uninstall-frameless.cmd` 可恢复标准卡片。如果安装路径不同，请用 `-Resources` 参数将 `resources` 目录传给 `frameless.ps1`。

### 🐧 Linux（.deb）

下载并解压本仓库，在仓库根目录运行：

```sh
sudo python3 frameless/linux-transparent-card.py apply
```

如果 CanvasTTY 安装在其他位置，请添加 `--resources /path/to/CanvasTTY/resources`。重启 CanvasTTY 并打开 Ame-chan。要恢复标准卡片，先关闭 CanvasTTY，再运行 `sudo python3 frameless/linux-transparent-card.py restore`；如果安装时使用了 `--resources`，恢复时也要使用相同参数。

### 🐧 Linux（AppImage）

保留原始 AppImage。在仓库根目录运行：

```sh
python3 frameless/linux-transparent-card.py apply --appimage /path/to/CanvasTTY.AppImage
~/.local/bin/canvastty-ame-chan
```

第一条命令会在 `~/.local/share/canvastty-ame-chan/` 创建单独的补丁版 CanvasTTY；第二条命令启动它。要保持透明卡片，请使用此启动器。要恢复使用原始 AppImage，请运行 `python3 frameless/linux-transparent-card.py restore --appimage /path/to/CanvasTTY.AppImage`，然后启动原始 AppImage。

### 🍎 macOS（Apple Silicon）

保留原始 `CanvasTTY.app`，应用补丁前先关闭它。在仓库根目录运行：

```sh
python3 frameless/mac-transparent-card.py apply --app /Applications/CanvasTTY.app
open "$HOME/Applications/CanvasTTY Ame-chan.app"
```

脚本会在 `~/Applications` 创建 CanvasTTY 副本，应用相同的 Ame-chan 样式，对副本进行本地 ad-hoc 签名并验证签名。如果 CanvasTTY 位于其他位置，请修改 `--app` 后的路径。要使用透明卡片，请启动这个副本。要恢复原始应用，请关闭 CanvasTTY，运行 `python3 frameless/mac-transparent-card.py restore`，然后启动原始 `CanvasTTY.app`。

补丁会在修改过的安装中将 `app.asar` 备份为 `app.asar.bak`。CanvasTTY 更新后需要重新应用。补丁不会修改插件的精灵图。插件已在 Ubuntu 的 Chromium 中检查；尚未在实际的 Linux 或 macOS 桌面上目视验证 CanvasTTY 中的最终外观。

## 🗂️ 仓库结构

| 路径 | 内容 |
| --- | --- |
| canvastty.plugin.json、index.html | 插件清单和入口页面 |
| ame.js、ame-frames.js、ame-*.webp | 动画播放器、帧时序和精灵图 |
| assets/preview.webp | 角色动画预览 |
| frameless/ | 透明卡片 CSS 以及 Windows/Linux/macOS 应用和恢复脚本 |
| README.md、README.ru.md | 英语和俄语说明 |
| [INSTALL.md](INSTALL.md) | Codex 或其他本地助手的完整安装指南 |
| [NOTICE.md](NOTICE.md)、[SECURITY.md](SECURITY.md) | 图片来源、许可范围和安全报告 |
| tests/、.github/workflows/ | 平台检查与自动验证 |

这是非官方粉丝项目。Ame-chan 是游戏 *NEEDY STREAMER OVERLOAD* 中的角色。本仓库与游戏及其创作者没有关联。

## 📜 许可证与安全

原创代码和文档采用 [MIT 许可证](LICENSE)。角色图片和宣传媒体不在授权范围内；请参阅[许可范围与角色权利](NOTICE.md)。漏洞报告说明见[安全政策](SECURITY.md)。
