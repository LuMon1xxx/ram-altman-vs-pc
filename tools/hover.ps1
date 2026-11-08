param([int]$X = 0, [int]$Y = 0)
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class MoveSim { [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y); }
'@
[MoveSim]::SetCursorPos($X, $Y) | Out-Null
Write-Output "moved to $X,$Y"
