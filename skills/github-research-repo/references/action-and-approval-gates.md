# 动作与授权门禁

## 初始状态路由

本地仓库不是使用本 Skill 的前置条件。先只读判定状态，再选择唯一入口：

| 本地 `<project-root>/Git/` | 目标 GitHub 仓库 | 路由 |
|---|---|---|
| 不存在或为空 | 不存在 | **Bootstrap**；如用户要求远端，再执行 **Create GitHub repository** |
| 已是 Git 仓库 | 不存在 | 审计本地仓库；如用户要求远端，再执行 **Create GitHub repository** |
| 不存在或为空 | 已存在 | **Clone** |
| 已是目标 Git 仓库但未连接 | 已存在 | **Attach** |
| 已正确连接 | 已存在 | 按请求进入 Promote、Audit、Synchronize 或 Publish |

普通非空目录、多个本地候选、多个可能远端、身份不一致或不相关历史不属于可自动路由状态；停止写入并让用户确认。Inspect 不得为了补齐状态而创建 `Git/`。

## Inspect

只读回答：

- `Git/`是否存在，是空目录、普通目录还是独立仓库；
- repo 对应哪个项目、方法范围和远端；
- 当前分支、HEAD、dirty 状态和已知 upstream 差异；
- 远端 owner/name、默认分支和可见性；
- README、目录结构和内容合同缺口；
- tracked、staged、untracked及历史中是否存在禁入风险。

不修改、不 commit、不 push、不 fetch，除非用户另行明确要求联网刷新远端状态。

## Bootstrap

顺序：

1. 确认项目根和唯一目标 `<project-root>/Git/`；目标可以尚不存在，也可以是空目录；
2. 检查项目是否已经有本地或远端方法与代码 repo；
3. 确认父目录仓库边界和目标目录无冲突；
4. 提出初始目录、README 和 `.gitignore`；
5. 获得本地初始化批准；
6. 目标不存在时创建 `Git/`，然后复制 `assets/README.template.md`和`assets/gitignore.template`并按项目事实填写；
7. 只在 `Git/` 内初始化本地 Git 仓库；
8. 运行 private 审计并报告尚未执行的 commit、远端创建和 push。

Bootstrap 不要求预先存在本地目录或 Git 仓库，也不自动创建远端。若用户的目标是“从零建立 GitHub 仓库”，在 Bootstrap 后继续执行下方远端创建门禁；远端创建、首次 commit 和首次 push 仍是可分别核验的动作。

远端创建是本 Skill 的正式能力，但必须使用下列独立门禁。

### Create GitHub repository

1. 先用只读方式确认目标 owner、repo 名、描述、本地 `Git/`、拟用远端名和可见性。
2. 搜索当前安装 GitHub 插件的工具面。存在仓库创建工具时优先用插件；不存在时使用 GitHub CLI。
3. 默认建立 private 仓库。若用户要求 public，先完整读取 [publication-audit.md](publication-audit.md)、通过 `--public` 审计并取得 public 的明确批准。
4. 创建前检查 `gh --version` 和 `gh auth status`。未安装或未认证时停止远端动作，保留已完成的安全本地工作并说明如何补足前提。
5. 展示精确命令，并取得“创建这个远端”的明确批准。对现有本地仓库的 private 创建，使用：

```text
gh repo create <owner>/<repo> --private --description <description> --source <project-root>/Git --remote <remote-name>
```

   描述为空时省略 `--description`。路径和描述使用当前 shell 的安全参数传递方式，尤其要正确处理空格、中文和引号；不把未解析占位符传给 `gh`。
6. 不在创建命令中使用 `--push`、`--add-readme`、`--gitignore` 或 `--license`。README 和 `.gitignore` 由本 Skill 管理；许可证是独立决定；首次 push 另行批准。
7. 不为了解决同名冲突自动改名或换 owner。如果远端已存在、本地已有同名但指向不同仓库的 remote、当前账户无组织权限或命名不唯一，停止并报告。
8. 创建成功后使用 `gh repo view <owner>/<repo> --json nameWithOwner,url,visibility,isPrivate,isEmpty,defaultBranchRef`、`git remote get-url <remote-name>` 和当前本地分支状态，复核实际 owner/name、URL、可见性、远端是否为空、默认分支状态和本地 remote URL。如果任一项与批准对象不一致，不 push。
9. 创建失败时保留本地结果，明确报告“未创建远端”和失败原因；不重复盲创建。

创建和首次 push 是两个独立动作。创建远端不授权 commit、push、PR、public 可见性、tag 或 release。首次 push 继续使用 Push 门禁和 GitHub 插件的最窄匹配 Skill。

初始化不批量复制项目内容，也不要求一开始填满所有工作流步骤。

## Clone

适用于目标 GitHub 仓库已存在而本地 `Git/` 不存在或为空：

1. 用 GitHub 插件只读核验 owner/repo、URL、可见性、默认分支和当前账户访问能力；不得只凭相似名称选择仓库。
2. 确认项目根、目标 `Git/`、拟用远端名和父目录仓库边界。目标为非空普通目录时停止，不覆盖或混合现有文件。
3. 展示已核验的远端与本地目标，取得本地克隆授权。
4. 插件能安全建立本地工作区时优先交给插件；否则使用当前环境中最窄的 `gh repo clone <owner>/<repo> <project-root>/Git`，再以经过核验的 URL 使用 `git clone` 作为回退。不得把 token 嵌入命令或 remote URL。
5. 克隆后复核仓库根、remote URL、当前分支、HEAD、dirty 状态、默认分支和可见性。身份不一致时停止后续写入。
6. 运行 private 审计；克隆不授权修改、commit、push、PR 或可见性变更。

认证或权限不足时报告“未克隆”，保留项目其他内容不变。不得回退为创建一个同名新仓库。

## Attach

适用于本地 `Git/` 已是预期 Git 仓库、目标远端已存在，但两者尚未连接或 remote 配置需要明确修正：

1. 只读核验本地仓库身份、提交历史、dirty 状态，以及远端 owner/repo、URL、可见性和默认分支。
2. 展示拟新增或修改的 remote 名称与 URL，并取得 Attach 授权。修改已有 remote 必须指出旧值和新值。
3. 添加或修正 remote 后立即复核实际 URL；必要的 fetch 是单独的联网读取动作，不从 Attach 授权推断。
4. 本地和远端都非空但无法证明历史相关、远端领先或分叉时停止；Attach 不授权 merge、rebase、pull、push 或用一端覆盖另一端。

Attach 不把普通非空目录初始化成仓库，也不把不相关的本地仓库强行连接到远端。

## Promote

“把这个放进去”默认只授权用户指向的文件或方法流程的本地整理：

1. 定位确切源文件或可核实的方法事实来源；
2. 展示拟复制内容、拟撰写的方法记录、拟排除项、目标位置和参数化改动；
3. 获得本地整理批准；
4. 复制并只修改 repo 副本；
5. 更新对应 README 或方法文档，包括工具版本、完整命令、参数、输入输出和执行顺序；
6. 运行 private 审计和最小测试；
7. 报告差异。

这句话不自动授权 commit、push、远端创建或公开。

## Commit

commit 的通用 Git 执行流程交给已安装的 GitHub 插件 Skill。本 Skill 只在转交前产生科研领域约束：

- 运行 private 审计；
- 运行相关最小测试；
- 列出每个允许暂存的文件及其 `03` 或已确认方法事实来源；
- 列出明确排除的用户改动；
- 将审计结果、允许文件和排除项传给 `$github` 路由的执行 Skill。

插件 Skill 负责显示实时 `git status`、完整目标 diff、拟暂存文件和 commit message，并取得 commit 的明确批准。它不得越过本 Skill 传递的文件范围。

## Push

push 的通用远端执行流程交给已安装的 GitHub 插件 Skill。本 Skill 传递：

- 确认获批 commit；
- 目标远端、owner/repo 和分支；
- private 可见性要求；
- 审计结果与本次授权边界。

插件 Skill 负责核验实时 upstream、可见性与 ahead/behind，展示确切 push 目标并取得独立批准。远端领先或分叉时停止；不自动 merge、rebase 或 force-push。

本 Skill 不自行规定通用 GitHub 分支或 PR 流程。用户要求完整分支、commit、push 和 draft PR 发布时路由到 `$yeet`；仅同步已有分支时先路由到 `$github` 选择最窄执行方式。

## Publish

公开必须满足：

1. repo、所属项目和拟公开方法范围唯一；
2. 用户明确确认当前方法内容已到可公开节点，且不存在项目、论文、合作、专利、许可或数据时点限制；
3. 当前工作树、暂存区和 tracked 文件审计通过；
4. `--public`完整历史审计通过；
5. README、数据可用性、环境、复现边界和链接已经完成；
6. 最终目录树和远端身份已经展示；
7. 用户明确批准把这个具体远端改为 public；
8. 变更后复核实际可见性和远端内容。

“方法可以分享”、投稿、送审、接受或论文发表都不自动授权远端变为 public。只有用户明确要求对具体远端执行可见性变更才进入门禁。

tag、release、许可证、CITATION、Zenodo/DOI 和归档分别说明、分别批准。

## 破坏性与恢复动作

以下动作从不顺带执行：

- 删除 repo 或远端；
- 删除用户文件；
- reset、stash、clean；
- merge、rebase；
- 历史重写；
- force-push；
- 回滚可见性；
- 删除 release 或 tag。

若敏感内容已进入历史，普通删除工作树文件不算解决。停止 commit/push/public，报告污染对象和可见远端；等待用户单独决定历史修复方案。
