import json

#返回结果json
class ResultInfo(object):
    """description of class"""
    def __init__(self):
        self.code;  #1.代表成功 0.代表失败
        self.obj;   #对象实例，或者对象集合实例
        self.msg;   #错误消息
        self.total; #对象总数


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)