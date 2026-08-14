# XLSkills — DeepSeek Harness (DSH) 版

`dev-pm-flow` / `requesting-code-review` / `systematic-debugging` 的 DSH 原生适配版。
与 Hermes 版同源：流程、铁律、双轴审查、fail-closed JSON、单一事实源全部继承；工具与机制换成 DSH 平台，并按 DSH 的并行能力做了强化。

## 工具映射（Hermes → DSH）

| 用途 | Hermes 版 | DSH 版 |
|---|---|---|
| 派子代理 | `delegate_task(tasks=[...])` | `subagent` / `subagent_fork`（**同一条消息批量派发 = 并行执行**） |
| 大规模编排 | — | `workflow`（见 `requesting-code-review/references/dual-axis-review.md`） |
| 改文件 | `patch` / `write_file` | `edit` / `write`（`read` 前置是平台强制的 read-before-write） |
| 搜代码 | `search_files` | `grep` / `glob` |
| 读文件 | `read_file` | `read` |
| 终端 | `terminal` | `pwsh`（Windows）/ bash |
| 网络搜索 | `web_search` | `web_search`（同名） |
| 方案确认 | 对话确认 | **plan mode**（`exit_plan_mode`）或 `ask_user_question` |
| 任务票 | 方案文件 | `todo_write`（结构化任务列表） |
| 跨轮持久化 | `.agent/plans/` 文件 | `.agent/plans/` 文件 + `create_goal` / `update_goal` |
| 后台命令 | — | `pwsh` + `run_in_background: true`，`job_output` 收集、`job_kill` 终止 |
| 子代理控制 | — | `send_message` / `interrupt_agent` / `list_agents` |
| 写权限护栏 | 文本铁律 | sandbox + 审批策略（机制级强制） |

## DSH 并行化设计（本版核心增强）

DSH agent-loop 默认 `maxParallelToolCalls = 10`：**同一条消息里的多个 `subagent` 调用并行执行**（后台/可继续子代理启动后不占并发槽，可继续加派）。三个技能据此强化：

- `dsh-dev-pm-flow` ④：🔴 重型任务按垂直切片 fan-out —— 一条消息批量派多个开发子代理并行（文件隔离规则不变，冲突文件串行）。
- `dsh-requesting-code-review` Step 5：双轴审查一次批量派发——大 diff 按文件组拆分，每组一个 Standards 审查员 + 1 个 Spec 审查员，全部同一消息发出（上限约 10 个）；或打包成 workflow 用 schema 强校验 JSON。
- `dsh-systematic-debugging` Phase 3：多个互斥假设并行验证；多组件证据收集并行。
- 所有构建/测试/长命令用后台任务，不忙等。

## 安装

DSH 技能发现根（rank 升序，来自 `dsh-skill-filesystem`）：

| 层级 | 路径 |
|---|---|
| 项目 | `<项目根>/.dsh/skills/` |
| 项目 | `<项目根>/.agents/skills/` |
| 用户 | `~/.dsh/skills/`（`$DSH_HOME`） |
| 用户 | `~/.agents/skills/`（`$DSH_AGENTS_HOME`） |

```powershell
# 用户级安装（Windows PowerShell）
Copy-Item dev-pm-flow, requesting-code-review, systematic-debugging -Destination "$env:USERPROFILE\.dsh\skills\" -Recurse
```

格式要求（DSH `skill-filesystem` 提供方）：目录名 = 技能名（kebab-case），frontmatter 至少含 `name` + `description`；可选 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`。目录下可带 `references/`、`scripts/`、`assets/` 等资源。

## 单一事实源

- `.NET` pattern 库复用仓库级 `requesting-code-review/references/dotnet.md`（Hermes/DSH 共用一份，不复制，防双份维护漂移）。其命令是 bash/grep 语法，pwsh 等价写法：
  - `git diff --cached | grep "^+[^+]" | grep -iE '<pattern>'` → `git diff --cached | Select-String -Pattern '^\+[^\+]' | Select-String -Pattern '<pattern>'`
  - 或全库搜索用 `git grep -n -E '<pattern>' -- <files>`
- 其他技术栈按同样约定新增 `references/<stack>.md`。

## 铁律（继承 Hermes 版，未放宽）

1. 方案没确认不动手
2. 任何改变历史或远端状态的操作（commit / push / force push / reset --hard / branch -D / clean -fd / rebase / amend 等）执行前必须先经用户确认（checkpoint 的 `git stash`、基线用的 `git worktree` 属流程机制，除外）
3. 自审必须真跑构建/测试，不靠"我觉得没问题"
4. 改之前先读文件，不盲改（DSH 平台强制 read-before-write）
5. 打回就改到位，不糊弄
6. 动手前必须创建 checkpoint（git stash），改崩能回滚
7. 没有测试套件就明说，不假装测过

## 与 DSH 平台机制的配合

- **sandbox / 审批**：写操作受 workspace 策略约束；被拒时用 `sandbox_permissions` 升级（附一句 justification，用户批准）。升级只针对被拒的同一操作，不提前滥用；拒绝即终局，不换命令绕过。
- **plan mode**：复杂方案用 `exit_plan_mode` 呈现给用户（approve / keep planning），approve 后自动退出 plan mode 再执行——这就是 DSH 原生的"方案确认闸门"。
- **后台任务**：`pwsh` 加 `run_in_background: true` 跑构建/测试/长命令，`job_output` 非阻塞读取，`job_kill` 终止；不要忙等轮询。
- **goal 工具**：跨轮长目标用 `create_goal` / `update_goal` 持久化；配合 `.agent/plans/` 文件，防会话压缩/跨天丢上下文。
- **技能热更新**：技能文件本体改动后 DSH 的 catalog 会自动失效重建，无需手动刷新；本目录下 `references/`、`scripts/` 等资源变更不会触发 catalog 重建（正常行为）。
