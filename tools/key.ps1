param([string]$Key = "SPACE", [int]$Times = 1, [int]$DelayMs = 250)
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class KeySim {
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint f, IntPtr e);
}
'@
$map = @{ SPACE = 0x20; ENTER = 0x0D; ESC = 0x1B; LEFT = 0x25; RIGHT = 0x27; F = 0x46; Q = 0x51 }
$vk = $map[$Key.ToUpper()]
if ($null -eq $vk) { Write-Output "unknown key $Key"; exit 1 }
for ($i = 0; $i -lt $Times; $i++) {
    [KeySim]::keybd_event([byte]$vk, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 40
    [KeySim]::keybd_event([byte]$vk, 0, 2, [IntPtr]::Zero)
    Start-Sleep -Milliseconds $DelayMs
}
Write-Output "sent $Key x$Times"
