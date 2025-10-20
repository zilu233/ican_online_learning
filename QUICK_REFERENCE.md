# 多学校班级管理系统 - 快速参考

## 📁 新增文件列表

```
OnlineJudgeSystem/
├── SCHOOL_MANAGEMENT_DESIGN.md          # 设计方案
├── IMPLEMENTATION_GUIDE.md              # 实施指南
├── migration_multi_school.sql           # 数据库迁移脚本
└── OnlineJudgeSystem/
    └── model/
        ├── Schools.py                   # 学校模型（新建）
        ├── Classes.py                   # 班级模型（新建）
        ├── Students.py                  # 学生模型（已扩展）
        └── Teachers.py                  # 教师模型（已扩展）
```

---

## 🗂️ 数据库表结构

### 新增表

#### schools（学校表）
```
id, school_name, school_code, province, city, address, 
contact_person, contact_phone, email, status, created_at, updated_at
```

#### classes（班级表）
```
id, school_id(FK), class_name, class_code, grade, teacher_id(FK), 
student_count, description, status, created_at, updated_at
```

### 扩展表

#### teacher（教师表）- 新增字段
```
school_id(FK), approval_status, approval_time, 
approval_admin_id, rejection_reason, created_at, updated_at
```

#### students（学生表）- 新增字段
```
school_id(FK), class_id(FK), enrollment_date, 
status, created_at, updated_at
```

---

## 🔑 核心API设计

### 学校管理
```python
GET  /admin/schools              # 学校列表页面
GET  /api/schools/list           # 获取学校列表
POST /api/schools/add            # 添加学校
POST /api/schools/update         # 更新学校
POST /api/schools/toggle_status  # 启用/禁用学校
```

### 班级管理
```python
GET  /admin/classes          # 班级列表页面
GET  /api/classes/list       # 获取班级列表（可按学校筛选）
POST /api/classes/add        # 添加班级
POST /api/classes/update     # 更新班级
```

### 教师审核
```python
GET  /admin/teacher_approval  # 教师审核页面
GET  /api/teachers/pending    # 获取待审核教师列表
POST /api/teachers/approve    # 审核教师（通过/拒绝）
```

---

## 📊 Python模型使用示例

### Schools 学校模型

```python
from OnlineJudgeSystem.model.Schools import Schools, SchoolsServer

# 查询所有启用的学校
schools = SchoolsServer.select_sql_all(status=1)

# 根据ID查询学校
school = SchoolsServer.select_sql_by_id(1)

# 添加学校
school = Schools()
school.SchoolName = "北京第一中学"
school.SchoolCode = "BJ001"
school.Province = "北京市"
school.Status = 1
school_id = SchoolsServer.insert_sql(school)

# 获取学校统计信息
stats = SchoolsServer.get_statistics(1)
print(f"教师数: {stats['teacher_count']}, 学生数: {stats['student_count']}")

# 检查学校代码是否存在
exists = SchoolsServer.check_code_exists("BJ001")
```

### Classes 班级模型

```python
from OnlineJudgeSystem.model.Classes import Classes, ClassesServer

# 查询某学校的所有班级
classes = ClassesServer.select_sql_by_school(school_id=1, status=1)

# 查询班主任的班级
my_classes = ClassesServer.select_sql_by_teacher(teacher_id=10)

# 添加班级
cls = Classes()
cls.SchoolId = 1
cls.ClassName = "高一(1)班"
cls.Grade = "高一"
cls.TeacherId = 10
class_id = ClassesServer.insert_sql(cls)

# 获取班级学生列表
students = ClassesServer.get_students(class_id=1)

# 更新班级学生人数（从students表统计）
ClassesServer.update_student_count(class_id=1)
```

### Teachers 教师模型（扩展）

```python
from OnlineJudgeSystem.model.Teachers import Teachers, TeachersServer

# 教师注册（默认待审核）
teacher = Teachers()
teacher.UserName = "teacher001"
teacher.PWD = "123456"
teacher.Name = "张老师"
teacher.SchoolId = 1
server = TeachersServer()
server.insert_sql(teacher)  # approval_status自动设为0

# 查询待审核教师
pending_teachers = server.select_sql_pending_approval()

# 查询某学校的待审核教师
school_pending = server.select_sql_pending_approval(school_id=1)

# 审核教师（通过）
server.approve_teacher(
    teacher_id=10, 
    admin_id=1, 
    status=1,  # 1-通过, 2-拒绝
    reason=""
)

# 审核教师（拒绝）
server.approve_teacher(
    teacher_id=11, 
    admin_id=1, 
    status=2,
    reason="资料不全"
)

# 查询某学校的已审核教师
approved_teachers = server.select_sql_by_school(school_id=1, approval_status=1)
```

### Students 学生模型（扩展）

```python
from OnlineJudgeSystem.model.Students import Students, StudentsServer

# 学生注册（关联学校和班级）
student = Students()
student.UserName = "student001"
student.PWD = "123456"
student.Name = "王同学"
student.SchoolId = 1
student.ClassId = 5
student.Status = 1
server = StudentsServer()
server.insert_sql(student)

# 查询某学校的所有学生
students = server.select_sql_by_school(school_id=1)

# 查询某班级的所有学生
class_students = server.select_sql_by_class(class_id=5)

# 更新学生班级
server.update_class(student_id=100, new_class_id=6)
```

---

## 🎨 数据库查询示例

### 统计查询

```sql
-- 查看各学校统计
SELECT 
    s.school_name AS '学校名称',
    COUNT(DISTINCT t.Id) AS '教师数量',
    COUNT(DISTINCT st.Id) AS '学生数量',
    COUNT(DISTINCT c.id) AS '班级数量'
FROM schools s
LEFT JOIN teacher t ON t.school_id = s.id
LEFT JOIN students st ON st.school_id = s.id
LEFT JOIN classes c ON c.school_id = s.id
WHERE s.status = 1
GROUP BY s.id, s.school_name;

-- 待审核教师数量
SELECT COUNT(*) FROM teacher WHERE approval_status = 0;

-- 班级学生分布
SELECT 
    s.school_name AS '学校名称',
    c.class_name AS '班级名称',
    c.student_count AS '学生人数'
FROM classes c
INNER JOIN schools s ON c.school_id = s.id
WHERE c.status = 1
ORDER BY s.school_name, c.class_name;
```

### 关联查询

```sql
-- 查询学生的完整信息（包含学校和班级）
SELECT 
    st.Id, st.Name, st.User_Name,
    sc.school_name, c.class_name
FROM students st
LEFT JOIN schools sc ON st.school_id = sc.id
LEFT JOIN classes c ON st.class_id = c.id
WHERE st.status = 1;

-- 查询教师的完整信息（包含学校和审核状态）
SELECT 
    t.Id, t.Name, t.User_Name,
    s.school_name,
    CASE t.approval_status
        WHEN 0 THEN '待审核'
        WHEN 1 THEN '已通过'
        WHEN 2 THEN '已拒绝'
    END AS '审核状态'
FROM teacher t
LEFT JOIN schools s ON t.school_id = s.id;
```

---

## 🔐 审核状态说明

### approval_status 值
```
0 = 待审核（默认）
1 = 已通过
2 = 已拒绝
```

### 审核流程
```
1. 教师注册 → approval_status = 0（待审核）
2. 教师无法登录（登录查询加入 approval_status=1 条件）
3. 管理员审核 → 设置 approval_status = 1（通过）或 2（拒绝）
4. 审核通过 → 教师可以登录
5. 审核拒绝 → 记录拒绝原因，教师仍无法登录
```

---

## 🚀 快速启动命令

### 1. 备份数据库
```bash
mysqldump -u root -p onlinejudgesystem > backup_$(date +%Y%m%d).sql
```

### 2. 执行迁移
```bash
mysql -u root -p onlinejudgesystem < migration_multi_school.sql
```

### 3. 验证迁移
```bash
mysql -u root -p onlinejudgesystem -e "
SELECT '学校表' AS '表名', COUNT(*) AS '记录数' FROM schools
UNION ALL
SELECT '班级表', COUNT(*) FROM classes
UNION ALL
SELECT '教师(已更新)', COUNT(*) FROM teacher WHERE school_id IS NOT NULL
UNION ALL
SELECT '学生(已更新)', COUNT(*) FROM students WHERE school_id IS NOT NULL;
"
```

### 4. 启动应用
```bash
cd OnlineJudgeSystem
python runserver.py
```

---

## 📝 模型字段映射

### Python ↔ 数据库

#### Schools
```
Id            ↔ id
SchoolName    ↔ school_name
SchoolCode    ↔ school_code
Province      ↔ province
City          ↔ city
Address       ↔ address
ContactPerson ↔ contact_person
ContactPhone  ↔ contact_phone
Email         ↔ email
Status        ↔ status
CreatedAt     ↔ created_at
UpdatedAt     ↔ updated_at
```

#### Classes
```
Id            ↔ id
SchoolId      ↔ school_id
ClassName     ↔ class_name
ClassCode     ↔ class_code
Grade         ↔ grade
TeacherId     ↔ teacher_id
StudentCount  ↔ student_count
Description   ↔ description
Status        ↔ status
CreatedAt     ↔ created_at
UpdatedAt     ↔ updated_at
```

#### Teachers（新增字段）
```
SchoolId         ↔ school_id
ApprovalStatus   ↔ approval_status
ApprovalTime     ↔ approval_time
ApprovalAdminId  ↔ approval_admin_id
RejectionReason  ↔ rejection_reason
```

#### Students（新增字段）
```
SchoolId       ↔ school_id
ClassId        ↔ class_id
EnrollmentDate ↔ enrollment_date
Status         ↔ status
```

---

## ⚡ 常用代码片段

### Flask路由权限检查
```python
# 检查管理员登录
if 'adminuser' not in session:
    return jsonify({'code': 0, 'msg': '未登录'})

# 检查教师登录且已审核
if 'teacheruser' not in session:
    return jsonify({'code': 0, 'msg': '未登录'})
teacher = session['teacheruser']
if teacher.ApprovalStatus != 1:
    return jsonify({'code': 0, 'msg': '账号未审核通过'})

# 检查学生登录
if 'useruser' not in session:
    return jsonify({'code': 0, 'msg': '未登录'})
```

### AJAX调用示例
```javascript
// 获取学校列表
$.get('/api/schools/list', function(res) {
    if (res.code === 1) {
        console.log(res.data);  // 学校数组
    }
});

// 添加学校
$.ajax({
    url: '/api/schools/add',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        school_name: '北京第一中学',
        school_code: 'BJ001',
        province: '北京市',
        city: '朝阳区'
    }),
    success: function(res) {
        if (res.code === 1) {
            alert('添加成功');
        }
    }
});

// 审核教师
$.ajax({
    url: '/api/teachers/approve',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        teacher_id: 10,
        status: 1,  // 1-通过, 2-拒绝
        reason: ''
    }),
    success: function(res) {
        if (res.code === 1) {
            alert('审核成功');
        }
    }
});
```

---

## 🎯 下一步工作

1. ✅ 数据库迁移（执行 `migration_multi_school.sql`）
2. ⏳ 创建 `schoolviews.py`（学校/班级/审核API）
3. ⏳ 创建前端模板（schools.html, classes.html, teacher_approval.html）
4. ⏳ 更新注册表单（添加学校和班级选择）
5. ⏳ 更新 `__init__.py`（导入schoolviews）
6. ⏳ 测试所有功能

---

**快速参考完成！开始实施吧！** 🚀
