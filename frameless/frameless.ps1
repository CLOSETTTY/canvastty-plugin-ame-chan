# Ame-chan (Claude) frameless patch for CanvasTTY (Windows).
# apply:   unpacks resources\app.asar into resources\app, adds CSS that hides the
#          plugin card frame for ame-chan-claude only, keeps app.asar as app.asar.bak.
# restore: removes resources\app and puts app.asar back.
param(
  [ValidateSet('apply', 'restore')][string]$Action = 'apply',
  [string]$Resources = (Join-Path $env:LOCALAPPDATA 'Programs\CanvasTTY\resources')
)
$ErrorActionPreference = 'Stop'

$exe = Join-Path (Split-Path $Resources -Parent) 'CanvasTTY.exe'
$asar = Join-Path $Resources 'app.asar'
$backup = Join-Path $Resources 'app.asar.bak'
$app = Join-Path $Resources 'app'
$cssFile = Join-Path $PSScriptRoot 'frameless.css'
$hostScript = Join-Path $PSScriptRoot 'ame-chan-host.js'
$markerStart = '/* ame-chan-claude-frameless:start */'
$markerEnd = '/* ame-chan-claude-frameless:end */'

if (-not (Test-Path $exe)) { throw "CanvasTTY not found: $exe (pass -Resources <path to CanvasTTY\resources>)" }

function Stop-CanvasTTY {
  $procs = Get-Process CanvasTTY -ErrorAction SilentlyContinue
  if (-not $procs) { return }
  Write-Host 'Closing CanvasTTY...'
  $procs | ForEach-Object { [void]$_.CloseMainWindow() }
  for ($i = 0; $i -lt 20 -and (Get-Process CanvasTTY -ErrorAction SilentlyContinue); $i++) { Start-Sleep 1 }
  Get-Process CanvasTTY -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep 2
}

# Minimal asar reader: [u32 4][u32 headerSize][u32 payload][u32 jsonLen][json]..., file data at 8 + headerSize.
function Expand-Asar([string]$Archive, [string]$Destination) {
  Add-Type -AssemblyName System.Web.Extensions
  $stream = [IO.File]::OpenRead($Archive)
  try {
    $reader = New-Object IO.BinaryReader($stream)
    [void]$reader.ReadUInt32()
    $headerSize = $reader.ReadUInt32()
    [void]$reader.ReadUInt32()
    $jsonLength = $reader.ReadUInt32()
    $json = [Text.Encoding]::UTF8.GetString($reader.ReadBytes($jsonLength))
    $serializer = New-Object Web.Script.Serialization.JavaScriptSerializer
    $serializer.MaxJsonLength = [int]::MaxValue
    $serializer.RecursionLimit = 1000
    $root = $serializer.DeserializeObject($json)
    $base = 8 + [int64]$headerSize
    $unpackedRoot = "$Archive.unpacked"
    $buffer = New-Object byte[] 1048576

    $walk = {
      param($node, [string]$relative)
      foreach ($name in $node['files'].Keys) {
        $entry = $node['files'][$name]
        $rel = if ($relative) { "$relative\$name" } else { $name }
        $target = Join-Path $Destination $rel
        if ($entry.ContainsKey('files')) {
          [void](New-Item -ItemType Directory -Force -Path $target)
          & $walk $entry $rel
        } elseif ($entry.ContainsKey('unpacked') -and $entry['unpacked']) {
          $source = Join-Path $unpackedRoot $rel
          # Builds for other CPU architectures may be missing from app.asar.unpacked.
          if (Test-Path $source) { Copy-Item -LiteralPath $source -Destination $target -Force }
        } elseif ($entry.ContainsKey('offset')) {
          $stream.Position = $base + [int64]$entry['offset']
          $left = [int64]$entry['size']
          $out = [IO.File]::Create($target)
          try {
            while ($left -gt 0) {
              $read = $stream.Read($buffer, 0, [int][Math]::Min($buffer.Length, $left))
              if ($read -le 0) { throw "Unexpected end of $Archive at $rel" }
              $out.Write($buffer, 0, $read)
              $left -= $read
            }
          } finally { $out.Dispose() }
        }
      }
    }
    [void](New-Item -ItemType Directory -Force -Path $Destination)
    & $walk $root ''
  } finally { $stream.Dispose() }
}

function Add-FramelessCss {
  $htmlPath = Join-Path $app 'out\renderer\index.html'
  $html = Get-Content -Raw -Encoding UTF8 $htmlPath
  if ($html -notmatch 'href="\./(assets/[^"]+\.css)"') { throw 'Renderer stylesheet not found in index.html.' }
  $target = Join-Path $app ('out\renderer\' + ($Matches[1] -replace '/', '\'))
  $current = [IO.File]::ReadAllText($target)
  $patch = [IO.File]::ReadAllText($cssFile)
  $block = "$markerStart`n$patch`n$markerEnd"
  $start = $current.IndexOf($markerStart)
  $end = $current.IndexOf($markerEnd)
  if ($start -ge 0 -and $end -gt $start) {
    # already patched: replace the block so a newer frameless.css takes effect
    $current = $current.Substring(0, $start) + $block + $current.Substring($end + $markerEnd.Length)
    [IO.File]::WriteAllText($target, $current)
  } else {
    [IO.File]::AppendAllText($target, "`n$block`n")
  }
  $scriptTag = '<script defer src="./assets/ame-chan-host.js"></script>'
  if (-not $html.Contains($scriptTag)) {
    if ($html.Contains('</body>')) {
      $html = $html.Replace('</body>', "  $scriptTag`n</body>")
    } else {
      $html += $scriptTag
    }
    [IO.File]::WriteAllText($htmlPath, $html)
  }
  Copy-Item -LiteralPath $hostScript -Destination (Join-Path $app 'out\renderer\assets\ame-chan-host.js') -Force
}

Stop-CanvasTTY

if ($Action -eq 'apply') {
  if (Test-Path $asar) {
    # Fresh install or CanvasTTY was updated: rebuild resources\app from the current app.asar.
    if (Test-Path $app) { Remove-Item -Recurse -Force $app }
    Write-Host 'Unpacking app.asar...'
    Expand-Asar $asar $app
    if (Test-Path $backup) { Remove-Item -Force $backup }
    Rename-Item $asar 'app.asar.bak'
  } elseif (-not (Test-Path $app)) {
    throw 'Neither app.asar nor resources\app found.'
  }
  Add-FramelessCss
  Write-Host 'Frameless patch applied.'
} else {
  if (Test-Path $backup) {
    if (Test-Path $asar) { Remove-Item -Force $backup } else { Rename-Item $backup 'app.asar' }
  }
  if (Test-Path $app) { Remove-Item -Recurse -Force $app }
  Write-Host 'CanvasTTY restored.'
}

Start-Process $exe
