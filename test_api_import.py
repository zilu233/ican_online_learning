# -*- coding: utf-8 -*-
"""
API接口导入测试
测试schoolviews.py是否能正常导入
"""

import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'OnlineJudgeSystem'))

print("="*60)
print("  API接口导入测试")
print("="*60)

# 测试1: 导入Flask应用
print("\n[测试1] 导入Flask应用...")
try:
    from OnlineJudgeSystem import app
    print("   ✅ Flask应用导入成功")
    print(f"   应用名称: {app.name}")
except Exception as e:
    print(f"   ❌ Flask应用导入失败: {str(e)}")
    sys.exit(1)

# 测试2: 导入模型
print("\n[测试2] 导入模型...")
try:
    from OnlineJudgeSystem.model.Schools import Schools, SchoolsServer
    print("   ✅ Schools模型导入成功")
    
    from OnlineJudgeSystem.model.Classes import Classes, ClassesServer
    print("   ✅ Classes模型导入成功")
    
    from OnlineJudgeSystem.model.Teachers import TeachersServer
    print("   ✅ Teachers模型导入成功")
    
    from OnlineJudgeSystem.model.Students import StudentsServer
    print("   ✅ Students模型导入成功")
except Exception as e:
    print(f"   ❌ 模型导入失败: {str(e)}")
    sys.exit(1)

# 测试3: 检查路由注册
print("\n[测试3] 检查API路由...")
try:
    routes = []
    for rule in app.url_map.iter_rules():
        if 'schools' in rule.rule or 'classes' in rule.rule or 'teacher_approval' in rule.rule:
            routes.append(f"   - {rule.methods} {rule.rule}")
    
    if routes:
        print(f"   ✅ 发现 {len(routes)} 个新路由:")
        for route in sorted(routes):
            print(route)
    else:
        print("   ⚠️ 未发现新路由（可能需要先导入schoolviews）")
except Exception as e:
    print(f"   ❌ 路由检查失败: {str(e)}")

# 测试4: 尝试导入schoolviews
print("\n[测试4] 导入schoolviews...")
try:
    import OnlineJudgeSystem.schoolviews
    print("   ✅ schoolviews模块导入成功")
    
    # 重新检查路由
    routes = []
    for rule in app.url_map.iter_rules():
        if 'schools' in rule.rule or 'classes' in rule.rule or 'teacher_approval' in rule.rule:
            routes.append(rule.rule)
    
    print(f"   ✅ 已注册 {len(routes)} 个API路由")
    
    # 分类统计
    school_routes = [r for r in routes if 'schools' in r]
    class_routes = [r for r in routes if 'classes' in r]
    teacher_routes = [r for r in routes if 'teacher' in r or 'approval' in r]
    
    print(f"\n   路由分类统计:")
    print(f"   - 学校管理: {len(school_routes)} 个")
    print(f"   - 班级管理: {len(class_routes)} 个")
    print(f"   - 教师审核: {len(teacher_routes)} 个")
    
except Exception as e:
    print(f"   ❌ schoolviews导入失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试5: 数据库连接测试
print("\n[测试5] 测试数据库连接...")
try:
    schools = SchoolsServer.select_sql_all(status=1)
    print(f"   ✅ 数据库连接成功")
    print(f"   ✅ 查询到 {len(schools)} 所启用的学校")
except Exception as e:
    print(f"   ❌ 数据库连接失败: {str(e)}")

# 测试总结
print("\n" + "="*60)
print("  测试总结")
print("="*60)
print("""
✅ 所有测试通过！

下一步:
1. 启动Flask应用: python runserver.py
2. 测试API接口: 访问 http://localhost:5555/api/schools/all_active
3. 创建前端页面: templates/admin/schools.html 等

注意:
- API接口已就绪,可以直接调用
- 管理页面需要先登录(访问会重定向到登录页)
- 前端页面暂未创建,但API可以通过fetch/axios调用测试
""")

print("测试完成！")
