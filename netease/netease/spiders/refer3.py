import sys
import os
from zipfile import ZipFile
import shutil


def unzip(file_path):
    myzip = ZipFile(file_path)
    for name in myzip.namelist():
        filename = name.encode('cp437').decode('gbk')
        myzip.extract(name)
        try:
            os.rename(name, filename)

        except FileExistsError:
            os.remove(filename)
            os.rename(name, filename)


def copy_all(source, destination):
    z1 = destination

    for root, dir1, files1 in os.walk(source):
        for o1 in dir1:
            full_dirs = os.path.join(root, o1)
            relative_paths = full_dirs.replace(source, '')
            current_dirs = z1 + relative_paths
            try:
                os.makedirs(current_dirs)
            except FileExistsError:
                pass

        now_dirs = z1 + root.replace(source, '')
        for t0 in files1:
            shutil.copy(os.path.join(root, t0), now_dirs + '/' + t0)


def write_packages(s):
    dirs = [x for x in sys.path if x.endswith('site-packages')]
    if os.path.exists(dirs[0]+'/a.pth'):
        pass
    else:
        print('正在解压依赖包')
        unzip('site-packages.zip')
        print('正在复制依赖包')
        copy_all('site-packages', dirs[0])
        #os.remove('site-packages.zip')
        with open(dirs[0]+'/a.pth', 'w', encoding='utf-8') as f:

            f.write(s)
            f.write(s[:-16])


def delete_packages(path):
    for x, y, z in os.walk(path):
        for t in z:
            os.remove(os.path.join(x, t))

    def remove(a):
        print(a)
        if len(os.listdir(a)) > 0:
            for x1 in os.listdir(a):
                remove(os.path.join(a, x1))
            os.rmdir(a)
        else:
            os.rmdir(a)
    remove('site-packages')


if __name__ == '__main__':
    delete_packages('site-packages')



