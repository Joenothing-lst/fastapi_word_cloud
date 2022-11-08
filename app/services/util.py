import datetime
import time
import uuid
from typing import Union

from dateutil.parser import parse


def stamp2date(timestamp: Union[str, int, float] = None, format="%Y-%m-%d %H:%M:%S"):
    """
    将时间戳转为标准日期输出

    :param timestamp: 时间戳
    :param format: 格式化字符串
    :return: str
    """
    if not timestamp:
        timestamp = time.time()
    return time.strftime(format, time.localtime(float(timestamp)))


def timestr2date(timestr=None, format="%Y-%m-%d %H:%M:%S"):
    """
    将时间字符串转为标准日期输出

    :param timestr: 时间字符串
    :param format: 格式化字符串
    :return:
    """
    if timestr and timestr.strip():
        return parse(timestr).strftime(format)
    else:
        return stamp2date(format=format)


def timestr2stamp(timestr=None) -> float:
    """
    将时间字符串转为时间戳输出

    :param timestr:
    :return:
    """
    return time.mktime(time.strptime(timestr2date(timestr), '%Y-%m-%d %H:%M:%S'))


def get_delay_date(days: Union[int, float] = 0, timestr=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
    """
    获取指定推迟后的日期时间

    :param days: 推迟天数
    :param timestr: 指定日期，默认为今天
    :param format: 格式化结果
    :param kwargs: 可选【seconds，minutes，hours，week，...】
    :return:
    """
    if not timestr:
        timestr = stamp2date()
    return (parse(timestr) + datetime.timedelta(days=days, **kwargs)).strftime(format)


def get_uuid4():
    return str(uuid.uuid4()).replace('-', '')
