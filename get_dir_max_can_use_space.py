# -*-coding:utf-8-*-
import os
import sys
import ctypes


def is_win_platform():
    p_lfm = sys.platform
    if p_lfm != 'win32' and p_lfm != 'win64':
        return False
    else:
        return True


def get_free_space(folder):
    """
     Return folder/drive free space (in GB)
    :param folder: string
    :return: int
    """
    convert_gb = 1024 ** 3
    try:
        if is_win_platform():
            partition = folder[0:2]
            if not os.path.exists(partition):
                print('folder is error,not exits {}'.format(partition))

        if not os.path.exists(folder):
            os.makedirs(folder)

        if is_win_platform():
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return 'free space:{}GB'.format(free_bytes.value / convert_gb)
        else:
            st = os.statvfs(folder)
            return 'free space:{}GB'.format(st.f_bavail * st.f_frsize / convert_gb)
    except Exception as ex:
        raise ex


print(get_free_space(r'H:\jad'))