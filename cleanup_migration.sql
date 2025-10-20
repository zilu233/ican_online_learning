-- 清理脚本：删除新增的表和外键约束
USE onlinejudgesystem;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. 删除classes表
DROP TABLE IF EXISTS `classes`;

-- 2. 删除schools表
DROP TABLE IF EXISTS `schools`;

SET FOREIGN_KEY_CHECKS = 1;

-- 3. 移除teacher表的新增字段（如果存在）
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
     AND TABLE_NAME = 'teacher' 
     AND COLUMN_NAME = 'school_id') > 0,
    'ALTER TABLE teacher DROP COLUMN school_id',
    'SELECT "school_id不存在" AS Result'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
     AND TABLE_NAME = 'teacher' 
     AND COLUMN_NAME = 'approval_status') > 0,
    'ALTER TABLE teacher DROP COLUMN approval_status, DROP COLUMN approval_time, DROP COLUMN approval_admin_id, DROP COLUMN rejection_reason, DROP COLUMN created_at, DROP COLUMN updated_at',
    'SELECT "审核字段不存在" AS Result'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. 移除students表的新增字段（如果存在）
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
     AND TABLE_NAME = 'students' 
     AND COLUMN_NAME = 'school_id') > 0,
    'ALTER TABLE students DROP COLUMN school_id',
    'SELECT "school_id不存在" AS Result'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'onlinejudgesystem' 
     AND TABLE_NAME = 'students' 
     AND COLUMN_NAME = 'class_id') > 0,
    'ALTER TABLE students DROP COLUMN class_id, DROP COLUMN enrollment_date, DROP COLUMN status, DROP COLUMN created_at, DROP COLUMN updated_at',
    'SELECT "班级字段不存在" AS Result'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '✓ 清理完成！' AS 'Status';
