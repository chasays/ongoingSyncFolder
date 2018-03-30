# -*- coding:UTF-8 -*-

import os
import time
import logging
import win32file
import win32con

import logging.handlers

LOG_FILE = r'D:\Package\monitor.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter
logger = logging.getLogger('monitor')  # 获取名为的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)
# #检测当前目录下所有文件删除、更新、修改等变化。更新日志输出到桌面。

MOUNTDISK = 'V:'  # where is mount.
ACTIONS = {
    1: "Created",
    2: "Deleted",
    3: "Updated",
    4: "Renamed from something",
    5: "Renamed to something"
}
# Thanks to Claudio Grondi for the correct set of numbers
FILE_LIST_DIRECTORY = 0x0001
path_to_watch = "{}\\".format(MOUNTDISK)
hDir = win32file.CreateFile(
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)


def isMountServer():
    ret = os.system("net use {}".format(MOUNTDISK))
    if 'successfully' not in ret:
        command = r'net use {} \\hifhwsat02\updates\Subaru\MainMedia'.format(MOUNTDISK)
        os.system(command)


# Sync folder for implementing
def monitorStatus():
    #
    # ReadDirectoryChangesW takes a previously-created
    #  handle to a directory, a buffer size for results,
    #  a flag to indicate whether to watch subtrees and
    #  a filter of what changes to notify.
    #
    # NB Tim Juchcinski reports that he needed to up
    #  the buffer size to be sure of picking up all
    #  events when a large number of files were
    #  deleted at once.
    #
    results = win32file.ReadDirectoryChangesW(
        hDir,
        1024,
        True,
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
        win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
        win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
        win32con.FILE_NOTIFY_CHANGE_SIZE |
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
        win32con.FILE_NOTIFY_CHANGE_SECURITY,
        None,
        None
    )
    slptime = 3
    logging.info('Sleep {} seconds....'.format(slptime))
    time.sleep(slptime)
    return results


def sync():
    for action, file in monitorStatus():
        full_filename = os.path.join(path_to_watch, file)
        logging.info('{}, {}'.format(full_filename, ACTIONS.get(action, "Unknown")))
        cmd = r'xcopy {} "D:\Package\" /s/h/e/k/f/c/y'.format(full_filename, full_filename[-8:])
        runXcopy = os.system(cmd)
        logging.debug(runXcopy)
        # with open('%UserProfile%\\fileupdate.txt', 'a') as f:
        #     f.write(','.join(['%s' % full_filename, '%s\n' % ACTIONS.get(action, "Unknown")]))
        #     f.close()


if __name__ == '__main__':
    sync()
