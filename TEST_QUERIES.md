# 数据库迁移测试 SQL 脚本

## 测试1: 检查表结构
```sql
-- 检查schools表
DESCRIBE schools;

-- 检查classes表
DESCRIBE classes;

-- 检查teacher表的新字段
SHOW COLUMNS FROM teacher WHERE Field IN ('school_id', 'approval_status', 'approval_time', 'approval_admin_id', 'rejection_reason');

-- 检查students表的新字段
SHOW COLUMNS FROM students WHERE Field IN ('school_id', 'class_id', 'enrollment_date', 'status');
```

## 测试2: 检查外键约束
```sql
-- 检查所有外键
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'onlinejudgesystem'
AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, COLUMN_NAME;
```

## 测试3: 数据完整性检查
```sql
-- 学校统计
SELECT 
    s.school_name AS '学校名称',
    s.school_code AS '学校代码',
    (SELECT COUNT(*) FROM teacher WHERE school_id = s.id) AS '教师数',
    (SELECT COUNT(*) FROM students WHERE school_id = s.id) AS '学生数',
    (SELECT COUNT(*) FROM classes WHERE school_id = s.id) AS '班级数',
    CASE s.status WHEN 1 THEN '启用' ELSE '禁用' END AS '状态'
FROM schools s
ORDER BY s.school_code;

-- 班级详情
SELECT 
    s.school_name AS '学校',
    c.class_name AS '班级名称',
    c.grade AS '年级',
    c.student_count AS '学生数',
    CASE c.status WHEN 1 THEN '启用' ELSE '禁用' END AS '状态'
FROM classes c
LEFT JOIN schools s ON c.school_id = s.id
ORDER BY s.school_name, c.grade, c.class_name;

-- 教师详情
SELECT 
    t.UserName AS '用户名',
    t.RealName AS '真实姓名',
    s.school_name AS '学校',
    CASE t.approval_status 
        WHEN 0 THEN '待审核'
        WHEN 1 THEN '已通过'
        WHEN 2 THEN '已拒绝'
        ELSE '未知'
    END AS '审核状态'
FROM teacher t
LEFT JOIN schools s ON t.school_id = s.id
ORDER BY s.school_name, t.RealName;

-- 学生详情
SELECT 
    st.UserName AS '用户名',
    st.RealName AS '真实姓名',
    s.school_name AS '学校',
    c.class_name AS '班级',
    st.Classes AS '旧班级字段',
    CASE st.status 
        WHEN 1 THEN '正常'
        WHEN 0 THEN '禁用'
        ELSE 'NULL'
    END AS '状态'
FROM students st
LEFT JOIN schools s ON st.school_id = s.id
LEFT JOIN classes c ON st.class_id = c.id
ORDER BY s.school_name, c.class_name, st.RealName;
```

## 测试4: 教师登录测试
```sql
-- 查看所有教师的审核状态
SELECT 
    UserName,
    RealName,
    approval_status,
    CASE approval_status 
        WHEN 0 THEN '待审核-无法登录'
        WHEN 1 THEN '已通过-可以登录'
        WHEN 2 THEN '已拒绝-无法登录'
        ELSE '未知状态'
    END AS '登录权限'
FROM teacher
ORDER BY approval_status, UserName;
```

## 测试5: 向后兼容性测试
```sql
-- 检查旧字段是否保留
SELECT 
    'students表' AS '表名',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.COLUMNS 
                     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
                     AND TABLE_NAME = 'students' 
                     AND COLUMN_NAME = 'Classes') 
         THEN '✓ Classes字段保留' 
         ELSE '✗ Classes字段缺失' 
    END AS '检查结果'
UNION ALL
SELECT 
    'teacher表',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.COLUMNS 
                     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
                     AND TABLE_NAME = 'teacher' 
                     AND COLUMN_NAME = 'Classes') 
         THEN '✓ Classes字段保留' 
         ELSE '✗ Classes字段缺失' 
    END;

-- 查看旧字段数据
SELECT 
    '学生' AS '类型',
    UserName AS '用户名',
    Classes AS '旧班级数据'
FROM students
WHERE Classes IS NOT NULL AND Classes != ''
LIMIT 5
UNION ALL
SELECT 
    '教师',
    UserName,
    Classes
FROM teacher
WHERE Classes IS NOT NULL AND Classes != ''
LIMIT 5;
```

## 测试6: 数据一致性验证
```sql
-- 验证外键数据一致性
SELECT 
    '教师-学校关联' AS '检查项',
    COUNT(*) AS '总数',
    SUM(CASE WHEN school_id IS NULL THEN 1 ELSE 0 END) AS 'NULL数',
    SUM(CASE WHEN school_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM schools WHERE id = teacher.school_id
    ) THEN 1 ELSE 0 END) AS '无效关联'
FROM teacher
UNION ALL
SELECT 
    '学生-学校关联',
    COUNT(*),
    SUM(CASE WHEN school_id IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN school_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM schools WHERE id = students.school_id
    ) THEN 1 ELSE 0 END)
FROM students
UNION ALL
SELECT 
    '学生-班级关联',
    COUNT(*),
    SUM(CASE WHEN class_id IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN class_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM classes WHERE id = students.class_id
    ) THEN 1 ELSE 0 END)
FROM students
UNION ALL
SELECT 
    '班级-学校关联',
    COUNT(*),
    SUM(CASE WHEN school_id IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN school_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM schools WHERE id = classes.school_id
    ) THEN 1 ELSE 0 END)
FROM classes;
```

## 测试7: 索引检查
```sql
-- 检查新建的索引
SELECT 
    TABLE_NAME AS '表名',
    INDEX_NAME AS '索引名',
    COLUMN_NAME AS '列名',
    NON_UNIQUE AS '非唯一',
    SEQ_IN_INDEX AS '序号'
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'onlinejudgesystem'
AND TABLE_NAME IN ('schools', 'classes', 'teacher', 'students')
AND INDEX_NAME != 'PRIMARY'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
```
