param([int]$X = 0, [int]$Y = 0, [int]$Count = 1)
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class InputSim {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint f, IntPtr e);
    public const uint LEFTDOWN = 0x0002, LEFTUP = 0x0004, KEYUP = 0x0002;
}
'@
[InputSim]::SetCursorPos($X, $Y) | Out-Null
Start-Sleep -Milliseconds 120
for ($i = 0; $i -lt $Count; $i++) {
    [InputSim]::mouse_event([InputSim]::LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [InputSim]::mouse_event([InputSim]::LEFTUP, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 200
}
Write-Output "clicked $X,$Y x$Count"
