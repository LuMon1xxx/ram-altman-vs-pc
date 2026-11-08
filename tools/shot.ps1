param([string]$Path = "$env:TEMP\shot.png")
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class DpiFix { [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); }
'@
[DpiFix]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output ("{0} {1}x{2}" -f $Path, $b.Width, $b.Height)
