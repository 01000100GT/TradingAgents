# tradingagents/dataflows/utils.py
# 本文件包含一些通用的实用函数，用于数据保存、日期获取以及方法装饰等。

import os
import json
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Annotated

# 定义保存路径的类型注释，表示文件保存路径，如果为 None 则不保存数据。
SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]


# 将 DataFrame 数据保存到指定路径，并打印保存信息。
def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    if save_path:
        data.to_csv(save_path)
        print(f"{tag} saved to {save_path}")


# 获取当前日期，格式为 YYYY-MM-DD。
def get_current_date():
    return date.today().strftime("%Y-%m-%d")


# 一个装饰器，用于装饰类中的所有可调用方法。
def decorate_all_methods(decorator):
    # 类的装饰器，遍历类的所有属性，如果属性是可调用对象，则用传入的装饰器装饰它。
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


# 获取给定日期的下一个工作日。如果给定日期是周末，则返回下一个周一。
def get_next_weekday(date):

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.weekday() >= 5:  # 5代表星期六，6代表星期日
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        return date
