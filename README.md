# 基于pkuseg的GSK医疗领域中文分词
此程序相对偏脚本，以下将分几个方面进行叙述




## 目录

* [主要功能](#主要功能)
* [使用及运行](#使用及运行)
* [样例及结果](#样例及结果)
* [详细入口参数及使用方法](#详细入口参数及使用方法)
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

## 并行化、改进及维护
### 1.并行化
目前暂时不建议使用并行化处理，由于应用环境——windows系统，并行处理时，进程创建成本较高，相关脚本开发尚未通过测试，完成后会更新本文档
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
10. [requirements.txt](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/requirements.txt) python包需求文件，可直接装载

## 写在最后
此为本程序README文档的1.0版本，后续会持续更新，下次更新预计解决：
程序内全部方法的说明

有任何关于本程序的问题及建议，欢迎将邮件发至：[*yingjiaxuan123@163.com*](link)















