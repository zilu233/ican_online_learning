-- ============================================
-- 简化迁移脚本：只创建表和插入数据
-- （字段已存在，无需ALTER TABLE）
-- ============================================

USE onlinejudgesystem;

-- ============================================
-- 第一部分：创建schools表
-- ============================================

CREATE TABLE IF NOT EXISTS `schools` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `school_name` VARCHAR(100) NOT NULL COMMENT '学校名称',
  `school_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '学校代码',
  `province` VARCHAR(50) DEFAULT NULL COMMENT '省份',
  `city` VARCHAR(50) DEFAULT NULL COMMENT '城市',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
  `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '联系人',
  `contact_phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态:1-启用,0-禁用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_school_code` (`school_code`),
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='学校信息表';

-- ============================================
-- 第二部分：创建classes表
-- ============================================

CREATE TABLE IF NOT EXISTS `classes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `school_id` INT(11) NOT NULL COMMENT '学校ID',
  `class_name` VARCHAR(100) NOT NULL COMMENT '班级名称',
  `class_code` VARCHAR(50) DEFAULT NULL COMMENT '班级代码',
  `grade` VARCHAR(50) DEFAULT NULL COMMENT '年级',
  `teacher_id` INT(11) DEFAULT NULL COMMENT '班主任ID',
  `student_count` INT(11) DEFAULT 0 COMMENT '学生人数',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '班级描述',
  `status` TINYINT(1) DEFAULT 1 COMMENT '状态:1-启用,0-禁用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_school_id` (`school_id`),
  INDEX `idx_teacher_id` (`teacher_id`),
  INDEX `idx_status` (`status`),
  FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='班级信息表';

-- ============================================
-- 第三部分：添加外键约束（如果不存在）
-- ============================================

-- 给teacher表添加外键（可能已存在）
SET @FK_EXISTS = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = 'onlinejudgesystem' 
    AND TABLE_NAME = 'teacher' 
    AND CONSTRAINT_NAME = 'teacher_ibfk_1');

SET @sql = IF(@FK_EXISTS = 0, 
    'ALTER TABLE teacher ADD FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL', 
    'SELECT "外键已存在" AS Result');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 给students表添加外键（可能已存在）
SET @FK_EXISTS = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = 'onlinejudgesystem' 
    AND TABLE_NAME = 'students' 
    AND CONSTRAINT_NAME = 'students_ibfk_1');

SET @sql = IF(@FK_EXISTS = 0, 
    'ALTER TABLE students ADD FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL', 
    'SELECT "外键已存在" AS Result');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @FK_EXISTS = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = 'onlinejudgesystem' 
    AND TABLE_NAME = 'students' 
    AND CONSTRAINT_NAME = 'students_ibfk_2');

SET @sql = IF(@FK_EXISTS = 0, 
    'ALTER TABLE students ADD FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL', 
    'SELECT "外键已存在" AS Result');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================
-- 第四部分：插入学校数据
-- ============================================

INSERT IGNORE INTO `schools` (`school_name`, `school_code`, `province`, `city`, `address`, `status`) 
VALUES 
('默认学校', 'DEFAULT', '默认省份', '默认城市', '默认地址', 1),
('北京第一中学', 'BJ001', '北京市', '朝阳区', '朝阳路100号', 1),
('上海实验中学', 'SH001', '上海市', '浦东新区', '世纪大道200号', 1),
('广州外国语学校', 'GZ001', '广东省', '广州市', '天河路300号', 1);

-- ============================================
-- 第五部分：更新现有数据
-- ============================================

-- 获取默认学校ID
SET @default_school_id = (SELECT id FROM schools WHERE school_code = 'DEFAULT' LIMIT 1);

-- 更新现有教师的学校ID和审核状态（如果为NULL）
UPDATE teacher 
SET school_id = @default_school_id, 
    approval_status = 1,
    approval_time = NOW()
WHERE school_id IS NULL;

-- 更新现有学生的学校ID（如果为NULL）
UPDATE students 
SET school_id = @default_school_id
WHERE school_id IS NULL;

-- 为默认学校创建班级（基于现有学生的Classes字段）
INSERT IGNORE INTO classes (school_id, class_name, grade, status)
SELECT DISTINCT 
    @default_school_id,
    Classes,
    CASE 
        WHEN Classes LIKE '%1%' THEN '一年级'
        WHEN Classes LIKE '%2%' THEN '二年级'
        WHEN Classes LIKE '%3%' THEN '三年级'
        ELSE '其他'
    END,
    1
FROM students
WHERE Classes IS NOT NULL AND Classes != '' AND school_id = @default_school_id
ORDER BY Classes;

-- 更新学生的class_id（基于班级名称匹配）
UPDATE students s
INNER JOIN classes c ON c.school_id = s.school_id AND c.class_name = s.Classes
SET s.class_id = c.id
WHERE s.Classes IS NOT NULL AND s.Classes != '' AND s.class_id IS NULL;

-- 更新班级的学生人数
UPDATE classes c
SET c.student_count = (
    SELECT COUNT(*) 
    FROM students s 
    WHERE s.class_id = c.id
);

-- ============================================
-- 第六部分：插入测试数据
-- ============================================

-- 为北京第一中学创建班级
SET @bj_school_id = (SELECT id FROM schools WHERE school_code = 'BJ001' LIMIT 1);
INSERT IGNORE INTO classes (school_id, class_name, class_code, grade, status) 
VALUES 
(@bj_school_id, '高一(1)班', 'BJ001-G1-1', '高一', 1),
(@bj_school_id, '高一(2)班', 'BJ001-G1-2', '高一', 1),
(@bj_school_id, '高二(1)班', 'BJ001-G2-1', '高二', 1);

-- 为上海实验中学创建班级
SET @sh_school_id = (SELECT id FROM schools WHERE school_code = 'SH001' LIMIT 1);
INSERT IGNORE INTO classes (school_id, class_name, class_code, grade, status) 
VALUES 
(@sh_school_id, '初一(1)班', 'SH001-J1-1', '初一', 1),
(@sh_school_id, '初一(2)班', 'SH001-J1-2', '初一', 1);

-- ============================================
-- 验证查询
-- ============================================

SELECT '✓ 迁移完成！' AS 'Status';

SELECT 
    (SELECT COUNT(*) FROM schools) AS '学校数量',
    (SELECT COUNT(*) FROM classes) AS '班级数量',
    (SELECT COUNT(*) FROM teacher) AS '教师数量',
    (SELECT COUNT(*) FROM students) AS '学生数量',
    (SELECT COUNT(*) FROM teacher WHERE approval_status = 0) AS '待审核教师';
