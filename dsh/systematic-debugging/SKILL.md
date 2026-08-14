---
name: dsh-systematic-debugging
description: "4-phase root cause debugging（DSH 版）：先闭环后假设 + seam 检查 + 并行假设验证。任何 bug/测试失败/构建失败/性能问题时触发。"
whenToUse: "任何技术问题：测试失败、生产 bug、意外行为、性能问题、构建失败、集成问题；尤其时间压力大、已经试过多次修复、看不懂问题的时候。"
version: 1.0.0-dsh
author: 小艾 (adapted for DeepSeek Harness; original adapted from obra/superpowers)
platforms: [linux, macos, windows]
metadata:
  tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
  related_skills: [dsh-dev-pm-flow]
---

# Systematic Debugging（DSH 版）

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

**与 Hermes 版的关系**：四阶段、铁律、red flags 同源。工具换为 DSH（`read` / `grep` / `glob` / `pwsh` / `subagent` / `job_*`），并新增**并行化**：证据收集、假设验证可多路并行（DSH 同一条消息多 subagent 并行 + 后台任务不占并发槽）。

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## The Feedback Loop Rule

The feedback loop is the debugging work. Before reading code to build a theory, create or identify a **tight** command that can go red on the user's exact symptom and green when the bug is fixed. A tight loop is fast, deterministic, agent-runnable, and specific enough to catch this bug — not merely "doesn't crash".

When a clean repro is hard, spend disproportionate effort building the loop. Guessing without a red-capable loop is the failure mode this skill exists to prevent.

## When to Use

Use for ANY technical issue:
- Test failures / Bugs in production / Unexpected behavior
- Performance problems / Build failures / Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings；完整读栈、行号、文件路径、错误码
- **Action:** 用 `read` 读相关源文件；用 `grep` 在代码库搜错误串

### 2. Build a Tight Feedback Loop

- 一条命令能否触发用户的确切症状？是否只因为这个 bug 才失败、修好才绿？够快到可以反复跑？确定性？（flaky bug 先提高复现率——50% flake 可调，1% 通常不可调）
- 不可复现 → 继续收集数据，不猜

**构造顺序参考（按此优先级）：**
1. 失败测试（落在能触达 bug 的 seam：unit / integration / e2e）
2. HTTP 脚本 / curl 打 dev server
3. CLI + fixture 输入，diff stdout/stderr 与预期
4. Headless browser（Playwright/Puppeteer），断言 DOM/console/network
5. 重放捕获的 trace：HAR、请求体、事件日志、队列消息、webhook body
6. 一次性 harness：boot 系统最小可用切片，调用失败路径
7. Property / fuzz loop（间歇性错误输出、输入空间大）
8. Bisection（`git bisect run`，bug 出现在两个已知状态之间）
9. Differential loop（新旧版本 / 两套配置 / 两个 provider / 两组数据对比）
10. Human-in-the-loop 脚本（最后手段）：把人工步骤脚本化并记录结果

**Tighten the loop once it exists:** 更快（缓存 setup、收窄范围、跳过无关初始化）；信号更尖（断言确切症状而非泛泛成功）；更确定（pin 时间、固定随机种子、隔离文件系统、冻结网络）。

**Action:** 用 `pwsh` 跑 tight loop：

```powershell
# C#/.NET — --no-restore 失败则去掉
dotnet test --filter "FullyQualifiedName~TestName" 2>&1 | Select-Object -Last 5

# Python 指定失败测试
python -m pytest tests/test_module.py::test_name -v

# 或脚本化复现
python scripts/repro_bug.py

# 高重复 flaky 复现（循环 100 次，失败即停）
1..100 | ForEach-Object { python -m pytest tests/test_flake.py::test_name -q; if ($LASTEXITCODE -ne 0) { break } }
```

### 3. Check Recent Changes

```powershell
git log --oneline -10
git diff
git log -p --follow src/problematic_file.py | Select-Object -First 100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

BEFORE proposing fixes, add diagnostic instrumentation. For EACH component boundary: log 进/出数据、验证环境/配置传播、检查各层状态。跑一次定位断在哪层，再调查该组件。

**并行收集（DSH 增强）**：不同边界的探针互不干扰时，用多个后台任务（`pwsh` + `run_in_background: true`，`job_output` 收集）或并行调查 subagent（同一条消息批量派发）同时抓证据，再汇总分析。

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**
- 坏值从哪来？谁用坏值调了这函数？一路往上追到源头
- 修源头，不修症状
- **Action:** 用 `grep` 追引用：

```text
grep "function_name("  → src/ 下 *.py
grep "variable_name\s*=" → src/ 下 *.py
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] A tight loop command exists and has been run at least once
- [ ] Loop is red-capable: it asserts the user's exact symptom, not a nearby failure
- [ ] Loop is deterministic, or a flaky bug has a high enough reproduction rate to debug
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypotheses can be stated and tested

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 0. Minimize the Reproduction

闭环红着的时候，把复现缩到仍会红的最小场景：一次只减一个输入/调用/配置/数据/步骤，每减一次重跑 loop，只留承载失败的部分。减到去掉任何剩余元素都变绿为止。最小复现收窄假设空间，往往就是最干净的回归测试。

### 1. Find Working Examples

- 同库找相似可用代码（`grep` 搜相似 pattern）

### 2. Compare Against References

- 参考实现**整段读完**，不 skim，理解透再套用

### 3. Identify Differences

- 工作 vs 损坏差异列全，再小也不许"那个不影响"

### 4. Understand Dependencies

- 依赖组件、设置、配置、环境、隐含假设

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form Ranked Falsifiable Hypotheses

- 先列 3-5 个假设，按"可能性 × 证伪成本"排序
- 每个必须带可测预测："若 X 是原因，则改/观察 Y 应发生 Z"
- 无法做出可测预测的假设直接丢弃
- 用户在场：先展示排序再测，领域知识可能一句话重排；用户 AFK 则按自己的排序走

### 2. Test Minimally

- 先测排序最高的假设，用最小探针；一次只动一个变量；别同时修多个东西
- 首选断点/REPL 而非加日志（一个断点胜过十条日志）；加日志用唯一前缀（如 `[DEBUG-a4f2]`）方便一次清理

### 3. Verify Before Continuing

- 成了 → Phase 4；没成 → 形成**新**假设
- **别在失败上叠修复**

### 4. When You Don't Know

- 说"我不懂 X"，不装懂；问用户；继续研究

**并行验证（DSH 增强）**：互斥假设可并行证伪——每个 probe 只验证自己的假设、只动自己的变量（保持 one-variable-at-a-time 纪律：并行的是**验证**，不是修复）。多个 probe 用同一条消息批量派 `subagent`（并行）或并行后台命令（`run_in_background: true`）；全部回来后按证据更新排序。**禁止**并行叠加多个修复。

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- 先写复现测试（红）→ 最小修复（绿）→ 重构；RED→GREEN 循环
- **Seam check（mattpocock/skills 借鉴）:** 回归测试必须落在**正确的接缝**上——能复现真实调用链上的 bug 模式。唯一可用接缝太浅时（比如 bug 需要多调用者协作，但只能写单调用者测试），那里的回归测试给的是假信心。**没有正确接缝，这本身就是发现**：记下来，标记"架构在阻止这个 bug 被锁死"，转给架构改进讨论

### 2. Implement Single Fix

- 修 Phase 1 定位的根因；ONE change at a time；没有"顺手"改进；不打包重构

### 3. Verify Fix

```powershell
# C#/.NET
dotnet test --filter "FullyQualifiedName~TestName" 2>&1 | Select-Object -Last 5

# 指定回归测试 (Python)
python -m pytest tests/test_module.py::test_regression -v

# 全量套件，确认无回归
python -m pytest tests/ -q
```

**重跑原始反馈闭环:** 回归测试过了还不够——回到 Phase 1 的原始（未最小化）反馈闭环，对真实场景再跑一次，确认 bug 在真实路径上确实消失。最小化复现通过 ≠ 原始场景修复。

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.** 数一数试过几次修复。
- < 3 次：带新信息回 Phase 1 重分析
- **≥ 3 次：STOP，质疑架构（见下）**——禁止不讨论架构就试第 4 次

### 5. If 3+ Fixes Failed: Question Architecture

**架构问题的信号：**
- 每次修复都在别处冒出新共享状态/耦合
- 修复需要"大规模重构"才能落地
- 每次修复都在别处制造新症状

**STOP 并质疑根本：**
- 这个模式根本上是健全的吗？
- 我们是不是"惯性坚持"？
- 该重构架构还是继续修症状？

**先和用户讨论，再试更多修复。** This is NOT a failed hypothesis — this is a wrong architecture.

## Red Flags — STOP and Follow Process

If you catch yourself thinking any of these, **STOP and return to Phase 1**:

- **没闭环就假设** — "It's probably X, let me fix that"；还没跑通复现命令就开始读代码猜原因
- **没调查就提修复** — "Quick fix for now, investigate later" / "Just try changing X"；还没 trace 数据流就列修复方案
- **硬试不止** — "One more fix attempt"（已试 2+ 次）/ 每次修复都在别处冒出新问题

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5)。

每种借口的完整拆穿见下方「Common Rationalizations」表。

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## DSH Integration

- 各 Phase 工具：`read` / `grep` / `glob` / `pwsh` / `web_search` / `subagent` / `job_output` / `job_kill`，此处不重复
- 复杂多组件问题：派调查 subagent（`subagent`，goal 里贴错误全文 + 复现命令，明确要求"只报告根因，不修复"）；多个组件边界可并行派多个调查员（同一条消息批量发出）
- 修复路径遵循 RED→GREEN 循环：先写复现测试（红）→ 修根因（绿）→ 重构
- 长命令（全量测试、压测、循环复现）放后台：`pwsh` + `run_in_background: true`，`job_output` 收集、`job_kill` 终止，不忙等

**No shortcuts. No guessing. Systematic always wins.**
