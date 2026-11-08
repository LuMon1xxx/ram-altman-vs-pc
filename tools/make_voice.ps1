# Synthesize speech with Windows OneCore (WinRT) voices -> WAV files.
# Usage: powershell -File make_voice.ps1 -OutDir <assets>
param(
    [Parameter(Mandatory = $true)][string]$OutDir
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Speech

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    })[0]

function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media, ContentType = WindowsRuntime] | Out-Null
[Windows.Media.SpeechSynthesis.SpeechSynthesisStream, Windows.Media, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null

function Save-WinRtSpeech {
    param([string]$Text, [string]$Path, [string]$VoiceMatch, [double]$Rate = 1.0, [double]$Volume = 1.0)
    $synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
    $voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.DisplayName -like $VoiceMatch } | Select-Object -First 1
    if ($null -ne $voice) { $synth.Voice = $voice }
    $ssml = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ru-RU'>" +
    "<prosody rate='$([int]($Rate * 100))%' volume='$([int]($Volume * 100))%'>" +
    [System.Security.SecurityElement]::Escape($Text) + "</prosody></speak>"
    $stream = Await ($synth.SynthesizeSsmlToStreamAsync($ssml)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
    $reader = [Windows.Storage.Streams.DataReader]::new($stream.GetInputStreamAt(0))
    $size = [uint32]$stream.Size
    Await ($reader.LoadAsync($size)) ([uint32]) | Out-Null
    $bytes = New-Object byte[] $size
    $reader.ReadBytes($bytes)
    [IO.File]::WriteAllBytes($Path, $bytes)
    Write-Host ("  [tts] " + (Split-Path $Path -Leaf) + " " + $size + " bytes")
}

function Save-SapiSpeech {
    param([string]$Text, [string]$Path, [string]$VoiceName, [int]$Rate = 0)
    $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
    try { $s.SelectVoice($VoiceName) } catch { }
    $s.Rate = $Rate
    $s.Volume = 100
    $s.SetOutputToWaveFile($Path)
    $s.Speak($Text)
    $s.Dispose()
    Write-Host ("  [sapi] " + (Split-Path $Path -Leaf))
}

$lines = @(
    @{ f = "vo_intro1"; v = "*Pavel*"; r = 0.95; t = "Мы в OpenAI строим AGI. Но дата-центрам катастрофически не хватает памяти." },
    @{ f = "vo_intro2"; v = "*Pavel*"; r = 0.95; t = "Поэтому мы вынуждены экспроприировать оперативную память из ваших домашних ПК." },
    @{ f = "vo_intro3"; v = "*Pavel*"; r = 0.95; t = "Это ради общего блага. И ради моего дата-центра." },
    @{ f = "vo_yes"; v = "*Pavel*"; r = 1.0; t = "Спасибо за вклад! Ваш компьютер стал на один гигабайт медленнее." },
    @{ f = "vo_no1"; v = "*Pavel*"; r = 1.05; t = "Уверен? Это всего один гигабайт. Тебе хватит." },
    @{ f = "vo_laugh"; v = "*Pavel*"; r = 1.0; t = "Ха-ха-ха. Слабый компьютер." },
    @{ f = "vo_rack"; v = "*Pavel*"; r = 0.95; t = "Вызываю серверную стойку!" },
    @{ f = "vo_taunt1"; v = "*Pavel*"; r = 1.05; t = "Ещё один гигабайт!" },
    @{ f = "vo_taunt2"; v = "*Pavel*"; r = 1.0; t = "Это ради AGI!" },
    @{ f = "vo_taunt3"; v = "*Pavel*"; r = 1.0; t = "Не сопротивляйся." },
    @{ f = "vo_round2"; v = "*Pavel*"; r = 1.0; t = "Реванш? Твоя память уже в Калифорнии." },
    @{ f = "vo_mkannounce"; v = "*Zira*"; r = 0.92; t = "Test your might. Mortal Kombat!" },
    @{ f = "vo_fight"; v = "*Zira*"; r = 1.0; t = "Fight!" },
    @{ f = "vo_fatality"; v = "*Zira*"; r = 0.9; t = "Fatality! Ram is secured!" },
    @{ f = "vo_round2announce"; v = "*Zira*"; r = 0.95; t = "Round two. Fight!" }
)

foreach ($l in $lines) {
    $path = Join-Path $OutDir ($l.f + ".wav")
    try {
        Save-WinRtSpeech -Text $l.t -Path $path -VoiceMatch $l.v -Rate $l.r
    }
    catch {
        Write-Host ("  [warn] winrt failed (" + $_.Exception.Message + "), sapi fallback")
        $sapiVoice = if ($l.v -like '*Zira*') { "Microsoft Zira Desktop" } else { "Microsoft Irina Desktop" }
        Save-SapiSpeech -Text $l.t -Path $path -VoiceName $sapiVoice
    }
}
Write-Host "voice done"
