# Chinese word segmentation in GSK medical field based on pkuseg
This program is relatively partial script, the following of this file will describe in several aspects.

## Catalogue

* [Main Feature](#Main_Feature)
* [How to use](#How_to_use)
* [Test Sample](#Test_Sample)
* [File Explanation](#File_Explanation)
* [All in All](#All_in_All)

## Main_Feature

This program has the following features:

1. Specialized Segmentation for Medical Domain Strings: Includes segmentation for postal codes (China), department information, hospital names, locations, etc.
2. Based on Peking University's pkuseg Module: pkuseg: A Toolkit for Multi-Domain Chinese Word Segmentation[**pkuseg：一个多领域中文分词工具包**](https://github.com/lancopku/PKUSeg-python)
3. Supports Part-of-Speech Tagging
4. Supports Range Testing or Sequential Testing on Existing Data
5. Segmentation Processing Efficiency: Approximately 20 entries per minute under i5-7300HQ + 8GB RAM conditions
6. Parallelization Module: Has been supported.

## How_to_use
1. Using PyPI
```shell
pip install pkuseg
```
2. Chinese Mirror source
```shell
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pkuseg
```
3. From github
```shell
python setup.py build_ext -i
```
The GitHub code does not include pre-trained models, so users need to download or train the models themselves. Pre-trained models can be found at [release](https://github.com/lancopku/pkuseg-python/releases). When using the models, set "model_name" to the model file.

**Note**: Installation methods 1 and 2 currently only support Python 3 versions on Linux (Ubuntu), Mac, and Windows 64-bit. For other systems, please use installation method 3 for local compilation and installation.


## Test_Sample

InPut：

| No | Name | Original Sequence |
|:--:| :--------: | :-----: |
| 1  |     孙凌云 |  南京大学医学院附属鼓楼医院风湿免疫科 |
| 2  |    李向培|  安徽医科大学附属省立医院风湿免疫科,合肥,230001 |

OutPut：

| Postal Code | Confidence | Province |City | Hospital Department | Hospital Name |
|:----:| :--------: | :-----: |:-----: | :--------: | :-----: |
|无    |2|  无 | 推断为：南京   | 风湿免疫科 |南京大学医学院附属鼓楼医院|
|230001|1|安徽|合肥 |风湿免疫科|安徽医科大学附属省立医院 |

## File_Explanation

1. [Fun_1.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_1.py)
Main Function for String Processing, Complete Program Functionality and Application
2. [Fun_2_Excl.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_2_Excl.py)
Methods for Handling Excel Documents
3. [Fun_3.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_3.py)
Standalone Testing for Small-Scale Segmentation Using pkuseg
4. [Test_Parallel.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Test_Parallel.py)
Parallel Module Development (Completed)
5. [Fun_5.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_5.py)
Reference for Parallel Principle Module, Deprecated, Only for Archival Purposes
6. [Fun_6.py](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/GSK_Module_1/Fun_6.py)
Testing Parallel Methods Implemented Using Process Pool
7. [Address.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Address.xlsx)
Data to be Processed
8. [Postal_Code_Data.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Postal_Code_Data.xlsx)
Postal Code Mapping Table
9. [Actual_Demo_1.xlsx](https://github.com/yingjiaxuan/Simon/blob/GSK_Intern/Excel/Actual_Demo_1.xlsx)
Output Results Based on 7

## All_in_All
For any questions or suggestions regarding this program, please feel free to email: [yingjiaxuan123@gmail.com](link)