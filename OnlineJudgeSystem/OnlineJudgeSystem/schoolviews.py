# -*- coding: utf-8 -*-
"""
多学校班级管理系统 - API视图层
包含学校管理、班级管理、教师审核的API接口
注意：本文件位于内层 Flask 包 OnlineJudgeSystem 下，便于 __init__.py 直接导入。
"""

from flask import request, jsonify, session, render_template
from OnlineJudgeSystem import app
from OnlineJudgeSystem.model.Schools import Schools, SchoolsServer
from OnlineJudgeSystem.model.Classes import Classes, ClassesServer
from OnlineJudgeSystem.model.Teachers import TeachersServer
from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
from OnlineJudgeSystem.model.Students import StudentsServer


def _is_admin_logged_in() -> bool:
    """Return True when current session belongs to an authenticated admin."""
    if session.get('logged_type') == 'admin':
        return True
    return 'adminuser' in session


def _sync_teacher_assignments(teacher_id: int):
    """Recalculate teacher's班级列表并写回教师表。"""
    if not teacher_id:
        return
    classes = ClassesServer.select_sql_by_teacher(int(teacher_id))
    class_names = ",".join([c.ClassName for c in classes])
    school_id = classes[0].SchoolId if classes else None
    TeachersServer().update_classes_and_school(int(teacher_id), class_names, school_id)


def _resolve_school_id_by_name(name: str) -> int:
    """Try to resolve a school id by its name (trimmed, case-insensitive) among active schools."""
    if not name:
        return 0
    key = str(name).strip().lower()
    try:
        schools = SchoolsServer.select_sql_all(status=1)
        for s in schools:
            if str(getattr(s, 'SchoolName', '')).strip().lower() == key:
                return int(s.Id)
    except Exception:
        pass
    return 0


# ============ 学校管理 ============

@app.route('/admin/schools')
def admin_schools():
    """学校列表页面"""
    if not _is_admin_logged_in():
        return render_template('login.html')
    return render_template('admin/schools.html')


@app.route('/api/schools/list', methods=['GET'])
def api_schools_list():
    """获取学校列表API"""
    if not _is_admin_logged_in():
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
            'created_at': str(school.CreatedAt) if school.CreatedAt else '',
            'teacher_count': stats['teacher_count'],
            'student_count': stats['student_count'],
            'class_count': stats['class_count'],
            'pending_teacher_count': stats['pending_teacher_count']
        })

    return jsonify({'code': 1, 'data': result})


@app.route('/api/schools/add', methods=['POST'])
def api_schools_add():
    """添加学校API"""
    if not _is_admin_logged_in():
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
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    data = request.get_json()

    # 检查学校代码是否被其他学校使用
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
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    data = request.get_json()
    school_id = data['id']
    status = data['status']

    SchoolsServer.update_status(school_id, status)

    return jsonify({'code': 1, 'msg': '操作成功'})


@app.route('/api/schools/detail/<int:school_id>', methods=['GET'])
def api_schools_detail(school_id):
    """获取学校详情API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    school = SchoolsServer.select_sql_by_id(school_id)
    if not school:
        return jsonify({'code': 0, 'msg': '学校不存在'})

    stats = SchoolsServer.get_statistics(school_id)

    result = {
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
        'created_at': str(school.CreatedAt) if school.CreatedAt else '',
        'teacher_count': stats['teacher_count'],
        'student_count': stats['student_count'],
        'class_count': stats['class_count'],
        'pending_teacher_count': stats['pending_teacher_count']
    }

    return jsonify({'code': 1, 'data': result})


# ============ 班级管理 ============

@app.route('/admin/classes')
def admin_classes():
    """班级列表页面"""
    if not _is_admin_logged_in():
        return render_template('login.html')
    return render_template('admin/classes.html')


@app.route('/admin/teachers')
def admin_teachers():
    """教师管理页面（显示教师姓名与所属班级）"""
    if not _is_admin_logged_in():
        return render_template('login.html')
    return render_template('admin/teachers.html')


# ============ 教师管理（编辑 / 删除）============
@app.route('/api/teachers/<int:teacher_id>', methods=['PUT'])
def api_teacher_update(teacher_id: int):
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})
    try:
        data = request.get_json(force=True, silent=True) or {}
        server = TeachersServer()
        teacher = server.select_sql_by_id(teacher_id)
        if not getattr(teacher, 'Id', 0):
            return jsonify({'code': 0, 'msg': '教师不存在'})

        # 允许修改的字段：Name, Card, Phone, Address
        teacher.Name = (data.get('name') or teacher.Name or '').strip()
        teacher.Card = (data.get('card') or teacher.Card or '').strip()
        teacher.Phone = (data.get('phone') or teacher.Phone or '').strip()
        teacher.Address = (data.get('address') or teacher.Address or '').strip()
        # 可选：classes（若前端未提供则保持不变）
        if 'classes' in data:
            teacher.Classes = (data.get('classes') or teacher.Classes or '').strip()

        server.update_sql(teacher)
        return jsonify({'code': 1, 'msg': '更新成功'})
    except Exception as e:
        return jsonify({'code': 0, 'msg': f'更新失败: {e}'})


@app.route('/api/teachers/<int:teacher_id>', methods=['DELETE'])
def api_teacher_delete(teacher_id: int):
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})
    try:
        # 先解除该教师与所有班级的绑定
        helper = MySqlHelper()
        helper.query(f"UPDATE classes SET teacher_id = NULL WHERE teacher_id = {int(teacher_id)}", "")
        helper.connent.commit()
        helper.end()

        # 删除教师记录
        TeachersServer().delete_sql(teacher_id)
        return jsonify({'code': 1, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'code': 0, 'msg': f'删除失败: {e}'})


@app.route('/api/classes/list', methods=['GET'])
def api_classes_list():
    """获取班级列表API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    school_id = request.args.get('school_id', None)
    if school_id:
        school_id = int(school_id)
    status = request.args.get('status', None)
    if status in (None, ""):
        status = None
    else:
        status = int(status)

    classes = ClassesServer.select_sql_all(school_id=school_id, status=status)

    result = []
    for cls in classes:
        result.append({
            'id': cls.Id,
            'school_id': cls.SchoolId,
            'school_name': getattr(cls, 'SchoolName', ''),
            'class_name': cls.ClassName,
            'class_code': cls.ClassCode,
            'grade': cls.Grade,
            'teacher_id': cls.TeacherId,
            'teacher_name': getattr(cls, 'TeacherName', ''),
            'student_count': cls.StudentCount,
            'description': cls.Description,
            'status': cls.Status
        })

    return jsonify({'code': 1, 'data': result})


@app.route('/api/classes/add', methods=['POST'])
def api_classes_add():
    """添加班级API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    data = request.get_json()
    # 支持按学校名称手输：若提供名称，则优先按名称解析并覆盖传入的 school_id
    school_id = int(data.get('school_id') or 0)
    name_from_client = (data.get('school_name') or '').strip()
    if name_from_client:
        resolved = _resolve_school_id_by_name(name_from_client)
        if resolved:
            school_id = resolved
    # 如果前端不再提供学校字段，则选择一个默认学校（第一个启用的学校）
    if not school_id:
        schools = SchoolsServer.select_sql_all(status=1)
        if schools:
            school_id = int(schools[0].Id)
    if not school_id:
        return jsonify({'code': 0, 'msg': '未找到可用学校，请先在“学校管理”添加并启用学校'})

    # 检查班级名称在该学校是否已存在
    if ClassesServer.check_name_exists(school_id, data['class_name']):
        return jsonify({'code': 0, 'msg': '该学校已存在同名班级'})

    cls = Classes()
    cls.SchoolId = school_id
    cls.ClassName = data['class_name']
    cls.ClassCode = data.get('class_code', '')
    cls.Grade = data.get('grade', '')
    cls.TeacherId = data.get('teacher_id', 0)
    cls.Description = data.get('description', '')
    cls.Status = 1

    class_id = ClassesServer.insert_sql(cls)

    if cls.TeacherId:
        _sync_teacher_assignments(cls.TeacherId)

    return jsonify({'code': 1, 'msg': '添加成功', 'class_id': class_id})


@app.route('/api/classes/update', methods=['POST'])
def api_classes_update():
    """更新班级API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    data = request.get_json()
    # 支持按学校名称手输：若提供名称，则优先按名称解析并覆盖传入的 school_id
    school_id = int(data.get('school_id') or 0)
    name_from_client = (data.get('school_name') or '').strip()
    existing = ClassesServer.select_sql_by_id(data['id'])
    if name_from_client:
        resolved = _resolve_school_id_by_name(name_from_client)
        if resolved:
            school_id = resolved
    # 如果未提供学校且未解析到，则沿用原班级所属学校
    if not school_id and existing:
        school_id = int(getattr(existing, 'SchoolId', 0) or 0)
    # 若仍为空，尝试选一个默认学校（启用列表第一个）
    if not school_id:
        schools = SchoolsServer.select_sql_all(status=1)
        if schools:
            school_id = int(schools[0].Id)
    if not school_id:
        return jsonify({'code': 0, 'msg': '未找到可用学校'})

    # 检查班级名称
    if ClassesServer.check_name_exists(school_id, data['class_name'], exclude_id=data['id']):
        return jsonify({'code': 0, 'msg': '该学校已存在同名班级'})

    cls = Classes()
    cls.Id = data['id']
    cls.SchoolId = school_id
    cls.ClassName = data['class_name']
    cls.ClassCode = data.get('class_code', '')
    cls.Grade = data.get('grade', '')
    cls.TeacherId = data.get('teacher_id', 0)
    cls.Description = data.get('description', '')
    cls.Status = data.get('status', 1)

    ClassesServer.update_sql(cls)

    old_teacher = existing.TeacherId if existing else None
    if old_teacher and old_teacher != cls.TeacherId:
        _sync_teacher_assignments(old_teacher)
    if cls.TeacherId:
        _sync_teacher_assignments(cls.TeacherId)

    return jsonify({'code': 1, 'msg': '更新成功'})


@app.route('/api/classes/delete', methods=['POST'])
def api_classes_delete():
    """删除班级API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    data = request.get_json() or {}
    try:
        class_id = int(data.get('id', 0))
    except (TypeError, ValueError):
        class_id = 0

    if not class_id:
        return jsonify({'code': 0, 'msg': '参数错误'})

    existing = ClassesServer.select_sql_by_id(class_id)
    if not existing:
        return jsonify({'code': 0, 'msg': '班级不存在'})

    students = StudentsServer().select_sql_by_class(class_id)
    if students:
        return jsonify({'code': 0, 'msg': '班级下仍有学生，无法删除'})

    ClassesServer.delete_sql(class_id)

    if getattr(existing, 'TeacherId', 0):
        _sync_teacher_assignments(existing.TeacherId)

    return jsonify({'code': 1, 'msg': '删除成功'})


@app.route('/api/classes/detail/<int:class_id>', methods=['GET'])
def api_classes_detail(class_id):
    """获取班级详情API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    cls = ClassesServer.select_sql_by_id(class_id)
    if not cls:
        return jsonify({'code': 0, 'msg': '班级不存在'})

    result = {
        'id': cls.Id,
        'school_id': cls.SchoolId,
        'school_name': getattr(cls, 'SchoolName', ''),
        'class_name': cls.ClassName,
        'class_code': cls.ClassCode,
        'grade': cls.Grade,
        'teacher_id': cls.TeacherId,
        'teacher_name': getattr(cls, 'TeacherName', ''),
        'student_count': cls.StudentCount,
        'description': cls.Description,
        'status': cls.Status
    }

    return jsonify({'code': 1, 'data': result})


@app.route('/api/classes/by_school/<int:school_id>', methods=['GET'])
def api_classes_by_school(school_id):
    """根据学校获取班级列表API（用于下拉框）"""
    classes = ClassesServer.select_sql_by_school(school_id, status=1)

    result = []
    for cls in classes:
        result.append({
            'id': cls.Id,
            'class_name': cls.ClassName,
            'class_code': cls.ClassCode,
            'grade': cls.Grade
        })

    return jsonify({'code': 1, 'data': result})


@app.route('/api/classes/students/<int:class_id>', methods=['GET'])
def api_classes_students(class_id):
    """获取班级学生列表API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    # 使用已有 StudentsServer 接口，返回学生对象列表
    students = StudentsServer().select_sql_by_class(class_id)

    result = []
    for student in students:
        result.append({
            'id': student.Id,
            'username': student.UserName,
            'name': student.Name,
            'card': student.Card,
            'phone': student.Phone,
            'status': getattr(student, 'Status', 1)
        })

    return jsonify({'code': 1, 'data': result})


# ============ 教师审核 ============

@app.route('/admin/teacher_approval')
def admin_teacher_approval():
    """教师审核页面（已关闭）"""
    return render_template('404.html') if False else jsonify({'code': 0, 'msg': '教师审核功能已关闭'}), 404


@app.route('/api/teachers/pending', methods=['GET'])
def api_teachers_pending():
    """已关闭"""
    return jsonify({'code': 0, 'msg': '教师审核功能已关闭'}), 404


@app.route('/api/teachers/approve', methods=['POST'])
def api_teachers_approve():
    """已关闭"""
    return jsonify({'code': 0, 'msg': '教师审核功能已关闭'}), 404


@app.route('/api/teachers/by_school/<int:school_id>', methods=['GET'])
def api_teachers_by_school(school_id):
    """根据学校获取教师列表API（用于下拉框）"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})
    server = TeachersServer()
    teachers = server.select_sql_by_school(school_id, approval_status=1)

    result = []
    for teacher in teachers:
        result.append({
            'id': teacher.Id,
            'username': teacher.UserName,
            'name': teacher.Name
        })

    return jsonify({'code': 1, 'data': result})


@app.route('/api/teachers/all_approved', methods=['GET'])
def api_teachers_all_approved():
    """获取所有已审核通过的教师列表API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    school_id = request.args.get('school_id', None)
    server = TeachersServer()
    teachers = []
    if school_id:
        try:
            school_id_int = int(school_id)
            teachers = server.select_sql_by_school(school_id_int, approval_status=1)
        except Exception:
            # 如果解析失败，退化为全量
            teachers = server.select_all_approved(approval_status=1)
    else:
        # 未指定school_id，返回全量已审核教师
        teachers = server.select_all_approved(approval_status=1)

    result = []
    for teacher in teachers:
        result.append({
            'id': teacher.Id,
            'username': teacher.UserName,
            'name': teacher.Name,
            'classes': getattr(teacher, 'Classes', '') or '',
            'school_id': getattr(teacher, 'SchoolId', None),
            'school_name': getattr(teacher, 'SchoolName', ''),
            'card': teacher.Card,
            'phone': teacher.Phone,
            'address': teacher.Address
        })

    return jsonify({'code': 1, 'data': result})


# ============ 辅助API ============

@app.route('/api/schools/all_active', methods=['GET'])
def api_schools_all_active():
    """获取所有启用的学校列表API（用于下拉框）"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})
    schools = SchoolsServer.select_sql_all(status=1)

    result = []
    for school in schools:
        result.append({
            'id': school.Id,
            'school_name': school.SchoolName,
            'school_code': school.SchoolCode
        })

    return jsonify({'code': 1, 'data': result})


@app.route('/api/statistics/overview', methods=['GET'])
def api_statistics_overview():
    """获取系统总体统计API"""
    if not _is_admin_logged_in():
        return jsonify({'code': 0, 'msg': '未登录'})

    from OnlineJudgeSystem.common.MySqlHelper import MySqlHelper
    helper = MySqlHelper()

    def scalar(sql: str) -> int:
        cnt = helper.query(sql, "")
        val = 0
        if cnt is not None:
            row = helper.cursor.fetchall()
            if row and len(row[0]) > 0:
                val = int(row[0][0])
        return val

    school_count = scalar("SELECT COUNT(*) FROM schools WHERE status = 1")
    class_count = scalar("SELECT COUNT(*) FROM classes WHERE status = 1")
    teacher_count = scalar("SELECT COUNT(*) FROM teacher WHERE approval_status = 1")
    student_count = scalar("SELECT COUNT(*) FROM students WHERE status = 1")
    pending_teacher_count = scalar("SELECT COUNT(*) FROM teacher WHERE approval_status = 0")

    helper.end()

    result = {
        'school_count': school_count,
        'class_count': class_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'pending_teacher_count': pending_teacher_count
    }

    return jsonify({'code': 1, 'data': result})
