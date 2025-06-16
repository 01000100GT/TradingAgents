# googlenews_utils.py
#
# 该文件包含用于从 Google News 抓取新闻数据的工具函数。
# 它实现了重试逻辑以处理速率限制，并支持按查询和日期范围进行搜索。
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """
    检查响应是否指示了速率限制（状态码 429）。
    Args:
        response: HTTP 响应对象。
    Returns:
        bool: 如果响应状态码为 429，则为 True，否则为 False。
    """
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """
    使用重试逻辑进行请求，以处理速率限制。
    在每次请求前添加随机延迟以避免检测。
    Args:
        url (str): 请求的 URL。
        headers (dict): 请求头。
    Returns:
        requests.Response: HTTP 响应对象。
    """
    # 每次请求前随机延迟以避免检测
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    抓取给定查询和日期范围的 Google 新闻搜索结果。
    Args:
        query (str): 搜索查询字符串。
        start_date (str): 开始日期，格式为 YYYY-MM-DD 或 MM/DD/YYYY。
        end_date (str): 结束日期，格式为 YYYY-MM-DD 或 MM/DD/YYYY。
    Returns:
        list: 包含新闻结果字典的列表。
    """
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    while True:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            results_on_page = soup.select("div.SoaBEf")

            if not results_on_page:
                break  # 未找到更多结果

            for el in results_on_page:
                try:
                    link = el.find("a")["href"]
                    title = el.select_one("div.MBeuO").get_text()
                    snippet = el.select_one(".GI74Re").get_text()
                    date = el.select_one(".LfVVr").get_text()
                    source = el.select_one(".NUnG9d span").get_text()
                    news_results.append(
                        {
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "date": date,
                            "source": source,
                        }
                    )
                except Exception as e:
                    print(f"处理结果时出错: {e}")
                    # 如果其中一个字段未找到，则跳过此结果
                    continue

            # 使用当前抓取的结果数量更新进度条

            # 检查"下一页"链接（分页）
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"多次重试后失败: {e}")
            break

    return news_results
