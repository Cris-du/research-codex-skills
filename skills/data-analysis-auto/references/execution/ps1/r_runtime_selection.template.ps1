# 仅当规划包含 R 命令时，把本固定块逐字放在规划命令区最前面。
$PlotLibraryRoot = $null

if (-not [string]::IsNullOrWhiteSpace($env:RESEARCH_PLOT_LIBRARY_ROOT)) {
    if (-not [System.IO.Path]::IsPathRooted($env:RESEARCH_PLOT_LIBRARY_ROOT)) {
        throw 'RESEARCH_PLOT_LIBRARY_ROOT 必须是绝对路径。'
    }
    $PlotLibraryRoot = [System.IO.Path]::GetFullPath(
        $env:RESEARCH_PLOT_LIBRARY_ROOT
    )
    if (-not (Test-Path -LiteralPath $PlotLibraryRoot -PathType Container)) {
        throw "RESEARCH_PLOT_LIBRARY_ROOT 指向的目录不存在：$PlotLibraryRoot"
    }
} else {
    $CompatiblePlotLibrary = Join-Path $ResearchProjectsRoot '绘图模式脚本库'
    if (Test-Path -LiteralPath $CompatiblePlotLibrary -PathType Container) {
        $PlotLibraryRoot = $CompatiblePlotLibrary
    }
}

$RscriptConfig = if ($PlotLibraryRoot) {
    Join-Path $PlotLibraryRoot 'Rscript_exe.txt'
} else {
    $null
}
$RLibFile = if ($PlotLibraryRoot) {
    $CandidateRLibFile = Join-Path $PlotLibraryRoot 'R.txt'
    if (Test-Path -LiteralPath $CandidateRLibFile -PathType Leaf) {
        $CandidateRLibFile
    } else {
        $null
    }
} else {
    $null
}

$RscriptCandidateRecords = [System.Collections.Generic.List[object]]::new()

if (-not [string]::IsNullOrWhiteSpace($env:RESEARCH_RSCRIPT)) {
    $RscriptCandidateRecords.Add([pscustomobject]@{
        Path = $env:RESEARCH_RSCRIPT.Trim()
        Origin = 'RESEARCH_RSCRIPT'
    })
}

if ($RscriptConfig -and (Test-Path -LiteralPath $RscriptConfig -PathType Leaf)) {
    Get-Content -LiteralPath $RscriptConfig -Encoding UTF8 |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith('#') } |
        ForEach-Object {
            $RscriptCandidateRecords.Add([pscustomobject]@{
                Path = $_
                Origin = $RscriptConfig
            })
        }
}

$PathRscript = Get-Command Rscript -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($PathRscript) {
    $RscriptCandidateRecords.Add([pscustomobject]@{
        Path = $PathRscript.Source
        Origin = 'PATH'
    })
}

$RscriptExe = $null
$RscriptAttempts = [System.Collections.Generic.List[string]]::new()
$SeenCandidates = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)

foreach ($Record in $RscriptCandidateRecords) {
    $CandidateText = [string]$Record.Path
    if (-not [System.IO.Path]::IsPathRooted($CandidateText)) {
        $RscriptAttempts.Add("$($Record.Origin)：$CandidateText -> 不是绝对路径")
        continue
    }

    try {
        $Candidate = [System.IO.Path]::GetFullPath($CandidateText)
    } catch {
        $RscriptAttempts.Add("$($Record.Origin)：$CandidateText -> 路径无效：$($_.Exception.Message)")
        continue
    }

    if (-not $SeenCandidates.Add($Candidate)) {
        continue
    }
    if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
        $RscriptAttempts.Add("$($Record.Origin)：$Candidate -> 文件不存在")
        continue
    }

    $Probe = $null
    try {
        $StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $StartInfo.FileName = $Candidate
        $StartInfo.Arguments = '--version'
        $StartInfo.UseShellExecute = $false
        $StartInfo.RedirectStandardOutput = $true
        $StartInfo.RedirectStandardError = $true
        $StartInfo.CreateNoWindow = $true

        $Probe = [System.Diagnostics.Process]::new()
        $Probe.StartInfo = $StartInfo
        if (-not $Probe.Start()) {
            throw '进程未能启动'
        }
        if (-not $Probe.WaitForExit(15000)) {
            $Probe.Kill()
            $Probe.WaitForExit()
            $RscriptAttempts.Add("$($Record.Origin)：$Candidate -> --version 超过 15 秒")
            continue
        }
        $ProbeExitCode = $Probe.ExitCode
    } catch {
        $RscriptAttempts.Add("$($Record.Origin)：$Candidate -> 无法启动：$($_.Exception.Message)")
        continue
    } finally {
        if ($null -ne $Probe) {
            $Probe.Dispose()
        }
    }

    if ($ProbeExitCode -eq 0) {
        $RscriptExe = $Candidate
        $RscriptAttempts.Add("$($Record.Origin)：$Candidate -> 可用，已选择")
        break
    }

    $RscriptAttempts.Add("$($Record.Origin)：$Candidate -> --version 退出码 $ProbeExitCode")
}

if (-not $RscriptExe) {
    $AttemptText = if ($RscriptAttempts.Count -gt 0) {
        $RscriptAttempts -join [Environment]::NewLine
    } else {
        '没有发现候选。请设置 RESEARCH_RSCRIPT，或把 Rscript 加入 PATH。'
    }
    throw "没有能够运行的 Rscript：$([Environment]::NewLine)$AttemptText"
}

$RLibraryArgs = if ($RLibFile) {
    @('--r-lib-file', $RLibFile)
} else {
    @()
}

Write-Host "Rscript：$RscriptExe"
Write-Host $(if ($PlotLibraryRoot) {
    "共享绘图库：$PlotLibraryRoot"
} else {
    '共享绘图库：未配置；当前任务应使用项目内参数化 R 脚本。'
})
Write-Host $(if ($RLibFile) {
    "R 包库配置：$RLibFile"
} else {
    'R 包库配置：使用 R 标准配置。'
})

# 后续每个 R 命令统一使用：
# & $RscriptExe --vanilla --encoding=UTF-8 $PlotScript @RLibraryArgs ...
