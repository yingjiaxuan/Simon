import re
import pkuseg

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

def func_parallel_processor(source_url):
    if __name__ == '__main__':  # 并行化模块
        pkuseg.test(source_url,
                    'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\output.txt', \
                    model_name="medicine", postag=True, nthread=20)


source_url = 'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Address_1.txt'
goal_url = 'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Address_goal.txt'
file_object = open(source_url,encoding='UTF-8-sig')
file_goal   = open(goal_url,'a',encoding='UTF-8-sig')
file_goal.truncate()
try:
    for line in file_object:
        tem, Postal_Code = func_Get_Postal_Code(line)#line带"\n"
        tem = func_Delete_Comma(tem)
        file_goal.write(tem+'\n')
        #print (Postal_Code,'-----',tem)
finally:
     file_object.close()
     file_goal.close()

print('world')

if __name__ == '__main__':
    pkuseg.test(goal_url,
                'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\output.txt', \
                model_name="medicine", postag=True, nthread=10)

print ('hello')
