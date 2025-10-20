# 多学校班级管理系统 - 设计方案

## 📋 需求分析

### 核心需求
1. **多学校支持**: 平台面向所有学校
2. **学校属性**: 教师和学生都需要归属于特定学校
3. **分校管理**: 根据学校进行班级、教师、学生的管理
4. **统一管理员**: 管理员不分学校，可以审核所有学校的教师

---

## 🏗️ 数据库设计

### 新增表结构

#### 1. 学校表 (schools)
```sql
CREATE TABLE `schools` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `school_name` VARCHAR(100) NOT NULL COMMENT '学校名称',
  `school_code` VARCHAR(50) UNIQUE NOT NULL COMMENT '学校代码',
  `province` VARCHAR(50) DEFAULT NULL COMMENT '省份',
  `city` VARCHAR(50) DEFAULT NULL COMMENT '城市',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
  `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '联系人',
  `contact_phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态:1-启用,0-禁用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_school_code` (`school_code`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='学校信息表';
```

#### 2. 班级表 (classes)
```sql
CREATE TABLE `classes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `school_id` INT(11) NOT NULL COMMENT '学校ID',
  `class_name` VARCHAR(100) NOT NULL COMMENT '班级名称',
  `grade` VARCHAR(50) DEFAULT NULL COMMENT '年级',
  `teacher_id` INT(11) DEFAULT NULL COMMENT '班主任ID',
  `student_count` INT(11) DEFAULT 0 COMMENT '学生人数',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态:1-启用,0-禁用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_school_id` (`school_id`),
  INDEX `idx_teacher_id` (`teacher_id`),
  FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='班级信息表';
```

### 修改现有表结构

#### 3. 教师表 (teacher) - 添加学校关联和审核状态
```sql
ALTER TABLE `teacher` 
ADD COLUMN `school_id` INT(11) DEFAULT NULL COMMENT '学校ID' AFTER `Id`,
ADD COLUMN `approval_status` TINYINT(1) DEFAULT 0 COMMENT '审核状态:0-待审核,1-已通过,2-已拒绝' AFTER `Address`,
ADD COLUMN `approval_time` DATETIME DEFAULT NULL COMMENT '审核时间' AFTER `approval_status`,
ADD COLUMN `approval_admin_id` INT(11) DEFAULT NULL COMMENT '审核管理员ID' AFTER `approval_time`,
ADD COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD INDEX `idx_school_id` (`school_id`),
ADD INDEX `idx_approval_status` (`approval_status`),
ADD FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE SET NULL;
```

#### 4. 学生表 (students) - 添加学校和班级关联
```sql
ALTER TABLE `students` 
ADD COLUMN `school_id` INT(11) DEFAULT NULL COMMENT '学校ID' AFTER `Id`,
ADD COLUMN `class_id` INT(11) DEFAULT NULL COMMENT '班级ID' AFTER `school_id`,
CHANGE COLUMN `Classes` `Classes` VARCHAR(60) DEFAULT NULL COMMENT '班级名称(保留兼容)',
ADD COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD INDEX `idx_school_id` (`school_id`),
ADD INDEX `idx_class_id` (`class_id`),
ADD FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE SET NULL,
ADD FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE SET NULL;
```

---

## 📊 数据模型关系

```
schools (学校)
  ├── 1:N → teachers (教师)
  ├── 1:N → students (学生)
  └── 1:N → classes (班级)
           └── 1:N → students (学生)

admins (管理员) - 全局，不关联学校
  └── 审核 → teachers (教师)
```

---

## 🔑 核心功能模块

### 1. 学校管理 (管理员)
- ✅ 添加/编辑/删除学校
- ✅ 查看学校列表
- ✅ 启用/禁用学校
- ✅ 查看学校统计信息（教师数、学生数、班级数）

### 2. 教师审核 (管理员)
- ✅ 查看待审核教师列表（所有学校）
- ✅ 审核通过/拒绝教师注册
- ✅ 按学校筛选教师
- ✅ 查看教师详细信息

### 3. 班级管理 (管理员/教师)
- ✅ 按学校查看班级列表
- ✅ 添加/编辑/删除班级
- ✅ 分配班主任
- ✅ 查看班级学生列表

### 4. 学生管理 (管理员/教师)
- ✅ 按学校查看学生列表
- ✅ 按班级查看学生列表
- ✅ 添加/编辑/删除学生
- ✅ 学生班级调整

### 5. 注册流程优化
- ✅ 教师注册时选择学校（待审核）
- ✅ 学生注册时选择学校和班级
- ✅ 自动关联学校信息

---

## 🎨 用户界面改进

### 管理员界面
1. **学校管理**
   - 学校列表页面
   - 学校添加/编辑表单
   - 学校统计仪表板

2. **教师审核**
   - 待审核列表（高亮显示）
   - 审核操作按钮
   - 学校筛选器

3. **统计Dashboard**
   - 各学校教师/学生数量
   - 待审核教师数量
   - 班级统计

### 教师/学生注册界面
1. **学校选择下拉框**
2. **班级选择下拉框**（学生）
3. **审核状态提示**（教师）

---

## 🔐 权限设计

### 管理员 (Admin)
- ✅ 全局权限
- ✅ 所有学校的增删改查
- ✅ 所有教师的审核
- ✅ 所有班级和学生的管理

### 教师 (Teacher)
- ✅ 只能查看/管理自己学校的信息
- ✅ 只能管理自己负责的班级
- ✅ 审核通过后才能使用系统

### 学生 (Student)
- ✅ 只能查看自己学校的信息
- ✅ 只能查看自己班级的信息
- ✅ 参与考试和练习

---

## 📝 实施步骤

### 第一阶段：数据库升级
1. ✅ 创建学校表和班级表
2. ✅ 修改教师表和学生表
3. ✅ 插入测试学校数据
4. ✅ 数据迁移脚本

### 第二阶段：后端模型更新
1. ✅ 创建School模型
2. ✅ 创建Class模型
3. ✅ 更新Teacher模型
4. ✅ 更新Student模型

### 第三阶段：业务逻辑实现
1. ✅ 学校管理API
2. ✅ 班级管理API
3. ✅ 教师审核API
4. ✅ 注册流程更新

### 第四阶段：前端界面开发
1. ✅ 学校管理页面
2. ✅ 班级管理页面
3. ✅ 教师审核页面
4. ✅ 注册表单更新

---

## 🎯 核心改进点

### 1. 数据隔离
- 教师和学生按学校隔离
- 班级归属于特定学校
- 确保数据安全性

### 2. 灵活管理
- 支持多学校接入
- 统一管理员审核
- 按学校分级管理

### 3. 扩展性
- 易于添加新学校
- 支持学校数量扩展
- 预留扩展字段

### 4. 用户体验
- 简化注册流程
- 清晰的审核状态
- 直观的管理界面

---

## 📌 注意事项

1. **向后兼容**: 保留原有Classes字段，逐步迁移
2. **数据完整性**: 使用外键约束保证数据一致性
3. **性能优化**: 添加必要的索引
4. **审核机制**: 教师需审核通过后才能使用系统
5. **数据迁移**: 现有数据需要关联到默认学校

---

## 🚀 预期效果

1. ✅ **多学校支持** - 系统可服务多个学校
2. ✅ **统一管理** - 管理员统一审核所有学校教师
3. ✅ **数据隔离** - 各学校数据相互独立
4. ✅ **灵活扩展** - 易于添加新学校和班级
5. ✅ **提升体验** - 更清晰的层级结构

---

## 📊 示例数据结构

### 学校示例
```json
{
  "id": 1,
  "school_name": "北京第一中学",
  "school_code": "BJ001",
  "province": "北京市",
  "city": "朝阳区",
  "teacher_count": 50,
  "student_count": 800,
  "class_count": 20
}
```

### 班级示例
```json
{
  "id": 1,
  "school_id": 1,
  "class_name": "高一(1)班",
  "grade": "高一",
  "teacher_id": 10,
  "student_count": 45
}
```

### 教师示例
```json
{
  "id": 10,
  "school_id": 1,
  "username": "lilaoshi",
  "name": "李老师",
  "approval_status": 1,
  "classes": ["高一(1)班", "高一(2)班"]
}
```

---

**设计完成！接下来将开始实施。**
