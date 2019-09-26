# 基于pkuseg的GSK医疗领域中文分词
此程序相对偏脚本，以下将分几个方面进行叙述




## 目录

* [主要功能](#主要功能)
* [使用及运行](#使用及运行)
* [样例及结果](#样例及结果)
* [详细入口参数及使用方法](#详细入口参数及使用方法)
* [其余方法说明](#其余方法说明)
* [并行化、改进及维护](#并行化、改进及维护)
* [引用及参考](#引用及参考)
* [文件说明](#文件说明)
* [写在最后](#写在最后)


## 主要功能
本程序具有如下几个特点：

1. 医疗领域字符串专项分词——邮政编码（中国）、科室信息、医院名称、所在地等。
2. 基于北京大学pkuseg模块——[**pkuseg：一个多领域中文分词工具包**](https://github.com/lancopku/PKUSeg-python)
3. 支持词性标注
4. 支持对已有数据做范围测试或顺序测试
5. 分词处理统计效率在i5-7300HQ+单8g内存条件下大约为20条/分钟
6. 并行化模块处于测试阶段，暂不推荐使用

## 使用及运行
- 运行本程序必须安装pkuseg模块
- pkuseg目前**仅支持python3**
- **为了获得好的效果和速度，强烈建议大家通过pip install更新到目前的最新版本**

    以下包安装内容引用自[pkuseg官方文档](https://github.com/lancopku/PKUSeg-python)
    

1. 通过PyPI安装(自带模型文件)：
	```
	pip3 install pkuseg
	之后通过import pkuseg来引用
	```
	建议更新到最新版本以获得更好的分词标注体验：
	```
   pip3 install -U pkuseg 
    ```
2. 如果PyPI官方源下载速度不理想，建议使用镜像源，比如：   
   初次安装：
	```
	pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pkuseg
	```
   更新：
	```
	pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pkuseg
	```
   
3. 如果不使用pip安装方式，选择从GitHub下载，可运行以下命令安装：
	```
	python setup.py build_ext -i
	```
	
   GitHub的代码并不包括预训练模型，因此需要用户自行下载或训练模型，预训练模型可详见[release](https://github.com/lancopku/pkuseg-python/releases)。使用时需设定"model_name"为模型文件。

注意：**安装方式1和2目前仅支持linux(ubuntu)、mac、windows 64 位的python3版本**。如果非以上系统，请使用安装方式3进行本地编译安装。

建议（本人补充）：推荐使用[**pycharm**](https://www.jetbrains.com/pycharm/download/#section=windows)作为编译器，同时使用[**Anaconda**](https://www.anaconda.com/)包管理器用以包管理



## 样例及结果
以下选择两个典型原数据展示输出结果：

输入：

| *序号* | 姓名 | 原序列 |
| :-----: | :--------: | :-----: |
|   1  |     孙凌云 |  南京大学医学院附属鼓楼医院风湿免疫科 |
| 2 |    李向培|  安徽医科大学附属省立医院风湿免疫科,合肥,230001 |

输出：

| 邮编 | 邮编信度 | 省/直辖市 |市/直辖市区 | 科室 | 剩余内容 |
|:----:| :--------: | :-----: |:-----: | :--------: | :-----: |
|无    |2|  无 | 推断为：南京   | 风湿免疫科 |南京大学医学院附属鼓楼医院|
|230001|1|安徽|合肥 |风湿免疫科|安徽医科大学附属省立医院 |

## 详细入口参数及使用方法

### 代码解析——基于文件[Fun_1.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_1.py)
以下代码示例适用于python交互式环境及pycharm编译器。

#### 测试方法1——顺序测试（源文件388-389行）
```python3
i = 80 # 起始行
while i < 84:  # 终结行
    name = sheet.row_values(i)[0]
    t = sheet.row_values(i)[1]
    m = re.search(r'[a-zA-z]{4,20}', t)  # 洗掉英文地址
    tem, Postal_Code = func_Get_Postal_Code(t)
    if m == None:
        func_Processor(dict_Postal_Code_City,dict_Postal_Code_Province, t, i, name, worksheet)
    i = i + 1
workbook_goal.close()
print('Finish_Processing')
```
#### 测试方法2——随机测试（源文件401-402行）
```python3
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
```
#### 字符串处理主方法（源文件290-357行）
```python3
func_Processor(dict_Postal_Code_City, dict_Postal_Code_Province, t, num, name, worksheet, loop=0)
	dict_Postal_Code_City		邮编——市/直辖市区映射字典表（基于输入邮编文件路径生成）
	dict_Postal_Code_Province       邮编——省/直辖市映射字典表（基于输入邮编文件路径生成）
	t                               待处理字符串（基于输入待处理文件路径，按行循环生成）
	num                             输出文件中的序号（基于待处理字符串所在行号生成）
	name                            姓名（基于待处理字符串所在行号name列生成）
	worksheet                       目标文件路径（基于输入的输出文件路径生成）
	loop=0                          默认0，当随机测试时，置为1
```
#### 调试方法及输入格式
```python3
dict_Postal_Code_City, dict_Postal_Code_Province = func_Get_Postal_Code_Dict_2('C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Postal_Code.xlsx')
workbook_source = xlrd.open_workbook("C:\Personal_File\DiskF\GSK_Intern\Address.xlsx")
分别修改以上两条路径为：
    邮编映射表路径（.xlsx）
    输入文件路径（.xlsx）
workbook_goal = xlsxwriter.Workbook('C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Actual_Demo_4.xlsx')
修改以上路径为：
    目标输出文件路径（.xlsx）
```

1. [邮编映射表参考](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Postal_Code_Data.xlsx),[输入文件参考](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Address.xlsx)（输入文件必须第一列为姓名，第二列为待处理字符串，否则无法识别）
2. 批量处理时，应当注释掉随机测试模块，使用顺序测试模块，并将范围定为0~line_max
3. 文档中剩余功能性方法已全部注释，可通过文字了解功能，后期可能会更新一个文档说明各个方法的机理
（目前修改以上内容即可进行处理及功能应用了）

## 其余方法说明
### 1.func_Get_Postal_Code
```python3
# 提取邮政编码及剩余字符串，入口参数为待处理字符串，返回剩余字符串及提取出的邮编
def func_Get_Postal_Code(t):
    m = re.search(r'[0-9]{5,6}', t)
    if m == None:
        # print('无邮政编码')
        return t, m
    tur = m.span()
    s_re = t[0:tur[0]] + t[tur[1]:len(t)]
    return s_re, m.group(0)

```
### 2.func_Delete_Comma
```python3
# 去除字符以外的全部符号，入口参数为字符串，出口参数为处理后的字符串
def func_Delete_Comma(line):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('', line)
    return line

```
### 3.func_Get_Postal_Code_Dict_2
```python3
# 构建邮政编码映射表，入口参数为邮编数据表，出口参数为一级映射及二级映射表——建议对结果进行序列化本地存储
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
```
### 4.Pro_Fin_ADD
```python3
# 处理句末出现的地址信息变为GG——未来会加入处理句首，入口参数为待处理list，出口参数为处理后list
# 建议将补丁部分生成本地字典导入分词方法
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
```
### 5.func_Get_An_City
```python3
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
```
### 6.Patch_Of_Dep
```python3
# 对科室的补丁处理，同样推荐生成本地字典
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
```
### 7.func_Get_Dep_2
```python3
# 倒序遍历，提取科室方法，并且自上而下增强逻辑——可能会有误判，需要不断补充停止关键字，同样推荐生成本地字典
# 入口参数为text，出口参数为list
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
```
### 8.func_Processor
```python3
# 提取“类科”方法，入口参数为text及表格写入列num，返回值为字符串
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
```

## 并行化、改进及维护
### 1.并行化
已完成并行化模块（[Test_Parallel.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Test_Parallel.py)）
需要使用python第三方库pp（parallel python），相关说明文档将于近期完成
### 2.改进
源文件（[Fun_1.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_1.py))中对于需要增加与否停用词等已做注释，后期也会更新本文档进行详细说明
### 3.维护
不建议修改除文件路径，停用词以外的任何内容，以免造成不可估计的逻辑错误

## 文件说明
1. [Fun_1.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_1.py)
字符串处理主函数，程序完整功能及应用
2. [Fun_2_Excl.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_2_Excl.py)
Excel文档相关处理方法参考
3. [Fun_3.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_3.py)
pkuseg小范围分词单独测试
4. [fun_4.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/fun_4.py)
并行模块开发（待优化，目前处于无法运行状态）
5. [Fun_5.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_5.py)
并行原理模块参考
6. [Fun_6.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_6.py)
进程池方法实现并行方法测试
7. [Address.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Address.xlsx)
待处理数据
8. [Postal_Code_Data.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Postal_Code_Data.xlsx)
邮编映射表
9. [Actual_Demo_1.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Actual_Demo_1.xlsx)
基于7的输出结果

## 写在最后
此为本程序README文档的2.0版本，后续会持续更新，下次更新预计解决：
并行化接口的使用说明

有任何关于本程序的问题及建议，欢迎将邮件发至：[*yingjiaxuan123@163.com*](link)















