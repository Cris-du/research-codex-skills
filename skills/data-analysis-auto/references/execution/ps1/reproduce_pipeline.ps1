$ErrorActionPreference = 'Stop'

$WorkRecordLeaf = [System.IO.Path]::GetFullPath($PSScriptRoot)
$RunPipeline = Join-Path $WorkRecordLeaf 'run_pipeline.ps1'

if (-not (Test-Path -LiteralPath $RunPipeline -PathType Leaf)) {
    throw "同目录中找不到 run_pipeline.ps1：$RunPipeline"
}

$DailyRoot = [System.IO.Path]::GetFullPath(
    (Split-Path -Parent $WorkRecordLeaf)
)
$FormalRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $DailyRoot '结果')
)
$TestRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $DailyRoot 'test')
)
$HashReport = Join-Path $WorkRecordLeaf '复现哈希记录.txt'

if (
    (Split-Path -Parent $TestRoot) -ne $DailyRoot -or
    (Split-Path -Leaf $TestRoot) -ne 'test'
) {
    throw "test 目录定位异常：$TestRoot"
}

if (Test-Path -LiteralPath $TestRoot -PathType Container) {
    Remove-Item -LiteralPath $TestRoot -Recurse -Force
}

& $RunPipeline -TestMode

if (-not (Test-Path -LiteralPath $TestRoot -PathType Container)) {
    throw 'run_pipeline.ps1 执行后没有生成 test 目录。'
}

$TestFiles = @(
    Get-ChildItem -LiteralPath $TestRoot -Recurse -File |
        Sort-Object FullName
)

$Report = @(
    "复现时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    "工作记录目录：$WorkRecordLeaf"
    "运行脚本：$RunPipeline"
    "正式结果根：$FormalRoot"
    "测试结果根：$TestRoot"
    "测试文件数量：$($TestFiles.Count)"
    ''
)

foreach ($TestFile in $TestFiles) {
    $RelativePath = $TestFile.FullName.Substring(
        $TestRoot.TrimEnd('\\').Length + 1
    )
    $FormalFile = Join-Path $FormalRoot $RelativePath
    $FormalExists = Test-Path -LiteralPath $FormalFile -PathType Leaf

    $FormalSize = if ($FormalExists) {
        (Get-Item -LiteralPath $FormalFile).Length
    } else {
        'MISSING'
    }

    $FormalHash = if ($FormalExists) {
        (Get-FileHash -LiteralPath $FormalFile -Algorithm SHA256).Hash
    } else {
        'MISSING'
    }

    $TestSize = $TestFile.Length
    $TestHash = (
        Get-FileHash -LiteralPath $TestFile.FullName -Algorithm SHA256
    ).Hash

    $Report += @(
        "文件：$RelativePath"
        "正式文件存在：$FormalExists"
        "正式文件大小：$FormalSize"
        "正式文件SHA256：$FormalHash"
        "测试文件大小：$TestSize"
        "测试文件SHA256：$TestHash"
        ''
    )
}

$Report |
    Set-Content -LiteralPath $HashReport -Encoding UTF8

if (
    -not (Test-Path -LiteralPath $HashReport -PathType Leaf) -or
    (Get-Item -LiteralPath $HashReport).Length -eq 0
) {
    throw '复现哈希记录写入失败，保留 test 目录。'
}

Remove-Item -LiteralPath $TestRoot -Recurse -Force

Write-Host "复现哈希记录已生成：$HashReport"
