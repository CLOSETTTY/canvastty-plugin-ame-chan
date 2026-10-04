https://github.com/user-attachments/assets/6900ae77-6dd2-4d47-8ac7-bf090f33ad92

<p align="center">
  <a href="README.md"><strong>English</strong></a> ·
  <a href="README.ru.md">Русский</a> ·
  <a href="README.zh-CN.md">简体中文</a>
</p>

# 💜 Ame-chan for CanvasTTY

<p align="center">
  <strong>Your animated pixel companion on the canvas.</strong><br>
  ✨ 19 activities · 🎲 Shuffled actions · 🪟 Windows · 🐧 Linux · 🍎 macOS<br>
  <a href="https://github.com/CLOSETTTY/canvastty-plugin-ame-chan/releases/latest">Latest release</a> ·
  <a href="INSTALL.md">Install with an AI agent</a> ·
  <a href="NOTICE.md">Artwork provenance</a>
</p>

An animated pixel character for the [CanvasTTY](https://github.com/howdeploy/CanvasTTY) canvas. Ame-chan breathes, blinks, dances, checks her phone, takes selfies, listens to music, and more.

<p align="center">
  <img src="assets/preview.webp" width="300" alt="Animated preview of Ame-chan on a transparent background">
</p>

## ✨ At a glance

| Detail | Description |
| --- | --- |
| Type | CanvasTTY canvas app |
| Version | 1.0.1 |
| Animation | 19 selectable activities plus an **All actions** mode |
| Permissions | None |
| Platform | CanvasTTY on Windows, Linux, and Apple Silicon macOS; transparent-card patch for each |

Ame-chan has an idle breathing loop and frame-by-frame actions. The transparent background lets her sit directly on your canvas. Choose one action to loop it, or use **Всё подряд** (All actions) for a shuffled sequence. The picker labels are in Russian.

## 🛠️ Tech stack

| Part | Technology |
| --- | --- |
| Plugin | HTML, CSS, vanilla JavaScript, and the Canvas 2D API |
| Animation assets | WebP sprite sheets with frame and timing data in JavaScript |
| Transparent-card patch | CSS; PowerShell and Batch on Windows, Python 3 on Linux and macOS |

The plugin is a static CanvasTTY canvas app. It needs no framework, build step, or runtime plugin permissions.

## 🚀 Install

Install directly from this public repository's URL. CanvasTTY does not install from private repository URLs.

1. Open **CanvasTTY → Settings → Plugins**.
2. Paste https://github.com/CLOSETTTY/canvastty-plugin-ame-chan and choose **Inspect**.
3. Review the manifest and permissions, then confirm **Install**.
4. Click **Open** on the Ame-chan plugin card.

Use the menu near the character's top-right corner to select an activity. Move and resize the plugin card on the canvas as usual.

**Installing with Codex?** Send it the public repository URL and ask: “Install Ame-chan in CanvasTTY and apply the transparent-card patch for my operating system. Follow INSTALL.md.” The agent needs access to your local CanvasTTY installation.

## 🫧 Transparent canvas card

The animation uses browser APIs available in CanvasTTY on Windows, Linux, and macOS. The plugin itself has a transparent background. CanvasTTY draws an opaque card around every plugin by default, so the screenshot-like appearance also needs a local CanvasTTY stylesheet patch. The patch keeps the card, movement, resizing, and hover controls. It affects Ame-chan only.

Close CanvasTTY before applying the patch. The plugin remains usable without it, but the card will have CanvasTTY's regular background and header.

### 🪟 Windows

1. Download this repository as a ZIP and extract it.
2. Run `frameless\install-frameless.cmd`.
3. Open Ame-chan again; hover over her to reveal the controls.

Run `frameless\uninstall-frameless.cmd` to restore the original card. For a custom installation, pass its resources directory to `frameless.ps1` with `-Resources`.

### 🐧 Linux (.deb)

Download and extract this repository, then run from its root:

```sh
sudo python3 frameless/linux-transparent-card.py apply
```

If CanvasTTY is installed outside the usual location, add `--resources /path/to/CanvasTTY/resources`. Restart CanvasTTY and open Ame-chan. To restore the original card, close CanvasTTY and run `sudo python3 frameless/linux-transparent-card.py restore` with the same `--resources` argument if used for installation.

### 🐧 Linux (AppImage)

Keep the original AppImage. From this repository's root, run:

```sh
python3 frameless/linux-transparent-card.py apply --appimage /path/to/CanvasTTY.AppImage
~/.local/bin/canvastty-ame-chan
```

The first command extracts a separate, patched CanvasTTY copy in `~/.local/share/canvastty-ame-chan/`; the second starts that copy. Start CanvasTTY with this launcher to keep the transparent card. To return to the original AppImage, run `python3 frameless/linux-transparent-card.py restore --appimage /path/to/CanvasTTY.AppImage` and launch the original AppImage.

### 🍎 macOS (Apple Silicon)

Keep the original `CanvasTTY.app` and close it before applying the patch. From this repository's root, run:

```sh
python3 frameless/mac-transparent-card.py apply --app /Applications/CanvasTTY.app
open "$HOME/Applications/CanvasTTY Ame-chan.app"
```

The script copies CanvasTTY into `~/Applications`, applies the same Ame-chan styling, ad-hoc signs the copy, and checks its signature. If CanvasTTY is elsewhere, change the `--app` path. Use this copy for the transparent card. To return to the original app, close CanvasTTY, run `python3 frameless/mac-transparent-card.py restore`, and launch the original `CanvasTTY.app`.

The patches back up `app.asar` as `app.asar.bak` in each modified installation. Reapply them after CanvasTTY updates. They never change the plugin's sprite files. The Linux plugin was checked in Chromium on Ubuntu; the CanvasTTY host appearance has not yet been visually verified on physical Linux or macOS desktops.

## 🗂️ Repository guide

| Path | Contents |
| --- | --- |
| canvastty.plugin.json, index.html | Plugin manifest and entry page |
| ame.js, ame-frames.js, ame-*.webp | Animation player, timing, and sprite sheets |
| assets/preview.webp | Animated character preview |
| frameless/ | Transparent-card CSS and Windows/Linux/macOS apply and restore scripts |
| README.ru.md, README.zh-CN.md | Russian and Simplified Chinese guides |
| [INSTALL.md](INSTALL.md) | Complete installation task for Codex or another local agent |
| [NOTICE.md](NOTICE.md), [SECURITY.md](SECURITY.md) | Artwork provenance, license scope, and security reporting |
| tests/, .github/workflows/ | Platform checks and automated validation |

This is an unofficial fan project. Ame-chan is a character from *NEEDY STREAMER OVERLOAD*. This repository is not affiliated with the game or its creators.

## 📜 License and security

Original code and documentation are available under the [MIT license](LICENSE). Character artwork and promotional media are excluded; see [license scope and character rights](NOTICE.md). Read the [security policy](SECURITY.md) for reporting instructions.
