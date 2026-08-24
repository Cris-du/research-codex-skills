# Contributing

感谢你改进这套科研 Skills。贡献应提高可移植性、科研语义准确性、权限边界或可复现性，同时保持每个 Skill 的职责清晰。

## 开始之前

1. 先搜索现有 Issue 和 Pull Request，避免重复工作。
2. 较大的行为变化请先开 Issue，写清真实使用场景、当前问题、期望行为和可能影响的 Skill。
3. 不要提交真实科研数据、未发表结果、私人路径、账号、密钥、日志或机构内部文件。

## 修改原则

- 保持 Skill 目录名与 `SKILL.md` frontmatter 中的 `name` 一致。
- 触发描述应准确区分相邻 Skill，避免把一个具体失败案例扩写成普遍规则。
- 只在确有复用价值时增加 `scripts/`、`references/` 或 `assets/`。
- 路径必须使用项目相对路径、环境变量或清楚标记的占位符，不得写入个人盘符和用户名。
- 修改脚本时保持 UTF-8，并运行与风险相称的真实验证。
- 不要弱化写入确认、覆盖保护、只读审计、科研证据或复现门禁。

## 本地检查

在仓库根目录运行：

```bash
python scripts/validate_skills.py
python -m compileall -q skills scripts
```

如果修改了 PowerShell 模板，还应使用 PowerShell 解析所有 `.ps1` 文件：

```powershell
Get-ChildItem -Recurse -Filter *.ps1 | ForEach-Object {
    [scriptblock]::Create((Get-Content -LiteralPath $_.FullName -Raw)) | Out-Null
}
```

如果修改了具体业务脚本，请在隔离的临时目录中测试其可观察行为，不要使用真实项目数据作为仓库测试夹具。

## Pull Request

Pull Request 请说明：

- 改了哪些 Skill；
- 要解决的真实问题；
- 是否改变触发、授权边界、输入输出或项目结构；
- 做过哪些验证；
- 是否存在兼容性或迁移影响。

提交 Pull Request 即表示你有权贡献相关内容，并同意贡献按本仓库的 MIT License 发布。
