## 目标
帮助 AI 代码代理立即在此仓库中高效工作：快速定位 Flask 应用入口、理解 MVC 风格的 model/view 约定、运行/调试方式以及常见的安全与数据库注意事项。

## 关键文件与架构概览
- 应用入口：`OnlineJudgeSystem/OnlineJudgeSystem/__init__.py` — 创建 Flask `app` 并导入视图模块。
- 本地开发启动：`OnlineJudgeSystem/runserver.py` — 设置 CORS、SESSION、SECRET_KEY，并使用 `app.run(HOST, PORT)` 启动。
- 视图（路由）分散在：`OnlineJudgeSystem/views.py`, `OnlineJudgeSystem/adminuserviews.py`, `OnlineJudgeSystem/teacherviews.py`, `OnlineJudgeSystem/usersviews.py`。
- 数据访问层：`OnlineJudgeSystem/common/MySqlHelper.py`（包装 PyMySQL 连接），配置在 `OnlineJudgeSystem/common/Config.py`。
- 模型：`OnlineJudgeSystem/model/` 下每个文件通常包含 数据类 和 对应的 `*Server` 操作类（如 `Students`, `StudentsServer`）。
- 静态与模版：`OnlineJudgeSystem/static/` 与 `OnlineJudgeSystem/templates/`。

## 项目约定和实用规则（给 AI 的具体指导）
- 路由处理（views）中：表单数据通过 `request.form.get(...)` 获取；session 使用 `session['logged_in']` 与 `session['logged_type']` 保存登录态。
- Model 层返回的对象通常有 `to_json()` 方法；查询与插入通过 `*Server` 类的方法（例如 `select_sql_login`, `insert_sql`）。在改动模型接口前，请搜索目录中相同命名模式以避免破坏调用。
- 数据库配置为硬编码在 `common/Config.py`（Windows 默认）。任何对 DB 的更改需同时更新此文件或添加新的配置分支并保证 `MySqlHelper` 使用正确字典。
- 文件上传目录：`OnlineJudgeSystem/upload/`（多个位置）。小心不要在提交/日志中泄露上传文件中的用户代码或敏感信息。

## 运行、调试与常见命令
- 本地运行（PowerShell）：
```powershell
python OnlineJudgeSystem\runserver.py
```
- 在编辑 `Config.py` 或在不同端口/主机运行时，可设置环境变量 `SERVER_HOST` 和 `SERVER_PORT`。

## 代码修改注意要点
- 不要随意更改 `app = Flask(__name__)` 的导入路径或视图导入顺序，视图模块通过导入注册路由。
- 数据库连接使用同步 PyMySQL；短时间内避免并行更改连接管理（例如切换到连接池）除非同时更新 `MySqlHelper`。
- 模板渲染使用 `render_template` 并传入模板内使用的变量名称（例如 `datas_student`、`datas_test`）。修改模板时同步检查对应视图中变量名。

## 安全与隐私提示
- 仓库中有硬编码的 DB 凭据（`common/Config.py`），不应该在生产环境使用。若需要本地测试，建议用本地测试库并在 `.env` 或配置管理中替换。
- 代码中保存 session 的做法使用随机 `SECRET_KEY`（在 `runserver.py` 启动时生成），这会在每次重启后失效；若需要持久化登录用于开发，请设置静态 `SECRET_KEY`（注意不要提交到 VCS）。

## 参考示例（快速定位）
- 登录流程：查看 `OnlineJudgeSystem/OnlineJudgeSystem/views.py` 中 `login()`，注意 `types` 字段决定使用 `Admins`/`Teachers`/`Students`。
- 数据库 helper：`OnlineJudgeSystem/OnlineJudgeSystem/common/MySqlHelper.py` — 查找 `query()` 与 `end()` 的使用位置以理解事务边界。

如果这些说明有遗漏或你希望我把风格化示例（如自动修复规则、常见 PR 模板）加入这个文件，请告诉我需要补充的主题，我会迭代更新。
