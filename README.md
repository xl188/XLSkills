# XLSkills — Hermes Agent 技能集

一套面向 **Hermes Agent** 的开发工作流技能集，覆盖从需求到交付的完整闭环：

| 技能 | 作用 | 触发时机 |
|---|---|---|
| **dev-pm-flow** | 开发 PM 流程：需求拆解(垂直切片)→方案→确认→执行→自审(双轴)→交付 | 用户提开发需求时 |
| **requesting-code-review** | 双轴 pre-commit 审查：Standards 轴(安全/质量) + Spec 轴(对照需求原文查缺漏/蔓延/领域错误)，两轴分开报告，独立子代理判定 + 自动修复循环(≤2轮) | 改动完成 / commit 前 / 🟡🔴 改动由 dev-pm-flow 联动 |
| **systematic-debugging** | 四阶段根因调试：根因调查→模式分析→假设测试→实现修复；**无复现闭环不假设**，3 次修复失败即质疑架构 | 任何 bug / 测试失败 / 构建失败 / 性能问题 |

## 设计理念

- **执行者与审查者分离**：任何 agent 不验证自己的工作，独立子代理 + fail-closed JSON 契约判定
- **双轴审查不合并**：Standards(代码写得规不规范) 与 Spec(做没做对需求) 分开报告，防止"代码规范但做错了事"被掩盖
- **方案先确认后动手**：方案未确认绝不动手；方案存档到项目根 `.hermes/plans/`，防上下文丢失
- **铁律**：git commit 由用户手动执行，agent 绝不代劳；没有测试套件就明说，不假装测过
- **先闭环后假设**：调试必须先建可复现的 tight feedback loop，无闭环不猜原因

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

## 目录结构

```
XLSkills/
├── README.md
├── LICENSE
├── dev-pm-flow/
│   └── SKILL.md
├── requesting-code-review/
│   ├── SKILL.md
│   └── references/
│       └── dotnet.md          # .NET/C#/SqlSugar 安全扫描 pattern 库
└── systematic-debugging/
    └── SKILL.md
```

## 贡献

欢迎 PR。新增技术栈的审查 pattern 时，在 `requesting-code-review/references/` 下新增 `<stack>.md`，SKILL.md 的流程主体不动。

## License

MIT — 见 [LICENSE](LICENSE)。其中 `requesting-code-review` / `systematic-debugging` 改编自 [obra/superpowers](https://github.com/obra/superpowers) (MIT)。
