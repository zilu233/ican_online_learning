class PageTool(object):
    def __init__(self,data_list,page,per_data_num = 6):
        '''
        初始化
        :param data_list: 所有数据列表
        :param page: 当前要查看的列表页
        :param per_data_num: 每页默认要显示几条
        '''
        self.data_list = data_list
        self.page = page
        self.per_data_num = per_data_num

    @property
    def start(self):
        '''
        计算引索的起始位置
        :return:
        '''
        return (self.page - 1) * self.per_data_num

    @property
    def end(self):
        '''
        计算引索的结束位置
        :return:
        '''
        return self.page * self.per_data_num

    def show(self):
        '''
        切片取数据,展示对应分页的结果
        :return:
        '''
        result = self.data_list[self.start:self.end]
        return result

    '''
while True:
    # 1.输入要查看的页码
    page = int(input("请输入要查看的页码:"))
    obj = PageTool(data_list,page)
    obj.show()
    '''
