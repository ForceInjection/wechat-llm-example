import re
from typing import Tuple
from bs4 import BeautifulSoup

# 将 HTML 表格内容转换为 Markdown 格式
def convert_markdown_table(html_content: str, line_sep: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    markdown_results = ''
    
    if tables:
        # 遍历所有表格并将其转换为 Markdown 格式
        for table in tables:
            markdown_table = convert_table_element_to_markdown(table, line_sep)
            markdown_results += markdown_table + line_sep + line_sep
        return markdown_results
    return ""

# 将单个 HTML 表格元素转换为 Markdown 表格
def convert_table_element_to_markdown(table, line_sep: str) -> str:
    rows = table.find_all('tr')
    markdown_rows = [convert_table_row_element_to_markdown(row, index, line_sep) for index, row in enumerate(rows)]
    return line_sep.join(markdown_rows)

# 将单个表格行转换为 Markdown 格式
def convert_table_row_element_to_markdown(table_row, row_number: int, line_sep: str) -> str:
    cells = table_row.find_all(['td', 'th'])
    cell_texts = [cell.get_text() + ' |' for cell in cells]
    row = '| ' + ' '.join(cell_texts)
    
    # 如果是表头行，添加分隔符
    if row_number == 0:
        row += line_sep + create_markdown_divider_row(len(cells))
    
    return row

# 创建 Markdown 表格的分隔符行
def create_markdown_divider_row(cell_count: int) -> str:
    divider_cells = ['--- |' for _ in range(cell_count)]
    return '| ' + ' '.join(divider_cells)

# 判断原始内容的换行符类型
def judge_line_sep(content: str) -> str:
    if '\r\n' in content:
        return '\r\n'
    elif '\r' in content:
        return '\r'
    return '\n'

# 移除文章中的 URL（包括图片和常规链接）
def remove_url(content: str) -> str:
    # 正则匹配图片链接和普通链接，并移除
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'  # 图片链接模式
    url_pattern = r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)'  # 普通链接模式
    
    content = re.sub(image_pattern, '', content)
    content = re.sub(url_pattern, '', content)
    
    return content

# 移除订阅类文本（如“点击‘阅读原文’”）
def remove_useless_text(content: str) -> str:
    subscribtion_pattern = r'点击“阅读原文”'
    match = re.search(subscribtion_pattern, content)
    
    if match:
        # 返回“阅读原文”之前的内容
        return content[:match.start()]
    return content

# 移除无用的特殊字符，如 * | ` > # 等
def remove_special_pattern(content: str) -> str:
    special_chars = ['*', '|', '`', '>', '#', '=', '-', '$', '<', '(', ')', ';', '_']
    for ch in special_chars:
        content = content.replace(ch, ' ')
    return content

# 移除多余的空白字符，将多个空白字符替换为单一的空格
def remove_whitespace(content: str) -> str:
    return re.sub(r'\s+', ' ', content).strip()

# 格式化空格：将多个空格替换为一个空格，移除多余的换行符
def format_whitespaces(content: str) -> str:
    processed_content = re.sub(r'[ \t]+', ' ', content)  # 替换多个空格或制表符为一个空格
    processed_content = re.sub(r'[ \t]+\n', '\n', processed_content)  # 替换空格+换行符为单一换行符
    processed_content = re.sub(r'\n[ \t]+', '\n', processed_content)  # 去除换行符后的空格或制表符
    processed_content = re.sub(r'\n{3,}', '\n\n', processed_content)  # 限制最多两个换行符
    return processed_content.strip()

# 对原始文章内容进行 Texify 处理（移除 URL 和无用文本）
def texify_markdown_content(raw_content: str) -> str:
    content = remove_url(raw_content)
    content = remove_useless_text(content)
    content = format_whitespaces(content)
    return content

# 对 Texify 后的文章内容进行净化处理，移除特殊字符和多余的空白
def purify_markdown_content(texified_content: str) -> str:
    texified_content = remove_special_pattern(texified_content)
    texified_content = remove_whitespace(texified_content)
    return texified_content

# 处理微信公众号文章，返回 Texified 和 Purified 的内容
def process_wechat_article(raw_content: str) -> Tuple[str, str]:
    texified_content = texify_markdown_content(raw_content)  # 处理原始内容
    purified_content = purify_markdown_content(texified_content)  # 进一步净化内容
    return texified_content, purified_content