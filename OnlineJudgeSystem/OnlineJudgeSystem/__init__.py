"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)





import OnlineJudgeSystem.views
import OnlineJudgeSystem.adminuserviews
import OnlineJudgeSystem.teacherviews
import OnlineJudgeSystem.usersviews
