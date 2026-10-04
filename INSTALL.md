# 🚀 Install Ame-chan with a local AI agent

After the repository is public, give Codex or another agent this repository URL and the following task:

> Install Ame-chan in CanvasTTY and apply the transparent-card patch for my
> operating system. Follow INSTALL.md. Preserve my existing CanvasTTY settings
> and other plugins. Verify the animation and hover controls after installation.

## Complete installation

CanvasTTY installs directly from a public GitHub repository URL. Wait until this
repository is public; release ZIP files cannot be imported directly by CanvasTTY.

1. Identify the operating system and existing CanvasTTY installation.
2. Read the manifest and the platform instructions in [README.md](README.md).
   The stable plugin ID is `ame-chan-claude`; do not rename it.
3. In **CanvasTTY → Settings → Plugins**, paste the repository root URL, choose
   **Inspect**, review the manifest and permissions, then confirm **Install**.
   If already installed, use CanvasTTY's update controls. Do not overwrite the
   user's plugin registry or workspace settings with a sample configuration.
4. Obtain a local copy of this repository. Close CanvasTTY before applying its
   transparent-card patch. Use the existing script for the detected platform:

   | Platform | Apply | Launch afterward |
   | --- | --- | --- |
   | Windows | `frameless\install-frameless.cmd` | Existing CanvasTTY installation |
   | Linux .deb | `sudo python3 frameless/linux-transparent-card.py apply` | Existing CanvasTTY installation |
   | Linux AppImage | `python3 frameless/linux-transparent-card.py apply --appimage /path/to/CanvasTTY.AppImage` | `~/.local/bin/canvastty-ame-chan` |
   | Apple Silicon macOS | `python3 frameless/mac-transparent-card.py apply --app /Applications/CanvasTTY.app` | `open "$HOME/Applications/CanvasTTY Ame-chan.app"` |

   Use the README's custom-path arguments when necessary. Do not substitute an
   unrelated installation or modify other plugins' styles.
5. Open the Ame-chan contribution. Check that the character animates, the card
   background is transparent, and the picker and close/resize controls appear
   on hover. Check movement and resizing without removing the canvas card.
6. Report the installed version, patched installation or launcher, what was
   verified, and any verification that could not be performed.

## Why there are two installation steps

CanvasTTY installs static plugin files from GitHub; it does not execute repository
scripts during installation. The sandboxed plugin cannot change the host's
stylesheet. Applying the local patch is therefore a separate step of the same
installation task. No extra plugin permissions or native services are required.

The patches retain backups. Restore commands are in the [README](README.md).
Reapply the patch after a CanvasTTY update. Promotional video is hosted as a
GitHub attachment and is not included in the plugin files.
