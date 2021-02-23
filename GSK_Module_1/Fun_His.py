import re
import xlrd

def func_Delete_Comma(t):  # 去掉各种标点符号和空格
    r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+'
    line = re.sub(r, '', t)
    return line

# 构建邮政编码映射表
def func_Get_Postal_Code_Dict(file_url):
    file1 = file_url
    workbook = xlrd.open_workbook(file1)
    sheet = workbook.sheet_by_index(0)  # 索引从0开始
    dict_Postal_Code_City = {}
    line_max = sheet.nrows
    for i in range(line_max):
        dict_Postal_Code_City[str(sheet.row_values(i)[1])[0:4]] = sheet.row_values(i)[0]
        dict_Postal_Code_City[str(sheet.row_values(i)[3])[0:4]] = sheet.row_values(i)[2]

        dict_Postal_Code_City[str(sheet.row_values(i)[5])[0:4]] = sheet.row_values(i)[4]
        dict_Postal_Code_City[str(sheet.row_values(i)[7])[0:4]] = sheet.row_values(i)[6]

        dict_Postal_Code_City['0' + str(sheet.row_values(i)[9])[0:3]] = sheet.row_values(i)[8]
        dict_Postal_Code_City['0' + str(sheet.row_values(i)[11])[0:3]] = sheet.row_values(i)[10]

        dict_Postal_Code_City['0' + str(sheet.row_values(i)[13])[0:3]] = sheet.row_values(i)[12]
        dict_Postal_Code_City['0' + str(sheet.row_values(i)[15])[0:3]] = sheet.row_values(i)[14]

    print("邮政编码映射表构建完成")
    print('')
    return dict_Postal_Code_City

# 提取分词后的科室——待升级，这一份由于是正序遍历，不符合基本逻辑，已被替换，仅留作参考
def func_Get_Dep(text):  # 提取分词后的科室——待升级，这一份由于是正序遍历，不符合基本逻辑，所以需要重写
    List_k = []
    for i in range(len(text)):
        t = text[i][0]  # 添加标注会增加运行成本，后期需要改进
        m = re.search(r'[\u4e00-\u9fa5]{1,10}科$', t)
        if m != None and m.group(0) != '医科' and m.group(0) != '首都儿科':  # 这就是一些容易被误会的名字，也是补丁
            # if i<(len(text)-1) and text[i+1][0] != "医院":#由于会有专科医院，这得拿掉
            if i < (len(text) - 1) and text[i + 1][0] == "医院":
                continue
            text[i] = ('GG', 'GG')  # 提取出来后变为GG
            # *********从下面一行开始为科室打补丁（权宜之计，因为暂时没找到原词典怎么改）下一步修改方案，直到医院之前全部并入科室（可能会过拟合）
            if i >= 1 and text[i - 1][0] == '感染':
                t = '感染' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '临床':
                t = '临床' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '神经':
                t = '神经' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '肾':
                t = '肾' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '肾病':
                t = '肾病' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '风湿免疫':
                t = '风湿免疫' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '小儿':
                t = '小儿' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '内':
                t = '内' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '肾脏':
                t = '肾脏' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '心血管':
                t = '心血管' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '免疫':
                t = '免疫' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 1 and text[i - 1][0] == '呼吸与':
                t = '呼吸与' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
            elif i >= 2 and text[i - 1][0] == '免疫' and text[i - 2][0] == '风湿':
                t = '风湿' + '免疫' + m.group(0)
                List_k.append(t)
                text[i - 1] = ('GG', 'GG')
                text[i - 2] = ('GG', 'GG')
            # *********这一行之上是补丁
            else:
                List_k.append(m.group(0))
    return List_k

# 推断研究所/中心等信息，可能需要自上而下向前推断重写，目前采用半穷举，最优先优化对象，已被替换，仅留作参考
def func_Infer_Dep(text, num):
    t = ''
    if text[len(text) - 1][0] == "研究所" or text[len(text) - 1][0] == "教研室" or text[len(text) - 1][0] == "中心" \
            or text[len(text) - 1][0] == "医学院" or text[len(text) - 1][0] == "学院" or text[len(text) - 1][0] == "实验室" \
            or text[len(text) - 1][0] == "免疫室":
        sum = []
        sum.append(text[len(text) - 1][0])
        if text[len(text) - 2][0] != '医院':
            sum.append(text[len(text) - 2][0])
        if text[len(text) - 3][0] == '风湿' or text[len(text) - 3][0] == '精神' or text[len(text) - 3][0] == '第一' \
                or text[len(text) - 3][0] == '第二' or text[len(text) - 3][0] == '同位素':
            sum.append(text[len(text) - 3][0])
            print("科室/研究所/中心，推断为：", end='')
            t = print_list(sum, 1)
            Excl_wri(worksheet, num, 6, "推断为：" + t)
            print('')
        else:
            print("科室/研究所/中心，推断为：", end='')
            t = print_list(sum, 1)
            Excl_wri(worksheet, num, 6, "推断为：" + t)
            print('')
    return t