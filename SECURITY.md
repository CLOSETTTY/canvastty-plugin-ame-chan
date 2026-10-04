# 🛡️ Security policy

## Scope

Reports may concern the current default branch of this plugin or its optional
Windows, Linux, and macOS transparent-card scripts. There is no guaranteed response time or support for
older snapshots.

The character runs as a static CanvasTTY canvas app. Its manifest requests no
permissions and declares no native hooks or services. The optional frameless
patch is separate: it modifies a local CanvasTTY installation or creates a
patched copy. Close CanvasTTY before applying it, then launch the appropriate
installation as described in the README. Review the script before running it.

## Reporting an issue

If GitHub displays **Security → Report a vulnerability**, use that private
reporting form. Otherwise, open an [issue](https://github.com/CLOSETTTY/canvastty-plugin-ame-chan/issues)
with the title **Private security contact requested** and no sensitive details.
The maintainer can then arrange a private channel. There is currently no
dedicated security mailbox.

Do not post credentials, personal files, or exploitable details in a public
issue. In a private report, include the plugin revision, CanvasTTY version,
operating system, affected component, and minimal reproduction steps. Remove
secrets from logs and screenshots.

For CanvasTTY host vulnerabilities, follow the
[CanvasTTY security policy](https://github.com/howdeploy/CanvasTTY/security/policy).
