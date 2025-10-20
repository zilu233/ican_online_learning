# 多学校班级管理系统 - API接口文档

## 📋 API概览

本文档列出了多学校班级管理系统的所有API接口。

**基础URL**: `http://localhost:5555`  
**认证方式**: Session (需管理员登录)

---

## 🏫 学校管理API

### 1. 学校列表页面
```
GET /admin/schools
```
**说明**: 返回学校管理页面  
**权限**: 管理员  
**返回**: HTML页面

---

### 2. 获取学校列表
```
GET /api/schools/list
```
**说明**: 获取所有学校列表及统计信息  
**权限**: 管理员

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | int | 否 | 学校状态: 1-启用, 0-禁用 |

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "school_name": "默认学校",
      "school_code": "DEFAULT",
      "province": "北京",
      "city": "北京市",
      "address": "朝阳区xxx路",
      "contact_person": "张三",
      "contact_phone": "13800138000",
      "email": "school@example.com",
      "status": 1,
      "created_at": "2025-10-18 18:57:00",
      "teacher_count": 6,
      "student_count": 5,
      "class_count": 4,
      "pending_teacher_count": 2
    }
  ]
}
```

---

### 3. 添加学校
```
POST /api/schools/add
```
**说明**: 添加新学校  
**权限**: 管理员  
**Content-Type**: application/json

**请求体**:
```json
{
  "school_name": "北京第一中学",
  "school_code": "BJ001",
  "province": "北京",
  "city": "北京市",
  "address": "朝阳区xxx路",
  "contact_person": "李四",
  "contact_phone": "13900139000",
  "email": "bj001@example.com",
  "status": 1
}
```

**返回示例**:
```json
{
  "code": 1,
  "msg": "添加成功",
  "school_id": 5
}
```

---

### 4. 更新学校
```
POST /api/schools/update
```
**说明**: 更新学校信息  
**权限**: 管理员  
**Content-Type**: application/json

**请求体**:
```json
{
  "id": 1,
  "school_name": "北京第一中学(更新)",
  "school_code": "BJ001",
  "province": "北京",
  "city": "北京市",
  "address": "朝阳区yyy路",
  "contact_person": "王五",
  "contact_phone": "13700137000",
  "email": "bj001@example.com",
  "status": 1
}
```

**返回示例**:
```json
{
  "code": 1,
  "msg": "更新成功"
}
```

---

### 5. 启用/禁用学校
```
POST /api/schools/toggle_status
```
**说明**: 切换学校启用状态  
**权限**: 管理员

**请求体**:
```json
{
  "id": 1,
  "status": 0
}
```

**返回示例**:
```json
{
  "code": 1,
  "msg": "操作成功"
}
```

---

### 6. 学校详情
```
GET /api/schools/detail/<school_id>
```
**说明**: 获取学校详细信息  
**权限**: 管理员

**返回示例**:
```json
{
  "code": 1,
  "data": {
    "id": 1,
    "school_name": "默认学校",
    "school_code": "DEFAULT",
    "province": "北京",
    "city": "北京市",
    "address": "朝阳区xxx路",
    "contact_person": "张三",
    "contact_phone": "13800138000",
    "email": "school@example.com",
    "status": 1,
    "created_at": "2025-10-18 18:57:00",
    "teacher_count": 6,
    "student_count": 5,
    "class_count": 4,
    "pending_teacher_count": 2
  }
}
```

---

### 7. 获取所有启用的学校(下拉框用)
```
GET /api/schools/all_active
```
**说明**: 获取所有启用状态的学校（用于下拉框选择）  
**权限**: 无需登录

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "school_name": "默认学校",
      "school_code": "DEFAULT"
    },
    {
      "id": 2,
      "school_name": "北京第一中学",
      "school_code": "BJ001"
    }
  ]
}
```

---

## 🎓 班级管理API

### 8. 班级列表页面
```
GET /admin/classes
```
**说明**: 返回班级管理页面  
**权限**: 管理员  
**返回**: HTML页面

---

### 9. 获取班级列表
```
GET /api/classes/list
```
**说明**: 获取班级列表  
**权限**: 管理员

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| school_id | int | 否 | 学校ID（不传则返回所有学校） |

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "school_id": 1,
      "school_name": "默认学校",
      "class_name": "计算机科学1班",
      "class_code": "CS101",
      "grade": "2023",
      "teacher_id": 1,
      "teacher_name": "李老师",
      "student_count": 30,
      "description": "计算机科学专业1班",
      "status": 1
    }
  ]
}
```

---

### 10. 添加班级
```
POST /api/classes/add
```
**说明**: 添加新班级  
**权限**: 管理员

**请求体**:
```json
{
  "school_id": 1,
  "class_name": "高一(1)班",
  "class_code": "G101",
  "grade": "2025",
  "teacher_id": 2,
  "description": "高一年级1班"
}
```

**返回示例**:
```json
{
  "code": 1,
  "msg": "添加成功",
  "class_id": 10
}
```

---

### 11. 更新班级
```
POST /api/classes/update
```
**说明**: 更新班级信息  
**权限**: 管理员

**请求体**:
```json
{
  "id": 1,
  "school_id": 1,
  "class_name": "计算机科学1班(更新)",
  "class_code": "CS101",
  "grade": "2023",
  "teacher_id": 2,
  "description": "计算机科学专业1班(更新)",
  "status": 1
}
```

**返回示例**:
```json
{
  "code": 1,
  "msg": "更新成功"
}
```

---

### 12. 班级详情
```
GET /api/classes/detail/<class_id>
```
**说明**: 获取班级详细信息  
**权限**: 管理员

**返回示例**:
```json
{
  "code": 1,
  "data": {
    "id": 1,
    "school_id": 1,
    "school_name": "默认学校",
    "class_name": "计算机科学1班",
    "class_code": "CS101",
    "grade": "2023",
    "teacher_id": 1,
    "teacher_name": "李老师",
    "student_count": 30,
    "description": "计算机科学专业1班",
    "status": 1
  }
}
```

---

### 13. 根据学校获取班级(下拉框用)
```
GET /api/classes/by_school/<school_id>
```
**说明**: 根据学校ID获取班级列表（用于下拉框）  
**权限**: 无需登录

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "class_name": "计算机科学1班",
      "class_code": "CS101",
      "grade": "2023"
    }
  ]
}
```

---

### 14. 获取班级学生列表
```
GET /api/classes/students/<class_id>
```
**说明**: 获取指定班级的学生列表  
**权限**: 管理员

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "username": "2327409011",
      "name": "杨超",
      "card": "110101199001011234",
      "phone": "13800138001",
      "status": 1
    }
  ]
}
```

---

## 👨‍🏫 教师审核API

### 15. 教师审核页面
```
GET /admin/teacher_approval
```
**说明**: 返回教师审核页面  
**权限**: 管理员  
**返回**: HTML页面

---

### 16. 获取待审核教师列表
```
GET /api/teachers/pending
```
**说明**: 获取待审核的教师列表  
**权限**: 管理员

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| school_id | int | 否 | 学校ID（不传则返回所有学校） |

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 7,
      "username": "teacher_bj_001",
      "name": "测试教师1",
      "school_id": 2,
      "school_name": "北京第一中学",
      "card": "110101199001011234",
      "phone": "13900139001",
      "address": "北京市朝阳区",
      "approval_status": 0
    }
  ]
}
```

---

### 17. 审核教师
```
POST /api/teachers/approve
```
**说明**: 审核教师(通过或拒绝)  
**权限**: 管理员

**请求体**:
```json
{
  "teacher_id": 7,
  "status": 1,
  "reason": ""
}
```

**参数说明**:
- `status`: 1-审核通过, 2-拒绝
- `reason`: 拒绝原因(status=2时需要填写)

**返回示例**:
```json
{
  "code": 1,
  "msg": "审核通过"
}
```

---

### 18. 根据学校获取教师(下拉框用)
```
GET /api/teachers/by_school/<school_id>
```
**说明**: 根据学校ID获取已审核通过的教师列表（用于下拉框）  
**权限**: 无需登录

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "username": "lilaoshi",
      "name": "李老师"
    }
  ]
}
```

---

### 19. 获取所有已审核教师
```
GET /api/teachers/all_approved
```
**说明**: 获取所有已审核通过的教师列表  
**权限**: 管理员

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| school_id | int | 否 | 学校ID（不传则返回所有学校） |

**返回示例**:
```json
{
  "code": 1,
  "data": [
    {
      "id": 1,
      "username": "lilaoshi",
      "name": "李老师",
      "school_id": 1,
      "school_name": "默认学校",
      "card": "110101199001011234",
      "phone": "13800138000",
      "address": "北京市"
    }
  ]
}
```

---

## 📊 统计API

### 20. 系统总体统计
```
GET /api/statistics/overview
```
**说明**: 获取系统总体统计数据  
**权限**: 管理员

**返回示例**:
```json
{
  "code": 1,
  "data": {
    "school_count": 4,
    "class_count": 9,
    "teacher_count": 4,
    "student_count": 5,
    "pending_teacher_count": 2
  }
}
```

---

## ❌ 错误响应

所有API在错误时返回统一格式：

```json
{
  "code": 0,
  "msg": "错误信息"
}
```

常见错误：
- `code: 0, msg: "未登录"` - 需要管理员登录
- `code: 0, msg: "学校代码已存在"` - 学校代码重复
- `code: 0, msg: "该学校已存在同名班级"` - 班级名称重复
- `code: 0, msg: "学校不存在"` - 学校ID无效
- `code: 0, msg: "班级不存在"` - 班级ID无效

---

## 🔐 权限说明

### 需要管理员登录的API:
- 所有 `/admin/*` 页面
- 所有 `/api/schools/*` 管理API
- 所有 `/api/classes/*` 管理API
- 所有 `/api/teachers/pending` 和 `/api/teachers/approve` API
- `/api/statistics/overview`

### 无需登录的API:
- `/api/schools/all_active` - 学校下拉框
- `/api/classes/by_school/<school_id>` - 班级下拉框
- `/api/teachers/by_school/<school_id>` - 教师下拉框

这些API用于注册表单，任何用户都可以访问。

---

## 📝 使用示例

### JavaScript调用示例

#### 获取学校列表
```javascript
fetch('/api/schools/list')
  .then(response => response.json())
  .then(data => {
    if (data.code === 1) {
      console.log('学校列表:', data.data);
    } else {
      console.error('错误:', data.msg);
    }
  });
```

#### 添加学校
```javascript
fetch('/api/schools/add', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    school_name: '测试学校',
    school_code: 'TEST001',
    province: '北京',
    city: '北京市',
    status: 1
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.code === 1) {
      console.log('添加成功, ID:', data.school_id);
    } else {
      alert('错误: ' + data.msg);
    }
  });
```

#### 审核教师
```javascript
fetch('/api/teachers/approve', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    teacher_id: 7,
    status: 1,  // 1-通过, 2-拒绝
    reason: ''
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.code === 1) {
      alert(data.msg);  // "审核通过"
    }
  });
```

#### 加载学校到下拉框
```javascript
fetch('/api/schools/all_active')
  .then(response => response.json())
  .then(data => {
    if (data.code === 1) {
      const select = document.getElementById('school_select');
      data.data.forEach(school => {
        const option = document.createElement('option');
        option.value = school.id;
        option.textContent = school.school_name;
        select.appendChild(option);
      });
    }
  });
```

#### 学校变化时加载班级(级联下拉框)
```javascript
document.getElementById('school_select').addEventListener('change', function() {
  const schoolId = this.value;
  
  fetch(`/api/classes/by_school/${schoolId}`)
    .then(response => response.json())
    .then(data => {
      if (data.code === 1) {
        const classSelect = document.getElementById('class_select');
        classSelect.innerHTML = '<option value="">请选择班级</option>';
        
        data.data.forEach(cls => {
          const option = document.createElement('option');
          option.value = cls.id;
          option.textContent = cls.class_name;
          classSelect.appendChild(option);
        });
      }
    });
});
```

---

## 🚀 快速开始

1. **启动Flask应用**
```bash
python runserver.py
```

2. **使用管理员账号登录**
- 访问: http://localhost:5555/admin/login

3. **访问管理页面**
- 学校管理: http://localhost:5555/admin/schools
- 班级管理: http://localhost:5555/admin/classes
- 教师审核: http://localhost:5555/admin/teacher_approval

4. **测试API**
使用浏览器开发者工具的Console或Postman测试API

---

**文档版本**: v1.0  
**更新日期**: 2025年10月18日  
**作者**: GitHub Copilot
