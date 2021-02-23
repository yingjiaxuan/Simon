from multiprocessing import Process
import os
import pkuseg


# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))

def func_parallel_processor():
    if __name__ == '__main__':  # 并行化模块
        pkuseg.test('C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\Address_goal.txt',
                    'C:\Personal_File\DiskF\GSK_Intern\Gsk_Inf\output.txt', \
                    model_name="medicine", postag=True, nthread=10)

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Process(target=func_parallel_processor(), args=('test',))
    print('Child process will start.')
    p.start()
    if p.is_alive():
        print('Process: %s is running' % p.pid)
    p.join()
    print('Child process end.')