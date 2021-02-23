import pp
import time
import pandas as pd
import Fun_1


def fun_Parallel_fun(a, b, df):
    row_loop = a
    df_goal = pd.DataFrame(columns=('ID', 'HCO', 'HCP', 'hcp_Id', 'Department'))
    while row_loop < b:
        t = str(df.loc[row_loop, 'HCO'])
        out_1, out_2 = Fun_1.fun_Processor(t)
        df_goal.loc[row_loop, 'ID'] = df.loc[row_loop, 'ID']
        df_goal.loc[row_loop, 'HCO'] = out_1
        df_goal.loc[row_loop, 'HCP'] = df.loc[row_loop, 'HCP']
        df_goal.loc[row_loop, 'hcp_Id'] = df.loc[row_loop, 'hcp_Id']
        df_goal.loc[row_loop, 'Department'] = out_2
        print("Hos:" + out_1)
        print("Dep:" + out_2)
        # print(row_loop / row_num)
        print("")
        row_loop = row_loop + 1

    t = str(a) + '_' + str(b) + '.xlsx'
    t = 'url' + t
    df_goal.to_excel(t, sheet_name='Sheet1', index=False, header=True)


# 生成输入列表
def fun_Set_Inputs(a, b, tem):
    inputs = [(loop, loop + tem) for loop in range(a, b // tem * tem, tem)]
    if b // tem != int(b / tem):
        inputs.append((b // tem * tem, b))
    if inputs[-1][1] > b:
        inputs.pop()
        inputs.append((inputs[-1][1], b))
    return inputs


if __name__ == '__main__':

    startTime = time.time()

    t = 'url'  # 开文件，录入
    df = pd.read_excel(t, sheet_name="Sheet1")
    row_num, column_num = df.shape
    print("获取完成")
    print("use: %.3fs" % (time.time() - startTime))

    print(df.shape)

    # ***********************并行部分**********************
    job_server = pp.Server()
    inputs = fun_Set_Inputs(0, 16000, 2000)  # 改这里
    jobs = []
    print("开始封装")
    for input in inputs:  # 封装
        a = job_server.submit(fun_Parallel_fun, (input[0], input[1], df,), \
                              (Fun_1.fun_Processor,), \
                              ("re", "pandas as pd", "pkuseg", "Fun_1",))
        jobs.append((input, a))
        print(jobs)
    print("封装结束")

    print("开始启动")
    for i in range(len(inputs)):  # 启动
        print(str(i) + "号进程启动")
        jobs[i][1]()
        print("use: %.3fs" % (time.time() - startTime))
    print("启动完成")

    print("拷贝并处理完成")
    print("use: %.3fs" % (time.time() - startTime))

    # a = job_server.submit(fun_Parallel_fun,(input[0],input[1],df,),\
    #                       (fun_Processor,fun_Cn_Proc,fun_En_Proc,func_Get_Postal_Code,func_Delete_Comma,fun_Cut_Str,Patch_Of_Dep,func_Get_Dep_2,Pro_Fin_ADD,func_Dele_str,print_list,Dele_GG,func_Infer_Dep_2,split_str,fun_match_En_dep,),\
    #                       ("re","pandas as pd","pkuseg",))
