import re
import xlrd
import xlsxwriter
import pkuseg
import random


# 提取邮政编码及剩余字符串
def func_Get_Postal_Code(t):
    m = re.search(r'[0-9]{5,6}', t)
    if m == None:
        # print('无邮政编码')
        return t, m
    tur = m.span()
    s_re = t[0:tur[0]] + t[tur[1]:len(t)]
    return s_re, m.group(0)


# 去除字符以外的全部符号
def func_Delete_Comma(line):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('', line)
    return line


# 构建邮政编码映射表
def func_Get_Postal_Code_Dict_2(file_url):
    file1 = file_url
    workbook = xlrd.open_workbook(file1)
    sheet = workbook.sheet_by_index(0)  # 索引从0开始
    dict_Postal_Code_City = {}
    i = 1
    while i < 2289:  # 以下这段由于excel的问题，耦合度过高，且很可能不完整，有问题
        x = int(sheet.row_values(i)[2])
        if len(str(x)) == 6:
            dict_Postal_Code_City[str(x)[0:4]] = sheet.row_values(i)[0]
        else:
            dict_Postal_Code_City['0'+str(x)[0:3]] = sheet.row_values(i)[0]
        i = i + 1
    dict_Postal_Code_Province = {'10':'北京/河北','51':'广东','20':'上海','30':'天津/河北','40':'重庆',\
                                 '43':'湖北','61':'四川','71':'陕西','05':'河北','07':'河北','06':'河北',\
                                 '04':'山西','45':'河南','46':'河南','47':'河南','11':'辽宁','12':'辽宁',\
                                 '15':'黑龙江','16':'黑龙江/内蒙古','02':'内蒙古','01':'内蒙古',\
                                 '03':'内蒙古/山西','13':'内蒙古/吉林','73':'内蒙古/甘肃','75':'内蒙古','21':'江苏','22':'江苏',\
                                 '24':'山东/安徽','25':'山东','26':'山东','27':'山东','23':'安徽','31':'浙江','32':'浙江',\
                                 '35':'福建','36':'福建','52':'广东','66':'云南','67':'云南','33':'江西',\
                                 '44':'湖北','41':'湖南','42':'湖南','62':'四川','53':'广西','54':'广西','34':'江西',\
                                 '85':'西藏','62':'四川','63':'四川','64':'四川','55':'贵州','56':'贵州','65':'云南',\
                                 '57':'海南','83':'新疆','84':'新疆','72':'陕西','74':'甘肃','75':'宁夏','81':'青海'}
    print("邮政编码一级映射及二级映射表构建完成")
    print('')
    return dict_Postal_Code_City, dict_Postal_Code_Province


# 将list转化为str输出，默认正序输出，输入置1则倒序
def print_list(List, flag=0):  # 默认正序输出，输入置1则倒序
    max = len(List)
    t = ''
    if flag == 0:
        for i in range(max):
            t = t + List[i]
    if flag != 0:
        max = -max
        i = -1
        while i >= max:
            t = t + List[i]
            i = i - 1
    print(t, end='')
    return t


# 处理句末出现的地址信息变为GG——未来会加入处理句首
def Pro_Fin_ADD(text):
    min_len = len(text)
    i = -1
    num = []
    if min_len >= 3:
        while i >= -2 and len(text[i][0]) <= 9:  # 写9完全是因为存在新疆这个超长
            if text[i][1] == 'ns' and text[i + 1][0] != '大学' and text[i + 1][0] != '医科大学' and text[i + 1][
                0] != '医学院' and \
                    text[i + 1][0] != "医院":
                # 打补丁就完事了，主要是某些需要靠名字推城市，只考虑句末
                text[i] = ('GG', 'GG')
            i = i - 1

    if min_len == 2:  # 应对 中国人民解放军第二炮兵总医院北京
        if text[1][1] == 'ns':
            text[1] = ('GG', 'GG')
    if text[0][1] == 'ns' and text[0][0] == '成都' and text[1][1] == 'ns':  # 少数情况应该单独挖掉
        text[0] = ('GG', 'GG')
    if text[0][1] == 'ns' and text[0][0] == '湛江' and text[1][1] == 'ns':  # 少数情况应该单独挖掉
        text[0] = ('GG', 'GG')
    if text[-1][1] == 'nr':
        text[-1] = ("GG", "GG")
    # *******************此处往下挖掉所有判定不出ns的末尾地址——因为是极少数，进行打补丁即可，增强逻辑反而可能出错
    if text[-1][0] == '孝感':
        text[-1] = ("GG", "GG")
    if text[-1][0] == '永康':
        text[-1] = ("GG", "GG")

    return text


# 写入函数，用一个控制全体写入
def Excl_wri(worksheet, line, list_1, str):
    worksheet.write(line, list_1, str)
    # pass


# 将text中所有不是GG的内容提取整合成字符串
def func_Dele_str(text):
    tem = ''
    for i in range(len(text)):
        if text[i][0] != 'GG':
            tem = tem + text[i][0]
    return tem


# 在邮编无法提取城市的情况下，进行二次城市提取，标明为参考信息，此时句末的地址信息还没洗掉，标点符号已经全部去除
def func_Get_An_City(text, flag_city, worksheet, num_1):
    i = -1
    num = []
    min_len = len(text)
    min_len = -min_len
    while i >= min_len and len(text[i][0]) <= 9:
        if text[i][1] == 'ns':
            num.append(text[i][0])
        i = i - 1
    if len(num) == 0 and flag_city == 2:  # 如果实在没办法——没邮编，又没扫到ns，那就强行拿第一个进去
        num.append('(强制首位)' + text[0][0])
    print('推断城市（越靠前可能性越高）:', end=' ')
    if len(num) == 0:
        print('无')
        Excl_wri(worksheet, num_1, 5, '无')
    else:
        str = print_list(num, 1)
        print("")
        Excl_wri(worksheet, num_1, 5, '推断为：' + str)


# 字符串割去不需要的部分
def fun_Cut_Str(line, t):
    # m = re.compile(str, L_Tem)
    rule = re.compile(t)
    line = rule.sub('', line)
    return line


def Patch_Of_Dep(text, i):
    t = text[i][0]
    m_1 = re.search(r'[\u4e00-\u9fa5]{0,10}院', t)
    m_2 = re.search(r'[\u4e00-\u9fa5]{0,10}大学', t)
    m_3 = re.search(r'[\u4e00-\u9fa5]{0,10}中心', t)
    # *******************此行以上打科室内部补丁（即会把科室包含进去的内容）
    if m_1 == None and m_2 == None and m_3 == None:
        return text
    else:
        if m_1 != None:
            t = m_1.group(0)
            str = fun_Cut_Str(text[i][0], t)  # 挖出来的科室
            text.pop(i)
            if i != -1:
                text.insert(i + 1, (t, 'n'))
                text.insert(i + 1, (str, 'n'))
            else:
                text.append((t, 'n'))
                text.append((str, 'n'))
        if m_2 != None:
            t = m_2.group(0)
            str = fun_Cut_Str(text[i][0], t)  # 挖出来的科室
            text.pop(i)
            if i != -1:
                text.insert(i + 1, (t, 'n'))
                text.insert(i + 1, (str, 'n'))
            else:
                text.append((t, 'n'))
                text.append((str, 'n'))
        if m_3 != None:
            t = m_3.group(0)
            str = fun_Cut_Str(text[i][0], t)  # 挖出来的科室
            text.pop(i)
            if i != -1:
                text.insert(i + 1, (t, 'n'))
                text.insert(i + 1, (str, 'n'))
            else:
                text.append((t, 'n'))
                text.append((str, 'n'))
        return text


# 倒序遍历，并且自上而下增强逻辑——可能会有误判，需要不断补充停止关键字
def func_Get_Dep_2(text):
    List_k = []
    max = len(text)
    max = -max
    i = -1
    while i >= max:
        t = text[i][0]  # 添加标注会增加运行成本，后期需要改进
        m = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}科$', t)  # 为了伺候CT科这种东西，得加上英文
        if m != None and m.group(0) != '医科' and m.group(0) != '首都儿科' and m.group(0) != '山眼科' \
                and m.group(0) != '专科':  # 这就是一些容易被误会的名字，也是补丁
            if i < -1 and text[i + 1][0] == "医院":  # 由于会有专科医院，这得拿掉
                i = i - 1
                continue
            text = Patch_Of_Dep(text, i)  # 长度如果变长了，就说明是分离了信息，直接弹出即可
            if len(text) > -max:
                List_k.append(text[i][0])
                text[i] = ('GG', 'GG')
                i = i - 1  # 补一个i-1
                continue
            # **********方案二——即不通过补丁，通过回溯逻辑**********************
            text[i] = ('GG', 'GG')  # 提取出来后变为GG
            List_k.append(m.group(0))
            j = i - 1
            # n = re.search(r'[\u4e00-\u9fa5]{1,10}院', text[j][0])
            while j >= max:
                n_1 = re.search(r'[\u4e00-\u9fa5]{0,10}院', text[j][0])
                n_2 = re.search(r'[\u4e00-\u9fa5]{0,10}大学', text[j][0])
                n_3 = re.search(r'[\u4e00-\u9fa5]{0,10}中心', text[j][0])
                if n_1 == None and n_2 == None and n_3 == None:
                    List_k.append(text[j][0])
                    text[j] = ('GG', "GG")
                    j = j - 1
                else:
                    if n_1 != None:
                        t = n_1.group(0)
                        str = fun_Cut_Str(text[j][0], t)
                    if n_2 != None:
                        t = n_2.group(0)
                        str = fun_Cut_Str(text[j][0], t)
                    if n_3 != None:
                        t = n_3.group(0)
                        str = fun_Cut_Str(text[j][0], t)
                    if str != '':
                        List_k.append(str)
                    j = j - 1
                    break
        i = i - 1
    return List_k


# 倒序清除list末尾的GG
def Dele_GG(text):
    while text[-1][0] == 'GG':
        text.pop()


# 此处不把学院作为科室，该方法为增强逻辑——正则匹配，而非一一对应，会产生过强的情况，需要在反复测试中打补丁
def func_Infer_Dep_2(text, num):
    List_k = []
    max = len(text)
    max = -max

    t = text[-1][0]
    m_1 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}所$', t)
    m_2 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}中心$', t)
    m_3 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}系$', t)
    m_4 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}室$', t)
    m_4 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}组$', t)
    # **********************多一个 组 ，部************************
    # **********************在这条线上打补丁，改为使用匹配的增强规则，而不是一一对应的照应规则**********************
    if m_1 != None or m_2 != None or m_3 != None or m_4 != None:
        List_k.append(text[-1][0])
        i = -2
        least = -1
        while i >= max:
            t = text[i][0]
            n_1 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}院$', t)  # 因为有单独分出大学的情况，故而从0开始
            n_2 = re.search(r'[\u4e00-\u9fa5a-zA-Z]{0,10}大学', t)  # 因为出现过大学不是末尾的情况，不加$
            if n_1 == None and n_2 == None:
                List_k.append(text[i][0])
                least = i
            else:
                break
            i = i - 1
        if least > max:  # 要去掉把全部内容匹配进去的情况——杭州市血液中心
            print("科室/研究所/中心，推断为：", end='')
            t = print_list(List_k, 1)
            Excl_wri(worksheet, num, 6, "推断为：" + t)
            print('')
            return t
        else:
            print("科室/研究所/中心，推断为：", '无')
            return ''
    else:
        return ''


# 处理字符串主函数
def func_Processor(dict_Postal_Code_City, dict_Postal_Code_Province, t, num, name, worksheet, loop=0):
    if loop != 0:
        num = loop
        print("循环编号:", loop)
    print("序号：", num, '   ', '姓名：', name)
    Excl_wri(worksheet, num, 0, num)  # 录入编号
    Excl_wri(worksheet, num, 1, name)  # 录入姓名
    print("原序列：", t)
    Excl_wri(worksheet, num, 2, t)  # 录入原序列
    tem, Postal_Code = func_Get_Postal_Code(t)
    flag_city = 1  # 默认找得到城市
    if Postal_Code != None:
        Excl_wri(worksheet, num, 3, Postal_Code)
        Postal_Code_City = Postal_Code[0:4]
        Postal_Code_Province = Postal_Code[0:2]
        if dict_Postal_Code_City.get(Postal_Code_City) != None and dict_Postal_Code_Province.get(Postal_Code_Province) != None:
            print('邮编：' + Postal_Code, '市/直辖市区：' + dict_Postal_Code_City[Postal_Code_City],
                  '省/直辖市：' + dict_Postal_Code_Province[Postal_Code_Province])
            Excl_wri(worksheet, num, 4, 1)
            Excl_wri(worksheet, num, 5, dict_Postal_Code_City[Postal_Code_City])
            Excl_wri(worksheet, num, 10, dict_Postal_Code_Province[Postal_Code_Province])
        elif dict_Postal_Code_City.get(Postal_Code_City) == None and dict_Postal_Code_Province.get(Postal_Code_Province) == None:
            print('邮编：' + Postal_Code, '省/市/直辖市/区：暂无映射，请检查数据库，并补充')
            flag_city = 3  # 表示有邮编，但没能映射
            Excl_wri(worksheet, num, 4, 3)
        elif dict_Postal_Code_City.get(Postal_Code_City) == None and dict_Postal_Code_Province.get(Postal_Code_Province) != None:
            print('邮编：' + Postal_Code, '市/直辖市区：暂无映射，请检查数据库，并补充' ,
                  '省/直辖市：' + dict_Postal_Code_Province[Postal_Code_Province])
            Excl_wri(worksheet, num, 4, 3)
          # Excl_wri(worksheet, num, 5, dict_Postal_Code_Province[Postal_Code_Province])
            Excl_wri(worksheet, num, 10, dict_Postal_Code_Province[Postal_Code_Province])
    else:
        print('邮编：无')
        flag_city = 2  # 表示无邮编
        Excl_wri(worksheet, num, 4, 2)

    tem = func_Delete_Comma(tem)  # 去除全部的标点符号和空格——考虑到可能有021-111这种非标点数据，这一步没放在最前面
    seg = pkuseg.pkuseg(model_name='medicine', postag=True)  # 程序会自动下载所对应的细领域模型，此处浪费资源了，后期改进
    text = seg.cut(tem)  # 进行分词

    if flag_city == 2 or flag_city == 3:
        func_Get_An_City(text, flag_city, worksheet, num)
    # L_Dep = func_Get_Dep(text)  # 提取科室——方案一——补丁
    L_Dep = func_Get_Dep_2(text)  # 提取科室——方案二——增强逻辑
    text = Pro_Fin_ADD(text)  # 末尾地址改成GG
    L_Tem = func_Dele_str(text)
    if len(L_Dep) != 0:
        # print("科室：" + L_Dep[0], "剩余内容：" + L_Tem)
        print('科室：', end='')
        str = print_list(L_Dep, 1)
        Excl_wri(worksheet, num, 6, str)
        Excl_wri(worksheet, num, 7, 1)
        print(' 剩余内容:' + L_Tem, end="")
        Excl_wri(worksheet, num, 8, L_Tem)
        print('\n')
    else:  # 下方推断逻辑依旧需要重写为自上而下的增强逻辑用于选择，需要重写
        Dele_GG(text)
        print("科室：暂无", "剩余内容：" + L_Tem)
        Excl_wri(worksheet, num, 7, 2)
        Excl_wri(worksheet, num, 9, L_Tem)
        # str = func_Infer_Dep(text, num)  # 推断出的科室字符串
        str = func_Infer_Dep_2(text, num)  # 增强逻辑推断科室字符串
        str = fun_Cut_Str(L_Tem, str)  # 去除科室字符串

        Excl_wri(worksheet, num, 8, str)
        if str != '':
            print('猜测后剩余内容:', str)
        print('')

if __name__ == '__main__':
    # *********************程序开始************************************
    dict_Postal_Code_City, dict_Postal_Code_Province = func_Get_Postal_Code_Dict_2(
        'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Postal_Code.xlsx')
    workbook_source = xlrd.open_workbook("C:\Personal_File\DiskF\GSK_Intern\Address.xlsx")
    sheet = workbook_source.sheet_by_index(0)  # 索引从0开始
    line_max = sheet.nrows

    # *********************写入文件模块****************************
    workbook_goal = xlsxwriter.Workbook('C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Actual_Demo_4.xlsx')
    worksheet = workbook_goal.add_worksheet()
    worksheet.set_column('C:C', 60)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 20)
    worksheet.set_column('I:I', 40)
    worksheet.set_column('J:J', 40)
    worksheet.set_column('K:K', 20)
    worksheet.write(0, 0, '序号')
    worksheet.write(0, 1, '姓名')
    worksheet.write(0, 2, '原序列')
    worksheet.write(0, 3, '邮编')
    worksheet.write(0, 4, '邮编是否可直接推断（1表示可以，2表示无邮编，城市为推断所得，3表示有邮编，但是无映射）')
    worksheet.write(0, 5, '市/直辖市区（若备注推断，则默认越靠前可能性越高）')  # 记得加备注标明是否是推断出来的
    worksheet.write(0, 6, '科室（若备注推断，结果仅供参考）')  # 记得加备注标明是否是推断出来的
    worksheet.write(0, 7, '科室是否是直接所得（1表示是，2表示推断所得，仅供参考）')
    worksheet.write(0, 8, '剩余内容（一般为医院名）')
    worksheet.write(0, 9, '科室推断前剩余内容（进行了中心/科室二次推断才会有，用于回溯）')
    worksheet.write(0, 10, '省/直辖市')
    # *********************范围测试********************************
    # i = 80
    # while i < 84:  # 修改这里确认作用范围
    #     name = sheet.row_values(i)[0]
    #     t = sheet.row_values(i)[1]
    #     m = re.search(r'[a-zA-z]{4,20}', t)  # 洗掉英文地址
    #     tem, Postal_Code = func_Get_Postal_Code(t)
    #     if m == None:
    #         func_Processor(dict_Postal_Code_City,dict_Postal_Code_Province, t, i, name, worksheet)
    #     i = i + 1
    # workbook_goal.close()
    # print('Finish_Processing')
    # *********************范围测试********************************
    # *********************随机测试********************************
    loop = 1
    while loop <= 20:  # 修改这里修改测试次数
        i = random.randrange(1, 22838)  # 修改这里修改随机范围
        name = sheet.row_values(i)[0]
        t = sheet.row_values(i)[1]  # 要处理的字符串
        m = re.search(r'[a-zA-z]{4,20}', t)  # 洗掉英文地址
        tem, Postal_Code = func_Get_Postal_Code(t)
        if m == None:
            func_Processor(dict_Postal_Code_City, dict_Postal_Code_Province, t, i, name, worksheet, loop)
        loop = loop + 1
    workbook_goal.close()
    print('Finish_Processing')
    # *********************随机测试********************************


# 小结 7.25
# Fun_1主要功能——分词邮编，邮编映射城市（无法映射的情况下靠剩余内容映射暂时未完成，需要一天）
# 从内容中提取科室，暂时只能提取科室，学系，中心之类的内容暂时只能靠手动添加字典实现——也就是别人的字典还不够好用
# 对于邮编返回None的内容，提取一次cpca或者pkuseg，尝试提取城市——和上方做一个判定逻辑

# 小结 7.29
# 剩余问题：眼科中心，会直接提取出眼科，暂缓解决——已通过增加映射暂时解决
# 剩余问题：当同时存在“中心类”以及科室，比如 第二军医大学长征医院实验诊断科临床免疫中心 会直接提取出实验诊断科，这可能是一个bug
# 剩余问题：由于存在医院名不在分词段末尾的情况，会产生科室提取不全的情况，如 上海交通大学医学院附属仁济医院风湿病学科 只能提取出学科，
# # 这是一个bug——已解决
# 剩余问题：本程序默认一个字段只有一组信息，故如果输入多组信息字段，需要先进行分句

# 小结 7.31
# 完成正式1.0版本
# 修复二级映射完成不填表的bug
# 修复科室等分词内部带“院”等导致停用词失效的问题
# 剩余问题：尚未完成文件预处理模块，使之符合并行处理的条件


# ****************************以下为cpca分离提取省市区信息，暂缓*****************************
# location_str = []
# import cpca
# location_str.append(tem)
# df = cpca.transform(location_str, pos_sensitive=True,cut=False)#默认情况下参数为True,可以选择换为False，可以给一个umap的字典映射
# # for i in range(3):
# #     for j in range (3):
# print(df)
#
# #m = re.search(r'[0-9]{5,6}', t)
#
# if int(df.iloc[0,4])>=len(df.iloc[0,3])-7:
#     df.iloc[0,3]=df.iloc[0,3][0:df.iloc[0,4]]
# elif int(df.iloc[0,5])>=len(df.iloc[0,3])-5:
#     df.iloc[0, 3] = df.iloc[0, 3][0:df.iloc[0, 5]]
#
# if (int(df.iloc[0,4]) <=2 and int(df.iloc[0,4]) >=0) or (int(df.iloc[0,5]) <=2 and int(df.iloc[0,4]) >=0):
#
#
# print(df)
