# XLSkills — Hermes Agent 技能集

**Production-grade PM workflow skills for AI coding agents.** 一套面向 **Hermes Agent** 的开发工作流技能集，把资深工程师 + PM 的完整闭环（需求确认→方案→执行→双轴审查→交付）编码成可被 AI agent 自动加载执行的技能。

```
 确认意图    拆解方案    用户确认    执行开发      双轴审查      交付验收
 ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
 │ 需求  │──▶│ 方案  │──▶│ 拍板  │──▶│ 切片  │──▶│Standards│──▶│ 过目  │
 │ Interview│  │垂直切片│   │ 等"可以" │   │ 增量  │   │ + Spec │   │ 验收  │
 └───────┘   └───────┘   └───────┘   └───────┘   └───────┘   └───────┘
  意图确认     方案存档      方案未确认     checkpoint     双轴分开      提交前
  (轻量采访)   .agent/plans  绝不动手       git stash    不合并排名     用户确认
```

## 三件套

| 技能 | 作用 | 触发时机 |
|---|---|---|
| **dev-pm-flow** | 开发 PM 流程：需求拆解(垂直切片)→方案→确认→执行→自审(双轴)→交付 | 用户提开发需求时 |
| **requesting-code-review** | 双轴 pre-commit 审查：Standards 轴(安全/质量) + Spec 轴(对照需求原文查缺漏/蔓延/领域错误)，两轴分开报告，独立子代理判定 + 自动修复循环(≤2轮) | 改动完成 / commit 前 / 🟡🔴 改动由 dev-pm-flow 联动 |
| **systematic-debugging** | 四阶段根因调试：根因调查→模式分析→假设测试→实现修复；**无复现闭环不假设**，3 次修复失败即质疑架构 | 任何 bug / 测试失败 / 构建失败 / 性能问题 |

## 设计理念

- **执行者与审查者分离**：任何 agent 不验证自己的工作，独立子代理 + fail-closed JSON 契约判定
- **双轴审查不合并**：Standards(代码写得规不规范) 与 Spec(做没做对需求) 分开报告，防止"代码规范但做错了事"被掩盖
- **方案先确认后动手**：方案未确认绝不动手；方案存档到项目根 `.agent/plans/`，防上下文丢失
- **铁律**：任何改变历史或远端状态的操作（commit / push / reset --hard 等）执行前必须经用户确认，agent 绝不擅自执行；没有测试套件就明说，不假装测过
- **先闭环后假设**：调试必须先建可复现的 tight feedback loop，无闭环不猜原因

## English Summary

XLSkills is a set of production-grade **PM workflow skills for Hermes Agent** (and other AI coding agents). Three focused skills:

- **dev-pm-flow** — requirements → plan → human confirmation → incremental execution → dual-axis review → delivery. Enforces human checkpoints, vertical slicing, and plan archiving.
- **requesting-code-review** — dual-axis pre-commit review: Standards (security/quality) + Spec (spec-compliance). Independent subagents, fail-closed JSON verdicts, auto-fix loop.
- **systematic-debugging** — 4-phase root-cause debugging: no fixes without a reproduction loop.

Why XLSkills: agent doesn't verify its own work; review is adversarial and spec-aware; nothing touches git history without explicit human confirmation. Compare with other skill collections in [comparison.md](comparison.md).

## 安装

克隆仓库后，将技能目录复制到 Hermes 的 skills 目录：

```bash
git clone https://github.com/xl188/XLSkills.git
cd XLSkills

# Linux/macOS
cp -r dev-pm-flow requesting-code-review systematic-debugging ~/.local/share/hermes/skills/

# Windows (PowerShell)
Copy-Item dev-pm-flow, requesting-code-review, systematic-debugging -Destination "$env:LOCALAPPDATA\hermes\skills\" -Recurse
```

也可逐个导入 Hermes 桌面端：设置 → Skills → Import。

## 依赖

- `requesting-code-review` 与 `dev-pm-flow` 相互联动（自审环节触发双轴审查）
- 双轴审查通过 `delegate_task` 派发独立子代理，无需额外安装
- `.NET/C#` 项目的静态扫描 pattern 库在 `requesting-code-review/references/dotnet.md`；其他技术栈可参照新增 `references/<stack>.md`

## 技能校验

```bash
python scripts/validate_skills.py   # 结构校验（强校验失败退出码 1）
```

强校验：每个技能有 `SKILL.md`、frontmatter 含 `name`+`description`、`name` 与目录名一致；弱校验（仅提示不挡）：`version` / `license` / 核心章节 / 触发词。纯标准库、无外部依赖，本地与 CI 皆可跑。

## 目录结构

```
XLSkills/
├── README.md
├── LICENSE
├── comparison.md          # 与主流 agent 技能集（agent-skills/Superpowers/Matt Pocock/Claude 官方）的对比
├── dev-pm-flow/
│   └── SKILL.md
├── requesting-code-review/
│   ├── SKILL.md
│   └── references/
│       └── dotnet.md          # .NET/C#/SqlSugar 安全扫描 pattern 库
├── scripts/
│   └── validate_skills.py     # 技能结构校验脚本（标准库，无依赖）
└── systematic-debugging/
    └── SKILL.md
```

## 贡献

欢迎 PR。新增技术栈的审查 pattern 时，在 `requesting-code-review/references/` 下新增 `<stack>.md`，SKILL.md 的流程主体不动。

## License

MIT — 见 [LICENSE](LICENSE)。其中 `requesting-code-review` / `systematic-debugging` 改编自 [obra/superpowers](https://github.com/obra/superpowers) (MIT)。
