# -*- coding: utf-8 -*-
"""
多学校系统数据库迁移测试脚本
测试迁移后的数据完整性和现有功能
"""

import sys
import os

# 添加OnlineJudgeSystem目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
onlinejudge_dir = os.path.join(current_dir, 'OnlineJudgeSystem')
sys.path.insert(0, onlinejudge_dir)

from common.MySqlHelper import MySqlHelper
from model.Students import Students, StudentsServer
from model.Teachers import Teachers, TeachersServer
from model.Schools import Schools, SchoolsServer
from model.Classes import Classes, ClassesServer

def print_section(title):
    """打印分隔标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_database_structure():
    """测试1: 数据库结构检查"""
    print_section("测试1: 数据库结构检查")
    
    helper = MySqlHelper()
    
    # 检查schools表
    print("\n[1.1] 检查schools表结构...")
    sql = "DESCRIBE schools"
    result = helper.query(sql)
    if result:
        print(f"✅ schools表存在，共{len(result)}个字段")
        for field in result:
            print(f"   - {field['Field']}: {field['Type']}")
    else:
        print("❌ schools表不存在或无法访问")
        return False
    
    # 检查classes表
    print("\n[1.2] 检查classes表结构...")
    sql = "DESCRIBE classes"
    result = helper.query(sql)
    if result:
        print(f"✅ classes表存在，共{len(result)}个字段")
        for field in result:
            print(f"   - {field['Field']}: {field['Type']}")
    else:
        print("❌ classes表不存在或无法访问")
        return False
    
    # 检查teacher表扩展字段
    print("\n[1.3] 检查teacher表扩展字段...")
    sql = "DESCRIBE teacher"
    result = helper.query(sql)
    new_fields = ['school_id', 'approval_status', 'approval_time', 'approval_admin_id', 'rejection_reason']
    found_fields = [field['Field'] for field in result]
    
    for field in new_fields:
        if field in found_fields:
            print(f"   ✅ {field} 字段存在")
        else:
            print(f"   ❌ {field} 字段不存在")
    
    # 检查students表扩展字段
    print("\n[1.4] 检查students表扩展字段...")
    sql = "DESCRIBE students"
    result = helper.query(sql)
    new_fields = ['school_id', 'class_id', 'enrollment_date', 'status']
    found_fields = [field['Field'] for field in result]
    
    for field in new_fields:
        if field in found_fields:
            print(f"   ✅ {field} 字段存在")
        else:
            print(f"   ❌ {field} 字段不存在")
    
    return True

def test_foreign_keys():
    """测试2: 外键约束检查"""
    print_section("测试2: 外键约束检查")
    
    helper = MySqlHelper()
    
    # 检查classes表外键
    print("\n[2.1] 检查classes表外键...")
    sql = """
    SELECT 
        CONSTRAINT_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'onlinejudgesystem'
    AND TABLE_NAME = 'classes'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    """
    result = helper.query(sql)
    if result:
        for fk in result:
            print(f"   ✅ {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
    else:
        print("   ⚠️ 未找到外键约束")
    
    # 检查teacher表外键
    print("\n[2.2] 检查teacher表外键...")
    sql = """
    SELECT 
        CONSTRAINT_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'onlinejudgesystem'
    AND TABLE_NAME = 'teacher'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    """
    result = helper.query(sql)
    if result:
        for fk in result:
            print(f"   ✅ {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
    else:
        print("   ⚠️ 未找到外键约束")
    
    # 检查students表外键
    print("\n[2.3] 检查students表外键...")
    sql = """
    SELECT 
        CONSTRAINT_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'onlinejudgesystem'
    AND TABLE_NAME = 'students'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    """
    result = helper.query(sql)
    if result:
        for fk in result:
            print(f"   ✅ {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
    else:
        print("   ⚠️ 未找到外键约束")

def test_data_integrity():
    """测试3: 数据完整性检查"""
    print_section("测试3: 数据完整性检查")
    
    helper = MySqlHelper()
    
    # 检查学校数据
    print("\n[3.1] 检查学校数据...")
    sql = "SELECT id, school_name, school_code, status FROM schools ORDER BY id"
    schools = helper.query(sql)
    print(f"   学校总数: {len(schools)}")
    for school in schools:
        status = "启用" if school['status'] == 1 else "禁用"
        print(f"   - [{school['school_code']}] {school['school_name']} ({status})")
    
    # 检查班级数据
    print("\n[3.2] 检查班级数据...")
    sql = """
    SELECT c.id, c.class_name, c.class_code, s.school_name, c.grade, c.status
    FROM classes c
    LEFT JOIN schools s ON c.school_id = s.id
    ORDER BY s.school_name, c.grade, c.class_name
    """
    classes = helper.query(sql)
    print(f"   班级总数: {len(classes)}")
    current_school = None
    for cls in classes:
        if current_school != cls['school_name']:
            current_school = cls['school_name']
            print(f"\n   【{current_school}】")
        status = "启用" if cls['status'] == 1 else "禁用"
        print(f"   - [{cls['class_code']}] {cls['class_name']} (年级:{cls['grade']}, {status})")
    
    # 检查教师数据
    print("\n[3.3] 检查教师数据...")
    sql = """
    SELECT t.Id, t.UserName, t.RealName, s.school_name, t.approval_status
    FROM teacher t
    LEFT JOIN schools s ON t.school_id = s.id
    ORDER BY s.school_name, t.RealName
    """
    teachers = helper.query(sql)
    print(f"   教师总数: {len(teachers)}")
    for teacher in teachers:
        status_map = {0: "待审核", 1: "已通过", 2: "已拒绝"}
        status = status_map.get(teacher['approval_status'], "未知")
        school = teacher['school_name'] if teacher['school_name'] else "未分配"
        print(f"   - {teacher['RealName']} (@{teacher['UserName']}) - {school} [{status}]")
    
    # 检查学生数据
    print("\n[3.4] 检查学生数据...")
    sql = """
    SELECT s.Id, s.UserName, s.RealName, sch.school_name, c.class_name, s.status
    FROM students s
    LEFT JOIN schools sch ON s.school_id = sch.id
    LEFT JOIN classes c ON s.class_id = c.id
    ORDER BY sch.school_name, c.class_name, s.RealName
    """
    students = helper.query(sql)
    print(f"   学生总数: {len(students)}")
    for student in students:
        school = student['school_name'] if student['school_name'] else "未分配"
        cls = student['class_name'] if student['class_name'] else "未分配班级"
        status = "正常" if student['status'] == 1 else "禁用"
        print(f"   - {student['RealName']} (@{student['UserName']}) - {school} / {cls} [{status}]")

def test_teacher_login():
    """测试4: 教师登录功能"""
    print_section("测试4: 教师登录功能测试")
    
    helper = MySqlHelper()
    
    # 获取所有教师账号
    sql = "SELECT UserName, Password, approval_status FROM teacher"
    teachers = helper.query(sql)
    
    print(f"\n[4.1] 测试教师登录...")
    print(f"   共有 {len(teachers)} 位教师")
    
    for teacher in teachers:
        username = teacher['UserName']
        password = teacher['Password']
        approval_status = teacher['approval_status']
        
        # 测试登录
        teacher_obj = TeachersServer().select_sql_login(username, password)
        
        if approval_status == 1:
            # 已审核通过的教师应该能登录
            if teacher_obj and teacher_obj.UserName:
                print(f"   ✅ {username}: 登录成功 (已审核)")
                if hasattr(teacher_obj, 'SchoolName') and teacher_obj.SchoolName:
                    print(f"      学校: {teacher_obj.SchoolName}")
            else:
                print(f"   ❌ {username}: 登录失败 (应该能登录)")
        else:
            # 未审核的教师应该无法登录
            if teacher_obj and teacher_obj.UserName:
                print(f"   ⚠️ {username}: 登录成功 (但未审核，不应能登录)")
            else:
                print(f"   ✅ {username}: 正确拒绝登录 (待审核)")

def test_student_login():
    """测试5: 学生登录功能"""
    print_section("测试5: 学生登录功能测试")
    
    helper = MySqlHelper()
    
    # 获取所有学生账号
    sql = "SELECT UserName, Password, status FROM students"
    students = helper.query(sql)
    
    print(f"\n[5.1] 测试学生登录...")
    print(f"   共有 {len(students)} 位学生")
    
    for student in students:
        username = student['UserName']
        password = student['Password']
        status = student['status']
        
        # 测试登录
        student_obj = StudentsServer().select_sql_login(username, password)
        
        if status == 1 or status is None:
            # 正常状态的学生应该能登录
            if student_obj and student_obj.UserName:
                print(f"   ✅ {username}: 登录成功")
                if hasattr(student_obj, 'SchoolName') and student_obj.SchoolName:
                    print(f"      学校: {student_obj.SchoolName}")
                if hasattr(student_obj, 'ClassName') and student_obj.ClassName:
                    print(f"      班级: {student_obj.ClassName}")
            else:
                print(f"   ❌ {username}: 登录失败 (应该能登录)")
        else:
            # 禁用的学生应该无法登录
            if student_obj and student_obj.UserName:
                print(f"   ⚠️ {username}: 登录成功 (但已禁用，不应能登录)")
            else:
                print(f"   ✅ {username}: 正确拒绝登录 (已禁用)")

def test_model_methods():
    """测试6: 模型方法测试"""
    print_section("测试6: 新增模型方法测试")
    
    # 测试Schools模型
    print("\n[6.1] 测试Schools模型...")
    try:
        schools = SchoolsServer().select_sql_all()
        print(f"   ✅ select_sql_all(): 返回 {len(schools)} 所学校")
        
        if schools:
            stats = SchoolsServer().get_statistics(schools[0].Id)
            if stats:
                print(f"   ✅ get_statistics(): 成功获取统计数据")
                print(f"      教师数: {stats.get('teacher_count', 0)}")
                print(f"      学生数: {stats.get('student_count', 0)}")
                print(f"      班级数: {stats.get('class_count', 0)}")
    except Exception as e:
        print(f"   ❌ Schools模型测试失败: {str(e)}")
    
    # 测试Classes模型
    print("\n[6.2] 测试Classes模型...")
    try:
        helper = MySqlHelper()
        sql = "SELECT id FROM schools LIMIT 1"
        school = helper.query(sql)
        
        if school:
            school_id = school[0]['id']
            classes = ClassesServer().select_sql_by_school(school_id)
            print(f"   ✅ select_sql_by_school(): 返回 {len(classes)} 个班级")
    except Exception as e:
        print(f"   ❌ Classes模型测试失败: {str(e)}")
    
    # 测试Students扩展方法
    print("\n[6.3] 测试Students扩展方法...")
    try:
        helper = MySqlHelper()
        sql = "SELECT id FROM schools WHERE school_code='DEFAULT' LIMIT 1"
        school = helper.query(sql)
        
        if school:
            school_id = school[0]['id']
            students = StudentsServer().select_sql_by_school(school_id)
            print(f"   ✅ select_sql_by_school(): 返回 {len(students)} 位学生")
    except Exception as e:
        print(f"   ❌ Students扩展方法测试失败: {str(e)}")
    
    # 测试Teachers扩展方法
    print("\n[6.4] 测试Teachers扩展方法...")
    try:
        pending = TeachersServer().select_sql_pending_approval()
        print(f"   ✅ select_sql_pending_approval(): 返回 {len(pending)} 位待审核教师")
        
        helper = MySqlHelper()
        sql = "SELECT id FROM schools WHERE school_code='DEFAULT' LIMIT 1"
        school = helper.query(sql)
        
        if school:
            school_id = school[0]['id']
            teachers = TeachersServer().select_sql_by_school(school_id)
            print(f"   ✅ select_sql_by_school(): 返回 {len(teachers)} 位教师")
    except Exception as e:
        print(f"   ❌ Teachers扩展方法测试失败: {str(e)}")

def test_backward_compatibility():
    """测试7: 向后兼容性测试"""
    print_section("测试7: 向后兼容性测试")
    
    helper = MySqlHelper()
    
    # 检查旧字段是否保留
    print("\n[7.1] 检查students表旧字段...")
    sql = "DESCRIBE students"
    result = helper.query(sql)
    fields = [field['Field'] for field in result]
    
    if 'Classes' in fields:
        print("   ✅ students.Classes 字段保留")
    else:
        print("   ⚠️ students.Classes 字段不存在")
    
    print("\n[7.2] 检查teacher表旧字段...")
    sql = "DESCRIBE teacher"
    result = helper.query(sql)
    fields = [field['Field'] for field in result]
    
    if 'Classes' in fields:
        print("   ✅ teacher.Classes 字段保留")
    else:
        print("   ⚠️ teacher.Classes 字段不存在")
    
    # 测试旧字段数据
    print("\n[7.3] 测试旧字段数据...")
    sql = "SELECT UserName, Classes FROM students WHERE Classes IS NOT NULL AND Classes != '' LIMIT 3"
    students = helper.query(sql)
    if students:
        print(f"   ✅ 找到 {len(students)} 位学生有旧Classes数据")
        for student in students:
            print(f"      - {student['UserName']}: {student['Classes']}")
    else:
        print("   ℹ️ 没有学生有旧Classes数据")

def generate_report():
    """生成测试报告"""
    print_section("测试完成")
    
    print("\n" + "="*60)
    print("  测试总结")
    print("="*60)
    print("""
本次测试涵盖以下方面:
✓ 数据库表结构完整性
✓ 外键约束配置
✓ 数据迁移完整性
✓ 教师登录功能（含审核机制）
✓ 学生登录功能
✓ 新增模型方法
✓ 向后兼容性

如果所有测试都通过，说明迁移成功且不影响现有功能。
如果有测试失败，请查看上面的详细日志进行排查。

下一步建议:
1. 如果测试通过: 创建schoolviews.py API接口
2. 如果有问题: 根据错误信息修复问题
""")

def main():
    """主测试函数"""
    print("="*60)
    print("  多学校系统数据库迁移测试")
    print("  日期: 2025年10月18日")
    print("="*60)
    
    try:
        # 执行所有测试
        test_database_structure()
        test_foreign_keys()
        test_data_integrity()
        test_teacher_login()
        test_student_login()
        test_model_methods()
        test_backward_compatibility()
        
        # 生成报告
        generate_report()
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
