#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import time
import datetime

import os

from dz_utils.dz_utils import dict_set, get_current_time, time_int2str, write_json_file_breakline, dict_get, read_json_file


def get_FileSize(filePath) -> float:
    """
    获取文件的大小,结果保留两位小数, 单位为MB
    :param filePath:
    :return:
    """
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


def get_FileAccessTime(filePath):
    """
    获取文件的访问时间
    :param filePath:
    :return:
    """
    # filePath = unicode(filePath, 'utf8')

    t: float = os.path.getatime(filePath)
    return time_int2str(t, '%Y-%m-%d %H:%M:%S')


def get_FileCreateTime(filePath: str) -> str:
    """
    获取文件的创建时间
    :param filePath: 文件路径
    :return: 字符串形式描述的时间
    """
    t = os.path.getctime(filePath)
    return time_int2str(t, '%Y-%m-%d %H:%M:%S')


def get_FileModifyTime(filePath):
    """
    获取文件的修改时间
    :param filePath:
    :return:
    """
    # filePath = unicode(filePath, 'utf8')

    t = os.path.getmtime(filePath)
    return time_int2str(t, '%Y-%m-%d %H:%M:%S')


def get_str_md5(content: str):
    """
    计算字符串md5
    :param content:
    :return:
    """
    m = hashlib.md5(content)
    return m.hexdigest()


def get_file_md5(file_name) -> str:
    """
    计算文件的md5
    :param file_name:
    :return:
    """
    # 创建md5对象
    m = hashlib.md5()
    with open(file_name, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            # 更新md5对象
            m.update(data)

            # 返回md5对象
    return m.hexdigest()


def main():
    all_info: dict = {}
    config: dict = read_json_file("./config.json")
    # 需要执行检查的目录列表
    root_dir_path_list: list[str] = dict_get(config, "check_dir_path_list", [])

    # 需要忽略的目录列表
    ignore_dir_list: list[str] = dict_get(config, "ignore_dir_list", [])
    # 需要执行检查的文件后缀名类型
    suffix_name_list: list[str] = dict_get(config, "suffix_name_list", [])
    for the_dir in root_dir_path_list:
        walk(all_info, the_dir, ignore_dir_list, suffix_name_list)

    write_json_file_breakline("./file_md5_all_info.json", all_info)

    attention_info_list = []
    for the_md5, the_file_path_list in all_info.items():
        if len(the_file_path_list) > 1:
            file_size: float = get_FileSize(the_file_path_list[0])
            attention_info_list.append([the_md5, file_size, the_file_path_list])
            # dict_set(attention_info, the_md5, the_file_path_list)
    attention_info_list.sort(key=sort_key, reverse=True)
    write_json_file_breakline("./file_md5_attention_info.json", attention_info_list)


def sort_key(elem: list):
    return elem[1]


def is_need_check(file_path: str, ignore_dir_list: list[str], suffix_name_list: list[str]) -> bool:
    is_right_suffix: bool = False
    for the_suffix in suffix_name_list:
        the_suffix = str.lower(the_suffix)
        if not str.startswith(the_suffix, "."):
            # 为后缀名添加一个点
            the_suffix = "." + the_suffix

        file_path_lower = str.lower(file_path)
        # 转为小写, 便于比对
        if str.endswith(file_path_lower, the_suffix):
            is_right_suffix = True
            break

    if not is_right_suffix:
        # 如果文件后缀名不符合要求, 则不必检查
        return False

    for the_ignore_dir in ignore_dir_list:
        if str.startswith(file_path, the_ignore_dir):
            # 如果文件处于忽略目录中, 则不必检查
            return False

    # 文件后缀名符合要求, 不切不在忽略目录中, 则需要检查
    return True


def walk(all_info: dict, root_dir_path: str, ignore_dir_list: list[str], suffix_name_list: list[str]):
    for root, dirs, files in os.walk(root_dir_path):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:

            a = os.path.join(root, f)
            if not is_need_check(a, ignore_dir_list, suffix_name_list):
                # 判定不属于资源文件, 所以不必检查
                continue
            # print(a, root, f)
            # print(f"os.path.dirname(a):{os.path.dirname(a)}")
            # print(f"os.path.split(a):{os.path.split(a)}")
            the_md5: str = get_file_md5(a)
            print(f"{get_current_time()} {a}, md5:{the_md5}")

            the_md5_files_list: list = dict_get(all_info, the_md5, [])
            the_md5_files_list.append(a)


if __name__ == "__main__":
    main()
