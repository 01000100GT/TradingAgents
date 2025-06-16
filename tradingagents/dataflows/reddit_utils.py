# reddit_utils.py
#
# 该文件提供了从 Reddit 获取社交媒体数据的工具函数。
# 它包含了将股票代码映射到公司名称的字典，并支持按类别、日期和查询获取热门帖子。
import requests
import time
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Annotated
import os
import re

# 股票代码到公司名称的映射字典
ticker_to_company = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    "TSM": "Taiwan Semiconductor Manufacturing Company OR TSMC",
    "JPM": "JPMorgan Chase OR JP Morgan",
    "JNJ": "Johnson & Johnson OR JNJ",
    "V": "Visa",
    "WMT": "Walmart",
    "META": "Meta OR Facebook",
    "AMD": "AMD",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "BABA": "Alibaba",
    "ADBE": "Adobe",
    "NFLX": "Netflix",
    "CRM": "Salesforce",
    "PYPL": "PayPal",
    "PLTR": "Palantir",
    "MU": "Micron",
    "SQ": "Block OR Square",
    "ZM": "Zoom",
    "CSCO": "Cisco",
    "SHOP": "Shopify",
    "ORCL": "Oracle",
    "X": "Twitter OR X",
    "SPOT": "Spotify",
    "AVGO": "Broadcom",
    "ASML": "ASML ",
    "TWLO": "Twilio",
    "SNAP": "Snap Inc.",
    "TEAM": "Atlassian",
    "SQSP": "Squarespace",
    "UBER": "Uber",
    "ROKU": "Roku",
    "PINS": "Pinterest",
}


def fetch_top_from_category(
    category: Annotated[str, "要获取热门帖子的类别。子版块的集合。"],
    date: Annotated[str, "要获取热门帖子的日期。"],
    max_limit: Annotated[int, "要获取的最大帖子数量。"],
    query: Annotated[str, "要在子版块中搜索的可选查询。"] = None,
    data_path: Annotated[
        str,
        "数据文件夹的路径。默认为 'reddit_data'。",
    ] = "reddit_data",
):
    """
    从指定类别和日期获取热门 Reddit 帖子。

    Args:
        category (str): 要获取热门帖子的类别（子版块集合）。
        date (str): 要获取热门帖子的日期。
        max_limit (int): 要获取的最大帖子数量。
        query (str, optional): 可选的搜索查询，用于在子版块中搜索。
        data_path (str, optional): 数据文件夹的路径。默认为 'reddit_data'。

    Returns:
        list: 包含热门帖子字典的列表。
    """
    base_path = data_path

    all_content = []

    if max_limit < len(os.listdir(os.path.join(base_path, category))):
        raise ValueError(
            "REDDIT FETCHING ERROR: max limit is less than the number of files in the category. Will not be able to fetch any posts"  # Reddit获取错误：最大限制小于类别中的文件数量。将无法获取任何帖子
        )

    limit_per_subreddit = max_limit // len(
        os.listdir(os.path.join(base_path, category))
    )

    for data_file in os.listdir(os.path.join(base_path, category)):
        # 检查 data_file 是否为 .jsonl 文件
        if not data_file.endswith(".jsonl"):
            continue

        all_content_curr_subreddit = []

        with open(os.path.join(base_path, category, data_file), "rb") as f:
            for i, line in enumerate(f):
                # 跳过空行
                if not line.strip():
                    continue

                parsed_line = json.loads(line)

                # 只选择来自指定日期的行
                post_date = datetime.utcfromtimestamp(
                    parsed_line["created_utc"]
                ).strftime("%Y-%m-%d")
                if post_date != date:
                    continue

                # 如果是 company_news，检查标题或内容是否提及公司名称（查询）
                if "company" in category and query:
                    search_terms = []
                    if "OR" in ticker_to_company[query]:
                        search_terms = ticker_to_company[query].split(" OR ")
                    else:
                        search_terms = [ticker_to_company[query]]

                    search_terms.append(query)

                    found = False
                    for term in search_terms:
                        if re.search(
                            term, parsed_line["title"], re.IGNORECASE
                        ) or re.search(term, parsed_line["selftext"], re.IGNORECASE):
                            found = True
                            break

                    if not found:
                        continue

                post = {
                    "title": parsed_line["title"],
                    "content": parsed_line["selftext"],
                    "url": parsed_line["url"],
                    "upvotes": parsed_line["ups"],
                    "posted_date": post_date,
                }

                all_content_curr_subreddit.append(post)

        # 按点赞数降序排序当前子版块的所有内容
        all_content_curr_subreddit.sort(key=lambda x: x["upvotes"], reverse=True)

        all_content.extend(all_content_curr_subreddit[:limit_per_subreddit])

    return all_content
