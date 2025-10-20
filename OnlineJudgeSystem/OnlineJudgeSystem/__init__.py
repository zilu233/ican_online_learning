"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)





import OnlineJudgeSystem.views
import OnlineJudgeSystem.adminuserviews
import OnlineJudgeSystem.teacherviews
import OnlineJudgeSystem.usersviews
import OnlineJudgeSystem.schoolviews  # 多学校班级管理系统API
