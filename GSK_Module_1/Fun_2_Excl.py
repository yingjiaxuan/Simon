import xlrd
import re
import xlsxwriter


def func_Get_Postal_Code_Dict(file_url):
    file1 = file_url
    workbook = xlrd.open_workbook(file1)
    sheet = workbook.sheet_by_index(0)  # 索引从0开始
    dict_Postal_Code_City = {}
    line_max = sheet.nrows
    for i in range(line_max):
        dict_Postal_Code_City[str(sheet.row_values(i)[1])[0:4]] = sheet.row_values(i)[0]
        dict_Postal_Code_City[str(sheet.row_values(i)[3])[0:4]] = sheet.row_values(i)[2]
    return dict_Postal_Code_City


# print(func_Get_Postal_Code('C:\Personal_File\DiskF\GSK_Intern\Trainning_Data.xlsx')) #测试输出，填入文件地址即可（必须是4列）

def func_Get_Postal_Code(t):
    m = re.search(r'[0-9]{4,6}', t)
    if m == None:
        return t, m
    tur = m.span()
    s_re = t[0:tur[0]] + t[tur[1]:len(t)]
    return s_re, m.group(0)

def Pro_Postal_Code(code):
    if code == None:
        return None
    else:
        return str(code)[0:4]

def Copy_Excel (source_url,goal_no_postal,goal_postal):
    workbook_source = xlrd.open_workbook(source_url)
    workbook_goal = xlsxwriter.Workbook(goal_no_postal)  # 创建一个excel文件，存没有邮编的
    workbook_goal2 = xlsxwriter.Workbook(goal_postal)  # 存有邮编的
    worksheet = workbook_goal.add_worksheet()  # 在文件中创建一个名为TEST的sheet,不加名字默认为sheet1,目标
    worksheet2 = workbook_goal2.add_worksheet()

    worksheet.set_column('A:A', 100)
    worksheet2.set_column('A:A', 100)
    sheet = workbook_source.sheet_by_index(0)  # 索引从0开始
    line_max = sheet.nrows
    loop_1 = 0
    loop_2 = 0
    for i in range(line_max):
        t = sheet.row_values(i)[0]
        m = re.search(r'[a-zA-z]{4,20}', t)  # 洗掉英文地址
        tem, Postal_Code = func_Get_Postal_Code(t)
        if Postal_Code == None and m == None:
            worksheet.write(loop_1, 0, sheet.row_values(i)[0])
            loop_1 = loop_1 + 1
        if Postal_Code != None and m == None:
            worksheet2.write(loop_2, 0, sheet.row_values(i)[0])
            loop_2 = loop_2 + 1
    # 输出时
    workbook_goal.close()
    workbook_goal2.close()
    print('Finish_Copy')
#**************以下为去重*********************
def Deduplication_Sheet(source_url,goal_url):
    workbook_source = xlrd.open_workbook(source_url)
    #workbook_goal = xlsxwriter.Workbook('C:\Personal_File\DiskF\GSK_Intern\data_temp.xlsx')
    workbook_goal = xlsxwriter.Workbook(goal_url)
    worksheet = workbook_goal.add_worksheet()
    worksheet.set_column('A:A', 100)
    sheet = workbook_source.sheet_by_index(0)
    line_max = sheet.nrows

    loop_3=0
    L_Hos_N = []#记得每次更新后初始化，用于暂存医院名和长度
    L_Hos_L = []
    i=0
    while i<line_max:#以名字为关键字去重,并且默认一个事实，一名字在一个城市只对应一所医院
        Name = sheet.row_values(i)[0]
        L_Hos_N.append(sheet.row_values(i)[1])
        L_Hos_L.append(len(sheet.row_values(i)[1]))
        tem, Postal_Code_this = func_Get_Postal_Code(sheet.row_values(i)[1])#要么返回邮编，要么返回None
        Postal_Code_this=Pro_Postal_Code(Postal_Code_this)
        if i+1 == line_max:
            tem, Postal_Code_next = func_Get_Postal_Code(sheet.row_values(i)[1])
            Postal_Code_next=Pro_Postal_Code(Postal_Code_next)
        else:
            tem, Postal_Code_next = func_Get_Postal_Code(sheet.row_values(i+1)[1])
            Postal_Code_next=Pro_Postal_Code(Postal_Code_next)
        j=i+1
        while j<line_max and sheet.row_values(j)[0] == Name and Postal_Code_this == Postal_Code_next and Postal_Code_this != None:
            L_Hos_N.append(sheet.row_values(j)[1])
            L_Hos_L.append(len(sheet.row_values(j)[1]))
            tem, Postal_Code_this = func_Get_Postal_Code(sheet.row_values(j)[1])  # 要么返回邮编，要么返回None
            Postal_Code_this = Pro_Postal_Code(Postal_Code_this)
            if j + 1 == line_max:
                tem, Postal_Code_next = func_Get_Postal_Code(sheet.row_values(j)[1])
                Postal_Code_next = Pro_Postal_Code(Postal_Code_next)
            else:
                tem, Postal_Code_next = func_Get_Postal_Code(sheet.row_values(j + 1)[1])
                Postal_Code_next = Pro_Postal_Code(Postal_Code_next)
            Name = sheet.row_values(j)[0]
            j=j+1#所有相同的暂存到list中
        max = L_Hos_L[0]
        max_num = 0
        for loop in range(len(L_Hos_N)):
            if L_Hos_L[loop]>=max:
                max = L_Hos_L[loop]#比出一个最长的
                max_num = loop
        worksheet.write(loop_3, 0, L_Hos_N[max_num])#这个i得改
        loop_3=loop_3+1
        L_Hos_N = []  # 记得每次更新后初始化，用于暂存医院名和长度
        L_Hos_L = []
        i=j
    workbook_goal.close()
    print ("名称关键字去重完成")#*******************以下再把邮编一样的去掉

    # workbook_source = xlrd.open_workbook('C:\Personal_File\DiskF\GSK_Intern\data_temp.xlsx')
    # workbook_goal = xlsxwriter.Workbook(goal_url)
    # worksheet = workbook_goal.add_worksheet()
    # worksheet.set_column('A:A', 100)
    # sheet = workbook_source.sheet_by_index(0)
    # line_max = sheet.nrows
    # loop_3 = 0
    # # L_Hos_N = []  # 记得每次更新后初始化，用于暂存医院名和长度
    # # L_Hos_L = []
    # i = 0
    # while i < line_max-1:  # 二次去重
    #     j=i
    #     if sheet.row_values(j)[0] == sheet.row_values(j+1)[0]:
    #         j=j+1
    #     worksheet.write(loop_3, 0, sheet.row_values(i)[0])
    #     i=j+1
    # workbook_goal.close()
Deduplication_Sheet('C:\Personal_File\DiskF\GSK_Intern\Address.xlsx','C:\Personal_File\DiskF\GSK_Intern\demo3.xlsx')
Copy_Excel('C:\Personal_File\DiskF\GSK_Intern\demo3.xlsx','C:\Personal_File\DiskF\GSK_Intern\demo.xlsx','C:\Personal_File\DiskF\GSK_Intern\demo2.xlsx')

#去重，待完成，去不掉——重名，且两个都没写邮政编码


# file1 = 'C:\Personal_File\DiskF\GSK_Intern\Trainning_Data.xlsx'
# workbook = xlrd.open_workbook(file1)
# sheet_name = workbook.sheet_names()[0]
# sheet = workbook.sheet_by_index(0)  # 索引从0开始
# dict_Postal_Code_City = {}
# line_max = sheet.nrows
# list_max = sheet.ncols
# print(line_max, list_max)
# for i in range(line_max):
#     dict_Postal_Code_City[int(sheet.row_values(i)[1])] = sheet.row_values(i)[0]
#     dict_Postal_Code_City[int(sheet.row_values(i)[3])] = sheet.row_values(i)[2]
# print(dict_Postal_Code_City)
# ****************以上完成邮政编码数据字典建立*******************
# rows = sheet.row_values(1)  # 第一行（实际是第二行）
# cols = sheet.col_values(2)  # 第二列（实际是第三列）
# print (cols)
# print(sheet.name, sheet.nrows, sheet.ncols)  # 名称，行数，列数
# print(sheet.cell_value(1, 2))
# print(cols)
# print(sheet_name)#输出Sheet1
# file2 = 'C:\Personal_File\DiskF\GSK_Intern\Address.xlsx'
