-- ============================================
-- 多学校班级管理系统 - 数据库迁移脚本
-- 版本: 1.0
-- 日期: 2024
-- 说明: 添加学校和班级支持，实现多租户架构
-- ============================================

-- 使用数据库
USE onlinejudgesystem;

-- ============================================
-- 第一部分：创建新表
-- ============================================

-- 1. 创建学校信息表
DROP TABLE IF EXISTS `schools`;
CREATE TABLE `schools` (
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

-- 2. 创建班级信息表
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes` (
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
-- 第二部分：修改教师表
-- ============================================

-- 添加学校关联和审核状态
ALTER TABLE `teacher` 
ADD COLUMN `school_id` INT(11) DEFAULT NULL COMMENT '学校ID' AFTER `Id`,
ADD COLUMN `approval_status` TINYINT(1) DEFAULT 0 COMMENT '审核状态:0-待审核,1-已通过,2-已拒绝' AFTER `Address`,
ADD COLUMN `approval_time` DATETIME DEFAULT NULL COMMENT '审核时间' AFTER `approval_status`,
ADD COLUMN `approval_admin_id` INT(11) DEFAULT NULL COMMENT '审核管理员ID' AFTER `approval_time`,
ADD COLUMN `rejection_reason` VARCHAR(255) DEFAULT NULL COMMENT '拒绝原因' AFTER `approval_admin_id`,
ADD COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- 添加索引
ALTER TABLE `teacher`
ADD INDEX `idx_school_id` (`school_id`),
ADD INDEX `idx_approval_status` (`approval_status`),
ADD INDEX `idx_created_at` (`created_at`);

-- 添加外键约束（如果学校被删除，教师的school_id设为NULL）
ALTER TABLE `teacher`
ADD FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE SET NULL;

-- ============================================
-- 第三部分：修改学生表
-- ============================================

-- 添加学校和班级关联
ALTER TABLE `students` 
ADD COLUMN `school_id` INT(11) DEFAULT NULL COMMENT '学校ID' AFTER `Id`,
ADD COLUMN `class_id` INT(11) DEFAULT NULL COMMENT '班级ID' AFTER `school_id`,
ADD COLUMN `enrollment_date` DATE DEFAULT NULL COMMENT '入学日期' AFTER `class_id`,
ADD COLUMN `status` TINYINT(1) DEFAULT 1 COMMENT '状态:1-在读,0-毕业/退学' AFTER `enrollment_date`;

-- 修改Classes字段注释（保留向后兼容）
ALTER TABLE `students` 
CHANGE COLUMN `Classes` `Classes` VARCHAR(60) DEFAULT NULL COMMENT '班级名称(兼容旧数据)';

-- 添加时间字段
ALTER TABLE `students`
ADD COLUMN `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- 添加索引
ALTER TABLE `students`
ADD INDEX `idx_school_id` (`school_id`),
ADD INDEX `idx_class_id` (`class_id`),
ADD INDEX `idx_status` (`status`),
ADD INDEX `idx_created_at` (`created_at`);

-- 添加外键约束
ALTER TABLE `students`
ADD FOREIGN KEY (`school_id`) REFERENCES `schools`(`id`) ON DELETE SET NULL,
ADD FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE SET NULL;

-- ============================================
-- 第四部分：插入初始测试数据
-- ============================================

-- 插入默认学校（用于迁移现有数据）
INSERT INTO `schools` (`school_name`, `school_code`, `province`, `city`, `address`, `status`) 
VALUES 
('默认学校', 'DEFAULT', '默认省份', '默认城市', '默认地址', 1),
('北京第一中学', 'BJ001', '北京市', '朝阳区', '朝阳路100号', 1),
('上海实验中学', 'SH001', '上海市', '浦东新区', '世纪大道200号', 1),
('广州外国语学校', 'GZ001', '广东省', '广州市', '天河路300号', 1);

-- 获取默认学校ID（用于更新现有数据）
SET @default_school_id = (SELECT id FROM schools WHERE school_code = 'DEFAULT');

-- 更新现有教师的学校ID为默认学校，审核状态设为已通过
UPDATE `teacher` 
SET `school_id` = @default_school_id, 
    `approval_status` = 1,
    `approval_time` = NOW()
WHERE `school_id` IS NULL;

-- 更新现有学生的学校ID为默认学校
UPDATE `students` 
SET `school_id` = @default_school_id
WHERE `school_id` IS NULL;

-- 为默认学校创建班级（基于现有学生的Classes字段）
INSERT INTO `classes` (`school_id`, `class_name`, `grade`, `status`)
SELECT DISTINCT 
    @default_school_id,
    `Classes`,
    CASE 
        WHEN `Classes` LIKE '%1%' THEN '一年级'
        WHEN `Classes` LIKE '%2%' THEN '二年级'
        WHEN `Classes` LIKE '%3%' THEN '三年级'
        ELSE '其他'
    END,
    1
FROM `students`
WHERE `Classes` IS NOT NULL AND `Classes` != ''
ORDER BY `Classes`;

-- 更新学生的class_id（基于班级名称匹配）
UPDATE `students` s
INNER JOIN `classes` c ON c.school_id = s.school_id AND c.class_name = s.Classes
SET s.class_id = c.id
WHERE s.Classes IS NOT NULL AND s.Classes != '';

-- 更新班级的学生人数
UPDATE `classes` c
SET c.student_count = (
    SELECT COUNT(*) 
    FROM `students` s 
    WHERE s.class_id = c.id
);

-- ============================================
-- 第五部分：插入测试数据（可选）
-- ============================================

-- 为北京第一中学创建班级
SET @bj_school_id = (SELECT id FROM schools WHERE school_code = 'BJ001');
INSERT INTO `classes` (`school_id`, `class_name`, `class_code`, `grade`, `status`) 
VALUES 
(@bj_school_id, '高一(1)班', 'BJ001-G1-1', '高一', 1),
(@bj_school_id, '高一(2)班', 'BJ001-G1-2', '高一', 1),
(@bj_school_id, '高二(1)班', 'BJ001-G2-1', '高二', 1);

-- 为上海实验中学创建班级
SET @sh_school_id = (SELECT id FROM schools WHERE school_code = 'SH001');
INSERT INTO `classes` (`school_id`, `class_name`, `class_code`, `grade`, `status`) 
VALUES 
(@sh_school_id, '初一(1)班', 'SH001-J1-1', '初一', 1),
(@sh_school_id, '初一(2)班', 'SH001-J1-2', '初一', 1);

-- 创建测试教师（待审核）
INSERT INTO `teacher` (`school_id`, `User_Name`, `PWD`, `Classes`, `Name`, `Card`, `Phone`, `Address`, `approval_status`) 
VALUES 
(@bj_school_id, 'teacher_bj_001', '123456', '', '张老师', '110101199001011234', '13800138001', '北京市朝阳区', 0),
(@sh_school_id, 'teacher_sh_001', '123456', '', '李老师', '310101199002021234', '13800138002', '上海市浦东新区', 0);

-- 创建测试学生
SET @bj_class1_id = (SELECT id FROM classes WHERE school_id = @bj_school_id AND class_name = '高一(1)班' LIMIT 1);
INSERT INTO `students` (`school_id`, `class_id`, `User_Name`, `PWD`, `Classes`, `Name`, `Card`, `Phone`, `Address`, `status`) 
VALUES 
(@bj_school_id, @bj_class1_id, 'student_bj_001', '123456', '高一(1)班', '王同学', '110101200501011234', '13800138003', '北京市朝阳区', 1),
(@bj_school_id, @bj_class1_id, 'student_bj_002', '123456', '高一(1)班', '赵同学', '110101200502021234', '13800138004', '北京市朝阳区', 1);

-- ============================================
-- 第六部分：数据验证查询
-- ============================================

-- 查看学校统计
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
GROUP BY s.id, s.school_name
ORDER BY s.id;

-- 查看待审核教师
SELECT 
    t.Id,
    t.Name AS '教师姓名',
    s.school_name AS '所属学校',
    t.approval_status AS '审核状态',
    CASE t.approval_status
        WHEN 0 THEN '待审核'
        WHEN 1 THEN '已通过'
        WHEN 2 THEN '已拒绝'
    END AS '状态说明',
    t.created_at AS '注册时间'
FROM teacher t
LEFT JOIN schools s ON t.school_id = s.id
WHERE t.approval_status = 0
ORDER BY t.created_at DESC;

-- 查看班级学生分布
SELECT 
    s.school_name AS '学校名称',
    c.class_name AS '班级名称',
    c.student_count AS '学生人数',
    t.Name AS '班主任'
FROM classes c
INNER JOIN schools s ON c.school_id = s.id
LEFT JOIN teacher t ON c.teacher_id = t.Id
WHERE c.status = 1
ORDER BY s.school_name, c.class_name;

-- ============================================
-- 迁移完成！
-- ============================================

-- 显示迁移摘要
SELECT '数据库迁移完成！' AS '状态',
       (SELECT COUNT(*) FROM schools) AS '学校数量',
       (SELECT COUNT(*) FROM classes) AS '班级数量',
       (SELECT COUNT(*) FROM teacher) AS '教师数量',
       (SELECT COUNT(*) FROM students) AS '学生数量',
       (SELECT COUNT(*) FROM teacher WHERE approval_status = 0) AS '待审核教师';
