# 多学校班级管理系统 - 实施指南

## 🎯 实施概览

本指南将帮助您逐步实施多学校班级管理系统升级。

---

## 📦 已完成的工作

### 1. ✅ 数据库设计
- **文件**: `migration_multi_school.sql`
- **内容**: 完整的数据库迁移脚本
  - 创建 `schools` 表（学校信息）
  - 创建 `classes` 表（班级信息）
  - 修改 `teacher` 表（添加学校关联和审核状态）
  - 修改 `students` 表（添加学校和班级关联）
  - 数据迁移脚本（兼容现有数据）
  - 测试数据插入

### 2. ✅ Python模型层
- **Schools.py** - 学校模型
  - `Schools` 实体类
  - `SchoolsServer` 服务类（CRUD + 统计）
  
- **Classes.py** - 班级模型
  - `Classes` 实体类
  - `ClassesServer` 服务类（CRUD + 学生管理）
  
- **Students.py** - 学生模型（已扩展）
  - 新增字段：`SchoolId`, `ClassId`, `EnrollmentDate`, `Status`
  - 新增方法：`select_sql_by_school`, `select_sql_by_class`, `update_class`
  - 更新 `insert_sql` 和 `update_sql` 支持新字段
  
- **Teachers.py** - 教师模型（已扩展）
  - 新增字段：`SchoolId`, `ApprovalStatus`, `ApprovalTime`, `ApprovalAdminId`
  - 新增方法：`select_sql_pending_approval`, `approve_teacher`, `select_sql_by_school`
  - 登录检查审核状态（只允许已审核通过的教师登录）

### 3. ✅ 设计文档
- **SCHOOL_MANAGEMENT_DESIGN.md** - 完整设计方案

---

## 🚀 实施步骤

### 阶段一：数据库迁移 ⚠️

#### 1. 备份数据库
```bash
# 在执行迁移前务必备份！
mysqldump -u root -p onlinejudgesystem > backup_before_migration.sql
```

#### 2. 执行迁移脚本
```bash
# 方式1: 命令行执行
mysql -u root -p onlinejudgesystem < migration_multi_school.sql

# 方式2: MySQL客户端执行
USE onlinejudgesystem;
SOURCE /path/to/migration_multi_school.sql;
```

#### 3. 验证迁移结果
```sql
-- 检查表是否创建成功
SHOW TABLES;

-- 检查学校数据
SELECT * FROM schools;

-- 检查班级数据
SELECT * FROM classes;

-- 检查学生的school_id是否已更新
SELECT Id, Name, school_id, class_id FROM students LIMIT 10;

-- 检查教师的school_id和审核状态
SELECT Id, Name, school_id, approval_status FROM teacher LIMIT 10;
```

---

### 阶段二：创建视图层（Views）

#### 1. 创建学校管理视图文件
需要创建 `OnlineJudgeSystem/schoolviews.py`，包含：

```python
# -*- coding: utf-8 -*-
from flask import request, jsonify, session, render_template
from OnlineJudgeSystem import app
from OnlineJudgeSystem.model.Schools import Schools, SchoolsServer
from OnlineJudgeSystem.model.Classes import Classes, ClassesServer
from OnlineJudgeSystem.model.Teachers import TeachersServer
from OnlineJudgeSystem.model.Students import StudentsServer


# ============ 学校管理 ============

@app.route('/admin/schools')
def admin_schools():
    """学校列表页面"""
    if 'adminuser' not in session:
        return render_template('login.html')
    return render_template('admin/schools.html')


@app.route('/api/schools/list', methods=['GET'])
def api_schools_list():
    """获取学校列表API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    status = request.args.get('status', None)
    if status is not None:
        status = int(status)
    
    schools = SchoolsServer.select_sql_all(status)
    
    # 获取每个学校的统计信息
    result = []
    for school in schools:
        stats = SchoolsServer.get_statistics(school.Id)
        result.append({
            'id': school.Id,
            'school_name': school.SchoolName,
            'school_code': school.SchoolCode,
            'province': school.Province,
            'city': school.City,
            'address': school.Address,
            'contact_person': school.ContactPerson,
            'contact_phone': school.ContactPhone,
            'email': school.Email,
            'status': school.Status,
            'created_at': school.CreatedAt,
            'teacher_count': stats['teacher_count'],
            'student_count': stats['student_count'],
            'class_count': stats['class_count'],
            'pending_teacher_count': stats['pending_teacher_count']
        })
    
    return jsonify({'code': 1, 'data': result})


@app.route('/api/schools/add', methods=['POST'])
def api_schools_add():
    """添加学校API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    
    # 检查学校代码是否已存在
    if SchoolsServer.check_code_exists(data['school_code']):
        return jsonify({'code': 0, 'msg': '学校代码已存在'})
    
    school = Schools()
    school.SchoolName = data['school_name']
    school.SchoolCode = data['school_code']
    school.Province = data.get('province', '')
    school.City = data.get('city', '')
    school.Address = data.get('address', '')
    school.ContactPerson = data.get('contact_person', '')
    school.ContactPhone = data.get('contact_phone', '')
    school.Email = data.get('email', '')
    school.Status = data.get('status', 1)
    
    school_id = SchoolsServer.insert_sql(school)
    
    return jsonify({'code': 1, 'msg': '添加成功', 'school_id': school_id})


@app.route('/api/schools/update', methods=['POST'])
def api_schools_update():
    """更新学校API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    
    # 检查学校代码是否已被其他学校使用
    if SchoolsServer.check_code_exists(data['school_code'], exclude_id=data['id']):
        return jsonify({'code': 0, 'msg': '学校代码已被其他学校使用'})
    
    school = Schools()
    school.Id = data['id']
    school.SchoolName = data['school_name']
    school.SchoolCode = data['school_code']
    school.Province = data.get('province', '')
    school.City = data.get('city', '')
    school.Address = data.get('address', '')
    school.ContactPerson = data.get('contact_person', '')
    school.ContactPhone = data.get('contact_phone', '')
    school.Email = data.get('email', '')
    school.Status = data.get('status', 1)
    
    SchoolsServer.update_sql(school)
    
    return jsonify({'code': 1, 'msg': '更新成功'})


@app.route('/api/schools/toggle_status', methods=['POST'])
def api_schools_toggle_status():
    """启用/禁用学校API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    school_id = data['id']
    status = data['status']
    
    SchoolsServer.update_status(school_id, status)
    
    return jsonify({'code': 1, 'msg': '操作成功'})


# ============ 班级管理 ============

@app.route('/admin/classes')
def admin_classes():
    """班级列表页面"""
    if 'adminuser' not in session:
        return render_template('login.html')
    return render_template('admin/classes.html')


@app.route('/api/classes/list', methods=['GET'])
def api_classes_list():
    """获取班级列表API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    school_id = request.args.get('school_id', None)
    if school_id:
        school_id = int(school_id)
    
    classes = ClassesServer.select_sql_all(school_id=school_id, status=1)
    
    result = []
    for cls in classes:
        result.append({
            'id': cls.Id,
            'school_id': cls.SchoolId,
            'school_name': cls.SchoolName,
            'class_name': cls.ClassName,
            'class_code': cls.ClassCode,
            'grade': cls.Grade,
            'teacher_id': cls.TeacherId,
            'teacher_name': cls.TeacherName,
            'student_count': cls.StudentCount,
            'description': cls.Description,
            'status': cls.Status
        })
    
    return jsonify({'code': 1, 'data': result})


@app.route('/api/classes/add', methods=['POST'])
def api_classes_add():
    """添加班级API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    
    # 检查班级名称在该学校是否已存在
    if ClassesServer.check_name_exists(data['school_id'], data['class_name']):
        return jsonify({'code': 0, 'msg': '该学校已存在同名班级'})
    
    cls = Classes()
    cls.SchoolId = data['school_id']
    cls.ClassName = data['class_name']
    cls.ClassCode = data.get('class_code', '')
    cls.Grade = data.get('grade', '')
    cls.TeacherId = data.get('teacher_id', 0)
    cls.Description = data.get('description', '')
    cls.Status = 1
    
    class_id = ClassesServer.insert_sql(cls)
    
    return jsonify({'code': 1, 'msg': '添加成功', 'class_id': class_id})


@app.route('/api/classes/update', methods=['POST'])
def api_classes_update():
    """更新班级API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    
    # 检查班级名称
    if ClassesServer.check_name_exists(data['school_id'], data['class_name'], exclude_id=data['id']):
        return jsonify({'code': 0, 'msg': '该学校已存在同名班级'})
    
    cls = Classes()
    cls.Id = data['id']
    cls.SchoolId = data['school_id']
    cls.ClassName = data['class_name']
    cls.ClassCode = data.get('class_code', '')
    cls.Grade = data.get('grade', '')
    cls.TeacherId = data.get('teacher_id', 0)
    cls.Description = data.get('description', '')
    cls.Status = data.get('status', 1)
    
    ClassesServer.update_sql(cls)
    
    return jsonify({'code': 1, 'msg': '更新成功'})


# ============ 教师审核 ============

@app.route('/admin/teacher_approval')
def admin_teacher_approval():
    """教师审核页面"""
    if 'adminuser' not in session:
        return render_template('login.html')
    return render_template('admin/teacher_approval.html')


@app.route('/api/teachers/pending', methods=['GET'])
def api_teachers_pending():
    """获取待审核教师列表API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    school_id = request.args.get('school_id', None)
    if school_id:
        school_id = int(school_id)
    
    server = TeachersServer()
    teachers = server.select_sql_pending_approval(school_id)
    
    result = []
    for teacher in teachers:
        result.append({
            'id': teacher.Id,
            'username': teacher.UserName,
            'name': teacher.Name,
            'school_id': teacher.SchoolId,
            'school_name': teacher.SchoolName,
            'card': teacher.Card,
            'phone': teacher.Phone,
            'address': teacher.Address,
            'approval_status': teacher.ApprovalStatus
        })
    
    return jsonify({'code': 1, 'data': result})


@app.route('/api/teachers/approve', methods=['POST'])
def api_teachers_approve():
    """审核教师API"""
    if 'adminuser' not in session:
        return jsonify({'code': 0, 'msg': '未登录'})
    
    data = request.get_json()
    teacher_id = data['teacher_id']
    status = data['status']  # 1-通过, 2-拒绝
    reason = data.get('reason', '')
    
    admin_id = session.get('adminuser').Id
    
    server = TeachersServer()
    server.approve_teacher(teacher_id, admin_id, status, reason)
    
    msg = '审核通过' if status == 1 else '已拒绝'
    return jsonify({'code': 1, 'msg': msg})
```

#### 2. 更新 `__init__.py` 导入新视图

在 `OnlineJudgeSystem/__init__.py` 中添加：
```python
from OnlineJudgeSystem import schoolviews  # 新增
```

---

### 阶段三：创建前端模板

#### 1. 学校列表页面 `templates/admin/schools.html`
#### 2. 班级管理页面 `templates/admin/classes.html`
#### 3. 教师审核页面 `templates/admin/teacher_approval.html`

（模板代码较长，建议单独创建）

---

### 阶段四：更新注册流程

#### 1. 修改教师注册表单
- 添加学校选择下拉框
- 注册后显示"等待审核"提示
- 修改 `register.html` 或 `loginAndRegister.html`

#### 2. 修改学生注册表单
- 添加学校选择下拉框
- 添加班级选择下拉框（动态加载）

#### 3. 更新 `views.py` 注册逻辑
```python
# 在教师注册时设置school_id
teacher.SchoolId = request.form['school_id']

# 在学生注册时设置school_id和class_id
student.SchoolId = request.form['school_id']
student.ClassId = request.form['class_id']
```

---

## ⚠️ 注意事项

### 1. 数据备份
- **执行迁移前必须备份数据库**
- 建议在测试环境先验证

### 2. 兼容性
- 保留了 `Classes` 字符串字段，现有功能不受影响
- 逐步迁移到新的关系型结构

### 3. 审核机制
- 新注册教师默认审核状态为待审核（0）
- 只有审核通过的教师才能登录系统
- 现有教师在迁移时自动设置为已通过（1）

### 4. 性能优化
- 已在关键字段添加索引
- 关联查询使用 LEFT JOIN

### 5. 外键约束
- 学校删除会级联删除班级
- 学校删除会将教师/学生的 school_id 设为 NULL
- 班级删除会将学生的 class_id 设为 NULL

---

## 🧪 测试清单

### 数据库测试
- [ ] 学校表创建成功
- [ ] 班级表创建成功
- [ ] 教师表字段添加成功
- [ ] 学生表字段添加成功
- [ ] 现有数据迁移成功
- [ ] 外键约束生效

### 功能测试
- [ ] 管理员可以添加学校
- [ ] 管理员可以创建班级
- [ ] 管理员可以查看待审核教师
- [ ] 管理员可以审核通过教师
- [ ] 管理员可以拒绝教师
- [ ] 教师注册后状态为待审核
- [ ] 待审核教师无法登录
- [ ] 已通过教师可以正常登录
- [ ] 学生可以选择学校和班级注册
- [ ] 按学校筛选教师列表
- [ ] 按学校筛选学生列表
- [ ] 按班级查看学生列表

### 权限测试
- [ ] 未登录无法访问管理页面
- [ ] 教师只能查看自己学校的数据
- [ ] 学生只能查看自己学校和班级的数据
- [ ] 管理员可以查看所有学校的数据

---

## 📊 预期改进

实施完成后，系统将具备：

1. ✅ **多学校支持** - 平台可服务多个学校
2. ✅ **统一审核** - 管理员统一审核所有学校教师
3. ✅ **数据隔离** - 各学校数据相互独立
4. ✅ **层级管理** - 学校 → 班级 → 学生清晰层级
5. ✅ **灵活扩展** - 易于添加新学校和班级

---

## 📞 需要帮助？

如果在实施过程中遇到问题，请检查：
1. 数据库连接配置是否正确
2. 字段名大小写是否匹配
3. Python模型文件路径是否正确
4. Flask路由是否正确注册

**祝实施顺利！** 🎉
