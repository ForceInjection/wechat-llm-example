import os
import re
import requests
from cgi import parse_header
from bs4 import BeautifulSoup
from typing import Tuple
from .process_article import format_whitespaces, judge_line_sep, convert_markdown_table

# 检查 URL 是否可访问
def check_url(url):
    try:
        # 发送 HEAD 请求，获取 URL 的响应
        response = requests.head(url, timeout=10)
        
        # 判断返回状态码是否是 2xx (表示请求成功)
        if response.status_code // 100 == 2:
            return True
        else:
            print(f"URL {url} 不可访问，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        # 捕获请求中的异常
        print(f"请求过程中发生错误: {e}")
        return False

# 格式化文件名为标题（移除扩展名并替换空格为下划线）
def format_article_title(file_name: str) -> str:
    # 去除文件扩展名
    file_name, _ = os.path.splitext(file_name)
    file_name = file_name.strip()  # 去除前后的空格
    file_name = format_whitespaces(file_name)  # 格式化空格
    file_name = re.sub(r'\s', '_', file_name)  # 将空格替换为下划线
    return file_name

# 处理原始文章内容，将 HTML 转换为 Markdown 格式
def process_markdown_content(raw_content: str) -> str:
    # 判断原始内容的换行符类型
    line_sep = judge_line_sep(raw_content)
    
    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(raw_content, 'html.parser')
    
    # 查找 HTML 中的所有表格
    tables = soup.find_all('table')
    
    # 将每个 HTML 表格转换为 Markdown 格式
    for table in tables:
        markdown_table = convert_markdown_table(str(table), line_sep)  # 转换表格为 Markdown
        table.replace_with(BeautifulSoup(markdown_table, 'html.parser'))  # 替换原 HTML 表格为 Markdown 表格
    
    # 返回转换后的文章内容
    return str(soup)

# 获取文章内容
def get_article_content(server_url: str, article_url: str) -> Tuple[str, str]:
    print(f"Attempting to fetch article from URL: {article_url}")

    # 如果 article_url 不可达，直接返回空字符串
    if not check_url(article_url):
        print(f"Error: Article URL {article_url} is unreachable or invalid.")
        return "", ""
    
    # 拼接 URL，参考：https://github.com/fengxxc/wechatmp2markdown
    url = f"{server_url}?url={article_url}&image=url"
    print(f"Constructed URL: {url}")  # 打印下载服务的完整 URL
    
    try:
        # 发起 GET 请求获取文章内容
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出异常
        print(f"Successfully fetched content from {article_url}.")
        
        # 从响应头中解析文件名
        _, params = parse_header(response.headers.get('content-disposition'))
        # 处理文件名中的编码问题
        file_name = params.get('filename', 'article_raw.md')
        file_name = file_name.encode('raw_unicode_escape').decode('utf-8')  # 防止编码问题
        title = format_article_title(file_name)  # 格式化文件名作为文章标题
        
        # 如果格式化后的标题为空，使用默认标题
        if len(title) == 0:
            print("Warning: Formatted title is empty, using default title.")
            title = 'article'
        
        # 获取文章内容
        raw_content = response.text

        # 打印文章内容的长度
        print(f"Fetched content length: {len(raw_content)} characters.")
        
        # 返回标题和处理过的文章内容
        return title, process_markdown_content(raw_content)
    
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch content from {article_url}: {e}")
        return "", ""