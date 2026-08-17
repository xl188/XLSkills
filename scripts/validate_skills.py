#!/usr/bin/env python3
"""XLSkills 结构校验脚本（agent-skills Tier1 的轻量版）。

强校验（FAIL，退出码 1）：技能目录有 SKILL.md / frontmatter 有 name+description /
name 与目录名一致 / description 非空。
弱校验（WARN 不挡）：有 version / 有核心章节 / description 含触发词。

用法：
    python scripts/validate_skills.py            # 校验仓库根
    python scripts/validate_skills.py <dir>      # 校验指定目录
"""
import pathlib
import re
import sys

# 仓库根下含 SKILL.md 的目录视为技能；排除隐藏目录与常见非技能目录
SKIP_DIRS = {".git", ".github", "docs", "scripts", "references", ".agent", ".hermes"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML frontmatter（宽松版，只取 key: value 行），返回 (字段dict, 正文)。"""
    fields: dict[str, str] = {}
    body = text
    m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if m:
        fm = m.group(1)
        body = text[m.end():]
        for line in fm.splitlines():
            mm = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*?)\s*$", line)
            if mm:
                fields[mm.group(1)] = mm.group(2).strip("'\"")
    return fields, body


def find_skills(root: pathlib.Path) -> list[pathlib.Path]:
    """扫描根目录，返回所有技能目录（含 SKILL.md 的子目录）。"""
    if (root / "SKILL.md").exists():
        return [root]
    skills = []
    for p in sorted(root.iterdir()):
        if not p.is_dir() or p.name in SKIP_DIRS or p.name.startswith("."):
            continue
        if (p / "SKILL.md").exists():
            skills.append(p)
    return skills


def validate_skill(skill_dir: pathlib.Path) -> tuple[list[str], list[str]]:
    """校验单个技能，返回 (fails, warns)。"""
    fails: list[str] = []
    warns: list[str] = []
    skill = skill_dir.name
    sk_path = skill_dir / "SKILL.md"

    if not sk_path.exists():
        fails.append(f"[{skill}] 缺 SKILL.md")
        return fails, warns

    text = sk_path.read_text(encoding="utf-8", errors="replace")
    fields, body = parse_frontmatter(text)

    name = fields.get("name", "")
    desc = fields.get("description", "")

    if not name:
        fails.append(f"[{skill}] frontmatter 缺 name")
    elif name != skill:
        fails.append(f"[{skill}] name '{name}' 与目录名 '{skill}' 不一致")

    if not desc:
        fails.append(f"[{skill}] frontmatter 缺 description")

    if "version" not in fields:
        warns.append(f"[{skill}] 缺 version")
    if "license" not in fields:
        warns.append(f"[{skill}] 缺 license")

    # 核心章节（弱校验，仅提示）
    core_sections = ["Overview", "When to Use", "Common Rationalizations", "Red Flags", "Verification"]
    missing = [s for s in core_sections if f"## {s}" not in body and f"## {s.lower()}" not in body.lower()]
    if missing:
        warns.append(f"[{skill}] 缺核心章节（建议补全，不强制）: {', '.join(missing)}")

    # description 是否含触发词（弱校验）
    if desc and not re.search(r"触发|trigger|Use when|when to use|Use|用", desc, re.I):
        warns.append(f"[{skill}] description 未见明显触发词（建议含 'Use when' / '触发' 类表述）")

    return fails, warns


def main() -> int:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    skills = find_skills(root)
    if not skills:
        print(f"✗ 未在 {root} 下找到任何技能目录（含 SKILL.md 的子目录）")
        return 1

    all_fails: list[str] = []
    all_warns: list[str] = []
    for s in skills:
        f, w = validate_skill(s)
        all_fails.extend(f)
        all_warns.extend(w)

    print(f"扫描 {len(skills)} 个技能: {', '.join(s.name for s in skills)}")
    if all_warns:
        print("\n[WARN]")
        for w in all_warns:
            print("  " + w)
    if all_fails:
        print("\n[FAIL]")
        for f in all_fails:
            print("  " + f)
        print(f"\n结论: {len(all_fails)} 项强校验未通过 ✗")
        return 1
    print(f"\n结论: 强校验全部通过 ✓（{len(all_warns)} 项弱校验建议）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
