param(
    [switch]$TestMode,
    [string]$ResearchProjectsRoot = $env:RESEARCH_PROJECTS_ROOT
)

$ErrorActionPreference = 'Stop'

function Resolve-ResearchProjectsRoot {
    param(
        [string]$ConfiguredRoot,
        [string]$StartPath
    )

    if (-not [string]::IsNullOrWhiteSpace($ConfiguredRoot)) {
        if (-not [System.IO.Path]::IsPathRooted($ConfiguredRoot)) {
            throw 'RESEARCH_PROJECTS_ROOT 或 -ResearchProjectsRoot 必须是绝对路径。'
        }
        $ResolvedRoot = [System.IO.Path]::GetFullPath($ConfiguredRoot)
        if (-not (Test-Path -LiteralPath $ResolvedRoot -PathType Container)) {
            throw "科研项目根目录不存在：$ResolvedRoot"
        }
        return $ResolvedRoot
    }

    $Current = Get-Item -LiteralPath ([System.IO.Path]::GetFullPath($StartPath))
    while ($null -ne $Current) {
        if ($Current.Name -eq '03_数据与分析') {
            $ProjectDirectory = $Current.Parent
            if ($null -ne $ProjectDirectory -and $null -ne $ProjectDirectory.Parent) {
                return $ProjectDirectory.Parent.FullName
            }
        }
        $Current = $Current.Parent
    }

    throw '无法从固定项目骨架推导科研项目根。请设置 RESEARCH_PROJECTS_ROOT，或使用 -ResearchProjectsRoot 传入绝对路径。'
}

$ResearchProjectsRoot = Resolve-ResearchProjectsRoot `
    -ConfiguredRoot $ResearchProjectsRoot `
    -StartPath $PSScriptRoot

$DailyRoot = Split-Path -Parent $PSScriptRoot
$OutputBranch = if ($TestMode) { 'test' } else { '结果' }

# ===== BEGIN PLANNED COMMANDS =====

# execution 严格按照规划表填写顺序运行命令。
# 只允许替换本区块，不得修改模板其它内容。

# ===== END PLANNED COMMANDS =====
