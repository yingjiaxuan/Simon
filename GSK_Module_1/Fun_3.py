# location_str = ["新疆维吾尔自治区人民医院风湿科", "复旦大学附属华山医院皮肤科,上海,200040", "北京大学人民医院风湿免疫科"]
# import cpca
# df = cpca.transform(location_str, pos_sensitive=True,cut=False)#默认情况下参数为True,可以选择换为False，可以给一个umap的字典映射
# # for i in range(3):
# #     for j in range (3):
#
# print(df)
# print(df.iloc[0,3])
# print(df.iloc[1,3])
# print(df.iloc[2,3])

# from cpca import drawer
# #df为上一段代码输出的df
# drawer.draw_locations(df, "C:\Personal_File\DiskF\GSK_Intern\Location_Pic\df.html")
#***************************以上为功能测试部分*****************以下为文件测试部分************************

t1 = '复旦大学附属华山医院皮肤科,上海,200040'#完成——医院名字不含地名，地址信息在最后
t2 = '华中科技大学同济医学院附属同济医院风湿免疫科,武汉,430030'#完成，同上，且只有城市名
t3 = '鲁中冶金矿业总公司  医院儿科,山东省莱芜市'#完成——医院名字不含地名，省市信息在最后
t4 = '中国医科大学附属第一医院皮肤科,沈阳,110001'#以上四类为同一类——即医院名称不会进入地名判断

t5 = '梅州市人民医院,广东,梅州,514032'#未完成，医院名称含有地名（绝大部分），且字符串末尾有地名
t5_1 = '210042,南京,中国医学科学院、中国协和医科大学皮肤病研究所'
t5_2 = '400038,重庆,第三军医大学西南医院皮肤科'#5.1,5.2已完成
t5_3 = '安徽医科大学附属省立医院风湿免疫科,合肥,230001'
t6 = '江苏省淮安市第一人民医院免疫风湿科'#未完成，医院名称含有地名，且字符串末尾无地名
t7 = '新疆维吾尔自治区人民医院风湿科'#新疆特殊，和上一同类
t8 = '广西医科大学第一附属医院皮肤性病科,南宁,530021'
t9 = '香港玛丽医院儿童及青少年医学系'

t10 = '南京军区南京总医院肾脏科国家肾脏疾病临床医学研究中心全军肾脏病研究所 南京,210016'
t11 = '南方医科大学生物技术学院输血医学系广东广州510515'

t12 = '云南省红十字会医院眼科昆明'

t13 = '中南大学湘雅医院皮肤科湖南长沙410008'
t14 = '安徽医科大学公共卫生学院流行病与卫生统计学系,合肥,230032'
t15 = '天津医科大学总医院感染免疫科天津'
t16 = '南京医科大学第一附属医院生殖中心'

t17 = '成都华西医科大学附属第一医院'
t18 = '北京医科大学免疫学系'#这个试试看

t19 = '解放军291医院医务处'

t20 = '五华县采血点五华'
def Pro_Fin_ADD(text):#处理句末出现的地址信息变为GG——未来会加入处理句首
    min_len = len(text)
    i = -1
    num = []
    if min_len >= 3:
        while i >= -3 and len(text[i][0]) <= 9:  # 写9完全是因为存在新疆这个超长
            if text[i][1] == 'ns' and text[i + 1][0] != '大学' and text[i + 1][0] != '医科大学' and text[i + 1][
                0] != '医学院' and \
                    text[i + 1][0] != "医院":
                # 打补丁就完事了，主要是某些需要靠名字推城市，只考虑句末
                text[i] = ('GG', 'GG')
            i = i - 1
    return text
import re

def remove_punctuation(line):
  rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
  line = rule.sub('',line)
  return line

import pkuseg
seg = pkuseg.pkuseg(model_name='medicine',postag=True)  # 程序会自动下载所对应的细领域模型
text = seg.cut('永康市第一人民医院肾内科浙江永康')              # 进行分词
print(text)
print(Pro_Fin_ADD(text))
#print(text[-4])
print(len(text),end="")



# import re
# # def func_Get_Postal_Code(text):
# #     m = re.search(r'^[\u4e00-\u9fa5_a-zA-Z0-9]+科$', t)
# #     if m == None:
# #         #print('无邮政编码')
# #         return t, m
# #     tur = m.span()
# #     s_re = t[0:tur[0]] + t[tur[1]:len(t)]
# #     return s_re, m.group(0)
# m = re.search(r'[\u4e00-\u9fa5]{1,5}科$', '阿斯顿发送到，风湿科')
# print (m)
# print (m.group(0))