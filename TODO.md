# 多学校班级管理系统 - 待办清单

## ✅ 已完成

### 数据库设计 (100%)
- [x] 设计schools表结构
- [x] 设计classes表结构
- [x] 设计teacher表扩展字段
- [x] 设计students表扩展字段
- [x] 编写CREATE TABLE语句
- [x] 编写ALTER TABLE语句
- [x] 编写数据迁移脚本
- [x] 添加外键约束
- [x] 添加索引
- [x] 创建测试数据
- [x] 编写验证查询

### Python模型层 (100%)
- [x] 创建Schools实体类
- [x] 创建SchoolsServer服务类
- [x] 实现学校CRUD方法
- [x] 实现学校统计方法
- [x] 创建Classes实体类
- [x] 创建ClassesServer服务类
- [x] 实现班级CRUD方法
- [x] 实现班级学生管理方法
- [x] 扩展Students实体类
- [x] 扩展StudentsServer服务类
- [x] 实现学生按学校/班级查询
- [x] 扩展Teachers实体类
- [x] 扩展TeachersServer服务类
- [x] 实现教师审核方法
- [x] 实现教师按学校查询

### 文档编写 (100%)
- [x] 编写SCHOOL_MANAGEMENT_DESIGN.md（设计方案）
- [x] 编写IMPLEMENTATION_GUIDE.md（实施指南）
- [x] 编写QUICK_REFERENCE.md（快速参考）
- [x] 编写SUMMARY.md（实施总结）
- [x] 编写TODO.md（本文档）

---

## 🔄 进行中

暂无

---

## 📋 待完成

### 阶段一：执行数据库迁移 (优先级: 🔴高)

#### 1.1 备份数据库
- [ ] 使用mysqldump备份现有数据库
- [ ] 验证备份文件完整性
- [ ] 记录备份文件路径

```bash
# 执行命令
mysqldump -u root -p onlinejudgesystem > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
```

#### 1.2 执行迁移脚本
- [ ] 在测试环境执行迁移（推荐）
- [ ] 在生产环境执行迁移
- [ ] 检查是否有错误信息

```bash
# 执行命令
mysql -u root -p onlinejudgesystem < migration_multi_school.sql
```

#### 1.3 验证迁移结果
- [ ] 验证schools表创建成功
- [ ] 验证classes表创建成功
- [ ] 验证teacher表字段添加成功
- [ ] 验证students表字段添加成功
- [ ] 验证现有数据已迁移
- [ ] 验证外键约束生效
- [ ] 验证索引创建成功

```sql
-- 执行验证查询（在migration_multi_school.sql最后有）
SELECT * FROM schools;
SELECT * FROM classes;
SELECT Id, Name, school_id, approval_status FROM teacher LIMIT 10;
SELECT Id, Name, school_id, class_id FROM students LIMIT 10;
```

---

### 阶段二：创建后端API (优先级: 🔴高)

#### 2.1 创建schoolviews.py
- [ ] 在OnlineJudgeSystem目录下创建schoolviews.py
- [ ] 复制IMPLEMENTATION_GUIDE.md中的完整代码
- [ ] 检查import语句是否正确
- [ ] 检查路由装饰器是否正确

**文件位置**: `OnlineJudgeSystem/OnlineJudgeSystem/schoolviews.py`

**需要实现的路由**:
```python
# 学校管理
- GET  /admin/schools              # 学校列表页面
- GET  /api/schools/list           # 获取学校列表
- POST /api/schools/add            # 添加学校
- POST /api/schools/update         # 更新学校
- POST /api/schools/toggle_status  # 启用/禁用学校

# 班级管理
- GET  /admin/classes         # 班级列表页面
- GET  /api/classes/list      # 获取班级列表
- POST /api/classes/add       # 添加班级
- POST /api/classes/update    # 更新班级

# 教师审核
- GET  /admin/teacher_approval # 教师审核页面
- GET  /api/teachers/pending   # 获取待审核教师
- POST /api/teachers/approve   # 审核教师
```

#### 2.2 更新__init__.py
- [ ] 打开OnlineJudgeSystem/__init__.py
- [ ] 在现有import语句后添加：`from OnlineJudgeSystem import schoolviews`
- [ ] 保存文件
- [ ] 重启Flask应用

**代码示例**:
```python
# 在现有import后添加
from OnlineJudgeSystem import views
from OnlineJudgeSystem import adminuserviews
from OnlineJudgeSystem import teacherviews  
from OnlineJudgeSystem import usersviews
from OnlineJudgeSystem import schoolviews  # 新增这一行
```

#### 2.3 测试API接口
- [ ] 启动Flask应用
- [ ] 使用Postman或curl测试学校列表API
- [ ] 测试添加学校API
- [ ] 测试更新学校API
- [ ] 测试班级列表API
- [ ] 测试待审核教师API
- [ ] 测试审核教师API

---

### 阶段三：创建前端页面 (优先级: 🟠中)

#### 3.1 创建学校管理页面
- [ ] 创建templates/admin/schools.html
- [ ] 实现学校列表显示（Bootstrap Table）
- [ ] 实现添加学校模态框
- [ ] 实现编辑学校模态框
- [ ] 实现学校统计信息显示
- [ ] 实现启用/禁用切换

**页面结构**:
```html
- 顶部：搜索框、添加按钮
- 中间：学校列表表格
  - 学校名称、代码、省市、状态
  - 教师数、学生数、班级数
  - 操作按钮（编辑、启用/禁用）
- 底部：分页
```

#### 3.2 创建班级管理页面
- [ ] 创建templates/admin/classes.html
- [ ] 实现学校选择下拉框
- [ ] 实现班级列表显示
- [ ] 实现添加班级模态框
- [ ] 实现编辑班级模态框
- [ ] 实现班主任分配
- [ ] 实现学生列表查看

**页面结构**:
```html
- 顶部：学校筛选、添加班级按钮
- 中间：班级列表表格
  - 班级名称、年级、班主任、学生人数
  - 操作按钮（编辑、查看学生）
- 底部：分页
```

#### 3.3 创建教师审核页面
- [ ] 创建templates/admin/teacher_approval.html
- [ ] 实现待审核教师列表
- [ ] 实现学校筛选
- [ ] 实现查看教师详情
- [ ] 实现审核通过按钮
- [ ] 实现审核拒绝模态框（填写拒绝原因）
- [ ] 实现审核历史显示

**页面结构**:
```html
- 顶部：学校筛选、状态筛选
- 中间：待审核教师列表
  - 教师姓名、学校、联系方式
  - 操作按钮（通过、拒绝、查看详情）
- 侧边：教师详情卡片
```

#### 3.4 更新管理员导航菜单
- [ ] 打开templates/adminLayout.html
- [ ] 在导航栏添加"学校管理"菜单项
- [ ] 添加"班级管理"菜单项
- [ ] 添加"教师审核"菜单项（显示待审核数量徽章）

---

### 阶段四：更新注册流程 (优先级: 🟠中)

#### 4.1 更新教师注册表单
- [ ] 打开templates/register.html或loginAndRegister.html
- [ ] 在教师注册表单添加学校选择下拉框
- [ ] 从/api/schools/list加载学校列表
- [ ] 添加"注册后需等待管理员审核"提示
- [ ] 更新提交逻辑（包含school_id）

**表单字段**:
```html
- 用户名
- 密码
- 姓名
- 学校（下拉选择）← 新增
- 身份证
- 手机号
- 地址
```

#### 4.2 更新学生注册表单
- [ ] 在学生注册表单添加学校选择下拉框
- [ ] 添加班级选择下拉框（根据学校动态加载）
- [ ] 实现学校变化时班级联动
- [ ] 更新提交逻辑（包含school_id和class_id）

**表单字段**:
```html
- 用户名
- 密码
- 姓名
- 学校（下拉选择）← 新增
- 班级（下拉选择）← 新增
- 身份证
- 手机号
- 地址
```

**JavaScript联动**:
```javascript
$('#school_select').change(function() {
    var school_id = $(this).val();
    $.get('/api/classes/list?school_id=' + school_id, function(res) {
        // 更新班级下拉框选项
    });
});
```

#### 4.3 更新views.py注册逻辑
- [ ] 打开OnlineJudgeSystem/views.py
- [ ] 找到教师注册函数（register_teacher或类似）
- [ ] 添加school_id获取：`school_id = request.form['school_id']`
- [ ] 设置teacher.SchoolId = school_id
- [ ] 找到学生注册函数
- [ ] 添加school_id和class_id获取
- [ ] 设置student.SchoolId和student.ClassId

**代码示例**:
```python
# 教师注册
teacher.SchoolId = request.form.get('school_id', 0)
# approval_status在insert_sql中自动设为0

# 学生注册
student.SchoolId = request.form.get('school_id', 0)
student.ClassId = request.form.get('class_id', 0)
```

#### 4.4 更新登录反馈
- [ ] 教师登录时，如果审核未通过，显示友好提示
- [ ] 修改登录函数，检查ApprovalStatus
- [ ] 显示"账号正在审核中，请耐心等待"或"账号审核未通过"

---

### 阶段五：全面测试 (优先级: 🟡一般)

#### 5.1 数据库测试
- [ ] 测试添加学校
- [ ] 测试更新学校
- [ ] 测试删除学校（验证级联删除）
- [ ] 测试添加班级
- [ ] 测试更新班级学生人数
- [ ] 测试学生班级调整
- [ ] 测试外键约束生效

#### 5.2 后端API测试
- [ ] 测试学校列表API（有数据）
- [ ] 测试学校列表API（按状态筛选）
- [ ] 测试学校统计信息准确性
- [ ] 测试班级列表API（按学校筛选）
- [ ] 测试待审核教师API
- [ ] 测试审核通过功能
- [ ] 测试审核拒绝功能

#### 5.3 前端功能测试
- [ ] 测试学校管理页面加载
- [ ] 测试添加学校（表单验证）
- [ ] 测试编辑学校
- [ ] 测试启用/禁用学校
- [ ] 测试班级管理页面加载
- [ ] 测试添加班级
- [ ] 测试班主任分配
- [ ] 测试教师审核页面加载
- [ ] 测试审核操作

#### 5.4 注册流程测试
- [ ] 测试教师注册（选择学校）
- [ ] 验证教师注册后status为待审核
- [ ] 测试待审核教师无法登录
- [ ] 测试审核通过后教师可登录
- [ ] 测试学生注册（选择学校和班级）
- [ ] 验证学生注册后关联正确
- [ ] 测试学校-班级联动选择

#### 5.5 权限测试
- [ ] 测试未登录访问管理页面（应跳转登录）
- [ ] 测试教师访问学校管理（应无权限）
- [ ] 测试学生访问管理页面（应无权限）
- [ ] 测试管理员访问所有学校数据
- [ ] 测试教师只能看自己学校数据
- [ ] 测试学生只能看自己学校/班级数据

#### 5.6 性能测试
- [ ] 测试大量学校数据加载速度
- [ ] 测试班级列表分页
- [ ] 测试学生列表分页
- [ ] 检查SQL查询效率（使用EXPLAIN）
- [ ] 检查索引是否生效

---

### 阶段六：优化与完善 (优先级: 🟢低)

#### 6.1 用户体验优化
- [ ] 添加加载动画
- [ ] 添加操作成功/失败提示（toastr）
- [ ] 优化表单验证提示
- [ ] 添加确认对话框（删除操作）
- [ ] 优化移动端响应式布局

#### 6.2 功能增强
- [ ] 学校logo上传功能
- [ ] 班级人数自动更新（触发器）
- [ ] 教师审核邮件通知
- [ ] 数据导出功能（Excel）
- [ ] 统计报表优化（图表展示）
- [ ] 批量导入学生功能

#### 6.3 代码优化
- [ ] 添加更多异常处理
- [ ] 统一错误返回格式
- [ ] 添加日志记录
- [ ] 优化SQL查询（JOIN优化）
- [ ] 添加API接口文档（Swagger）

#### 6.4 文档更新
- [ ] 更新README.md添加新功能说明
- [ ] 添加API文档
- [ ] 添加部署文档
- [ ] 添加常见问题FAQ

---

## 📅 时间估算

### 必须完成（核心功能）
- 阶段一（数据库迁移）: 0.5天
- 阶段二（后端API）: 1天
- 阶段三（前端页面）: 2天
- 阶段四（注册流程）: 1天
- 阶段五（测试）: 1.5天
**小计**: 约6天

### 可选完成（优化增强）
- 阶段六（优化）: 3-5天

---

## ✅ 完成标准

### 阶段一完成标准
- ✅ 数据库备份文件存在
- ✅ 所有表创建成功
- ✅ 所有字段添加成功
- ✅ 现有数据已迁移
- ✅ 验证查询全部通过

### 阶段二完成标准
- ✅ schoolviews.py文件创建
- ✅ __init__.py已更新
- ✅ 所有API路由可访问
- ✅ API返回正确JSON格式
- ✅ 无Python语法错误

### 阶段三完成标准
- ✅ 3个HTML页面创建完成
- ✅ 页面可正常访问
- ✅ AJAX请求正常工作
- ✅ 表单验证正常
- ✅ UI美观且响应式

### 阶段四完成标准
- ✅ 注册表单添加学校/班级选择
- ✅ 学校-班级联动正常
- ✅ 注册逻辑正确保存数据
- ✅ 登录时审核状态检查生效

### 阶段五完成标准
- ✅ 所有测试用例通过
- ✅ 无功能性bug
- ✅ 权限控制正确
- ✅ 性能满足要求

---

## 🚀 下一步行动

### 立即开始
1. ⚠️ **备份数据库**（最重要！）
2. 执行数据库迁移脚本
3. 验证迁移结果
4. 创建schoolviews.py
5. 更新__init__.py
6. 测试API接口

### 推荐顺序
```
备份数据库 → 迁移数据库 → 创建API → 测试API → 
创建前端 → 更新注册 → 全面测试 → 上线发布
```

---

## 📝 备注

- 每完成一个阶段，打勾标记 [x]
- 遇到问题记录在对应任务下
- 测试发现的bug及时修复
- 保持代码风格统一
- 提交前检查无console.log和print调试代码

---

**开始实施吧！祝顺利！** 🎉

**第一步：备份数据库！** ⚠️
```bash
mysqldump -u root -p onlinejudgesystem > backup_$(date +%Y%m%d_%H%M%S).sql
```
