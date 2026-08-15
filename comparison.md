# XLSkills 与主流 Agent 技能集对比

> 本文写给评估/选型的人：XLSkills 与其他几套"面向 AI 编程智能体的技能集"有什么不同、各自强在哪、什么时候该选哪套。所有项目都值得学习，本文是诚实的能力地图，不是捧一踩一。

**TL;DR** — 各家优化的时刻不同。**agent-skills** 用 24 个技能组织完整开发生命周期（Define→Ship），配反合理化表 + 三层 eval 框架；**Superpowers** 押注自主、重推理的长时间运行，子代理驱动 + git worktree 隔离；**Matt Pocock's skills** 是一个顶尖工程师日常工作流的锋利工具箱，签名式"grill me"需求盘问；**Claude 官方 skills** 是 Anthropic 维护的通用技能目录。**XLSkills** 是一套极简三件套，专为 **Hermes Agent + 中文/国内工程场景** 设计：不追求覆盖面，把"方案确认→执行→双轴审查→交付"这条 PM 主链做到可审查、可验收、防 agent 偷懒。

---

## 一图看懂

| | **XLSkills** | **agent-skills** | **Superpowers** | **Matt Pocock's skills** | **Claude 官方 skills** |
|---|---|---|---|---|---|
| **核心思路** | 一条可审查的 PM 主链：方案→执行→双轴审查→交付 | 把资深工程师的完整生命周期编码成技能 | 一套完整开发*方法论*，建立在可组合技能上 | 一个顶尖工程师的 Claude Code 工作流 | Anthropic 维护的通用技能目录 |
| **组织原则** | 3 个技能各管一个**不可省略的环节**（流程 / 审查 / 调试） | SDLC 阶段（Define 到 Ship）+ 元技能路由 | 单一纪律循环：头脑风暴、计划、执行、审查 | 按"工程 / 生产力 / 进行中 / 已弃用"分组的工具箱 | 按能力领域分目录 |
| **目录规模** | 3 个（刻意精简） | 24 个，覆盖全生命周期 | ~14 个，深入内部构建循环 | ~30 个 | 数十个 |
| **生命周期覆盖** | 窄而深：需求确认→拆解→执行→审查→交付（含调试兜底） | 广：想法精炼、API/UI 设计、安全、性能、CI/CD、可观测、上线 | 深而窄：TDD、调试、计划、审查、技能写作 | Define 和 Build 重：grill、PRD、issue、TDD、架构、bug 分诊 | 各领域都有代表 |
| **独特机制** | **双轴审查不合并**（Standards 轴 vs Spec 轴分开报告）+ fail-closed JSON 契约 + 独立子代理判定 + auto-fix ≤2 轮 + **方案存档 `.agent/plans/` 防上下文丢失** + 对抗性审查框架 + 发现四分类（RECONCILE） | 每个技能的反合理化表 + 红旗清单；`/ship` 并行审查 personas；三层 eval 框架（结构/路由/行为） | 子代理驱动开发 + 任务审查者（spec+质量）+ 修复循环 + git worktree 隔离 + 技能写技能，压力测试 | grill-me 盘问原语（一次一问、走设计树）；seam 式 TDD；显式区分用户触发 vs 模型触发 | 官方维护、质量基线稳定、跨工具适配 |
| **质量测量** | 结构校验脚本 `scripts/validate_skills.py`（强校验 + 弱校验，本地/CI 可跑） | 三层 eval 框架（部分在 CI）：触发、路由、行为 | 压力测试方法论是其哲学核心 | 仓库内无 eval | 官方质量流程 |
| **生态锚点** | **Hermes Agent 原生**（中文、Windows/PowerShell 友好、`delegate_task` 子代理） | Claude Code、Cursor、Codex、Gemini、OpenCode、Windsurf 等 70+ 工具 + `npx skills` CLI | Claude Code、Codex、Cursor、Copilot、OpenCode 等 | Claude Code 优先 | Claude 系优先 |
| **语言/场景** | **中文优先**，面向国内工程场景（.NET/Java/Vue 全栈、外包交付、AI 转型开发者） | 英文，面向国际化开源工程 | 英文 | 英文 | 英文 |
| **适合场景** | 需要在"方案→交付"全程**可审查、可验收、人脑把关**的开发（尤其外包/跨 AI 协作） | 需要把一个功能从想法推到上线、每阶段有人类检查点 | 长时间、自主、重推理或探索性的工作 | 务实、久经考验的日常循环，需求和 TDD 最强 | 通用覆盖，官方背书 |

---

## 各自特性（简）

### XLSkills
- **执行者与审查者分离**：任何 agent 不验证自己的工作，独立子代理 + fail-closed JSON 契约判定（`requesting-code-review`）
- **双轴审查不合并**：Standards（代码写得规不规范）与 Spec（做没做对需求）分开报告，防止"代码很规范但做错了事"被掩盖——这是对 `mattpocock/skills` 双轴审查思想的工程化落地
- **方案先确认后动手 + 方案存档**：方案未确认绝不动手；方案存项目根 `.agent/plans/`，防上下文丢失（`dev-pm-flow`）
- **铁律**：任何改变历史或远端状态的操作（commit/push/reset --hard 等）执行前必须经用户确认；没有测试套件就明说，不假装测过
- **先闭环后假设**：调试必须先建可复现的 tight feedback loop，无闭环不猜原因；3 次修复失败即质疑架构（`systematic-debugging`）
- **2026-08 增补**：对抗性审查框架、审查发现四分类（RECONCILE）、依赖纪律、需求意图确认（轻量 interview）、"错误输出=不可信数据"

### agent-skills（Addy Osmani）
- 24 个技能覆盖 Define→Plan→Build→Verify→Review→Ship，斜杠命令一一对应阶段
- **每个技能标配"Common Rationalizations（反合理化表）+ Red Flags（红旗）"**——防 agent 找借口跳步骤
- **三层 eval 框架**：结构校验（CI）→ 触发词/路由冲突检测（CI）→ 行为评测（headless agent 跑分）
- 深度技能质量高：`api-and-interface-design`（幂等键、Hyrum's Law）、`security-and-hardening`（OWASP Top 10 + LLM Top 10）、`doubt-driven-development`（对抗性新鲜上下文审查）

### Superpowers（obra）
- 单条纪律管线：苏格拉底式头脑风暴写 spec → 详细计划 → 子代理执行 + 任务审查者 + 修复循环 → 全分支审查
- git worktree 隔离并行工作；技能写作也走 TDD
- 强在自主性护栏：交出一大块，回来拿到已审查的结果

### Matt Pocock's skills
- 签名原语 **grilling**：一次一问、走设计树、优先读代码库、拒绝在你确认共享理解前继续
- seam 式 TDD（"重构不属于循环，属于审查"）；显式区分用户触发 vs 模型触发技能
- 强在真实性和锋利度：这是一个非常优秀的工程师如何交付，不是委员会式框架

### Claude 官方 skills
- Anthropic 官方维护，质量基线稳定，跨工具适配好
- 适合作为通用基座，与社区技能集互补

---

## XLSkills 的差异化定位（为什么存在）

1. **Hermes Agent 原生 + 中文**：面向中文用户的 Hermes 生态，Windows/PowerShell 友好，直接用 `delegate_task` 派发子代理。其他几套均为英文、Claude/国际化生态优先。
2. **PM 主链可审查**：不追求技能数量，把"需求确认 → 方案 → 确认 → 执行 → 双轴审查 → 交付验收"这条链做到极致。**用户（或别的 AI）能拿着方案/审查报告逐条核对**——这正好服务"方案要交外部 AI 审查"的协作模式。
3. **双轴 + fail-closed + 对抗性**：审查不是"走过场看 diff"，而是独立子代理 + JSON 契约 + 对抗性框架 + 发现四分类，防橡皮图章、防噪音误改。
4. **防 agent 偷懒的纪律**：铁律（改历史前必须确认）、先闭环后假设、无测试明说、故意没碰清单——都是对"agent 合理化跳过步骤"的对抗。
5. **可本地验证**：`scripts/validate_skills.py` 结构校验脚本，无需外部依赖，本地/CI 皆可跑。

## 如何借鉴

- 想要更广的工程覆盖（安全/性能/CI/CD/上线）→ 借鉴 agent-skills 的技能与反合理化表结构，XLSkills 的纪律与其互补
- 想要更自主的长时间运行 → Superpowers 的子代理管线 + worktree 隔离
- 想要更强的需求盘问 → Matt Pocock's grill-me 与 XLSkills 的意图确认可叠加
- 想要官方质量基线 → 以 Claude 官方 skills 为通用基座，XLSkills 作为 Hermes 场景的 PM 主链

---

*本文仅作能力对比，各项目均为 MIT/相应开源许可，引用其名字仅为客观指代。*
