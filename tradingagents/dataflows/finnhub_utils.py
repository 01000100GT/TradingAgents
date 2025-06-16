# finnhub_utils.py
#
# 该文件包含用于从磁盘获取和处理 Finnhub 数据的工具函数。
# 主要功能是根据指定的日期范围和数据类型过滤和检索数据。
import json
import os


def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):
    """
    从磁盘获取并处理已保存的 Finnhub 数据。

    Args:
        ticker (str): 股票代码。
        start_date (str): 开始日期，格式为 YYYY-MM-DD。
        end_date (str): 结束日期，格式为 YYYY-MM-DD。
        data_type (str): 要获取的 Finnhub 数据类型。可以是 insider_trans, SEC_filings, news_data, insider_senti, 或 fin_as_reported。
        data_dir (str): 数据保存的目录。
        period (str, optional): 周期，默认为 None。如果指定，应为 "annual" 或 "quarterly"。

    Returns:
        dict: 按日期范围过滤后的数据。
    """

    if period:
        data_path = os.path.join(
            data_dir,
            "finnhub_data",
            data_type,
            f"{ticker}_{period}_data_formatted.json",
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    data = open(data_path, "r")
    data = json.load(data)

    # 根据日期范围（字符串，格式为 YYYY-MM-DD）过滤键（日期，字符串）
    filtered_data = {}
    for key, value in data.items():
        if start_date <= key <= end_date and len(value) > 0:
            filtered_data[key] = value
    return filtered_data
