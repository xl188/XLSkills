# .NET / C# 安全扫描参考（SqlSugar / SqlClient / Dapper / Oracle）

本文件是 requesting-code-review 的 .NET 专属静态扫描 pattern 库。
SKILL.md 是通用流程；接 .NET 项目时读取本文件执行扫描，接其他技术栈时新增对应参考文件（如 references/java.md），SKILL.md 不动。

## 静态扫描命令（对 diff 的 + 行执行）

```bash
# SqlSugar/Dapper/SqlClient 裸 SQL 调用点 + 拼接特征（命中后人工复核是否参数化）
# 注意：不要用裸 'select|insert|update|delete' 关键词过滤——日志/注释里的 "insert done: {n}" 会误伤
git diff --cached | grep "^+[^+]" | grep -iE '\.SqlQuery|\.ExecuteCommand|\.Ado\.|\.Query<|\.ExecuteNonQuery|\.ExecuteReader' | grep -E '\$\"|string\.Format|\+ ?[a-zA-Z_$]'

# Process.Start 进程执行（C# 的 os.system 等价物）
git diff --cached | grep "^+[^+]" | grep -E 'Process\.Start|ProcessStartInfo|UseShellExecute'

# 危险反序列化（.NET 专有）
git diff --cached | grep "^+[^+]" | grep -E 'BinaryFormatter|SoapFormatter|LosFormatter|JavaScriptSerializer|ObjectStateFormatter'

# 动态编译/加载（C# 的 eval 等价物）
git diff --cached | grep "^+[^+]" | grep -E 'CSharpCodeProvider|CodeDomProvider|Assembly\.Load(From)?\('

# 路径穿越 — 用户输入直接拼文件路径
git diff --cached | grep "^+[^+]" | grep -E 'Path\.Combine\(.*(Request|QueryString|Form\[|HttpContext)'

# 硬编码凭据 — 连接串/密码明文
git diff --cached | grep "^+[^+]" | grep -iE "(Password|Pwd|Passwd|User ?Id)\\s*=\\s*[\"']{1}[^\"']{6,}[\"']{1}"
```

说明：
- `grep "^+[^+]"` 排除 `+++ b/file` 的 diff 头行（第一个 + 后不能再是 +）
- 扫描只针对新增行；命中 = 需人工复核的信号，不是自动定罪

## C# 常见风险模式（审查子代理的判据参考）

```csharp
// Bad: SQL 注入 — 字符串插值拼 SQL
db.Ado.SqlQuery<T>($"SELECT * FROM t_orders WHERE entrust_no = {input}");
// Good: 参数化
db.Ado.SqlQuery<T>("SELECT * FROM t_orders WHERE entrust_no = @no", new { no = input });

// Bad: SqlSugar Where 拼字符串
db.Queryable<Entrust>().Where($"EntrustNo = {input}").ToList();
// Good: 表达式树
db.Queryable<Entrust>().Where(e => e.EntrustNo == input).ToList();

// Bad: 拼接 SQL
var sql = "SELECT * FROM t_user WHERE name = '" + name + "'";
// Good: SqlParameter / 参数化
var sql = "SELECT * FROM t_user WHERE name = @name";

// Bad: 外部命令执行（shell 注入面）
Process.Start("cmd.exe", "/c " + userInput);
// Good: 白名单校验后执行
if (!AllowedCommands.Contains(userInput)) throw new ArgumentException();

// Bad: 危险反序列化
var obj = new BinaryFormatter().Deserialize(stream);
// Good: 换 System.Text.Json（.NET 8 默认禁用 BinaryFormatter）

// Bad: 动态编译（C# 的 eval 等价物）
new CSharpCodeProvider().CompileAssemblyFromSource(...);
```

## 自审 checklist（C# 附加项）

- [ ] SqlSugar/Dapper 查询参数化（Where/Ado 不拼字符串，不用 `$"..."` 裸 SQL）
- [ ] 连接串/密钥不进代码（走 appsettings/环境变量/配置中心）
- [ ] 无 Process.Start 执行外部命令（或输入已验证）
