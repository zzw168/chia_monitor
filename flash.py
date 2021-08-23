import os

def flash():
    my_list =[]
    for path, dir_list, file_list in os.walk("c:\\a1"):
        print(dir_list)
        for i in dir_list :
            f =open('a.txt','a')
            f.write('  - %s\%s\%s'%(path,i,'261398126'))
            f.write('\n')
            f.close()
        # for dir_name in dir_list:
            # print(dir_name)
        #     print(os.path.join(path, dir_list))
        break

if __name__ == '__main__':
    # print('ok')
    flash()