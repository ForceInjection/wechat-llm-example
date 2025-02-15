import os
import re
import argparse
import csv
import datetime
import random
import time
from download import get_article_content, process_wechat_article

# 保存内容到指定文件
def save_content(content: str, dir: str, file: str) -> None:
    """
    保存文章内容到指定的目录和文件中

    :param content: 文章内容
    :param dir: 目标目录
    :param file: 文件名
    """
    try:
        # 如果目录不存在，则创建目录
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        # 生成完整的文件路径
        file_path = os.path.join(dir, file)
        
        # 将内容写入指定文件
        with open(file_path, 'w', encoding='utf-8') as f_content:
            f_content.write(content)
        print(f"Document '{file}' saved to '{dir}'.")
    except Exception as e:
        print(f"Error saving document '{file}': {e}")

# 下载并处理公众号文章
def download_article(downloader_url: str, article_url: str, save_dir: str, save_processed: bool) -> bool:
    """
    下载并处理微信公众号文章

    :param downloader_url: 文章下载器 URL
    :param article_url: 文章 URL
    :param save_dir: 保存文章的目录
    :param save_processed: 是否保存处理后的文章（Texify 和 Purify）
    :return: raw_filename（下载的原始文件名）和下载时间（字符串）
    """
    # 获取文章内容和标题
    title, content = get_article_content(downloader_url, article_url)

    # 如果文章标题或内容为空，返回错误
    if not title or not content:
        print(f"Error: Failed to retrieve article: {article_url}")
        return None, None, None

    # 提取文章 URL 中的文章 ID（例如：https://mp.weixin.qq.com/s/kXAQdC0xxVQqfljamNPTQQ 最后一部分）
    match = re.search(r"s/([^/]+)", article_url)
    article_id = match.group(1) if match else title
    
    # 保存原始内容到文件
    raw_filename = f"{article_id}_raw.md"
    save_content(content, save_dir, raw_filename)
    
    # 处理文章内容（Texify 和 Purify）
    texified_content, purified_content = process_wechat_article(content)
    
    # 根据 `save_processed` 参数决定是否保存处理后的内容
    if save_processed:
        save_content(texified_content, save_dir, f"{article_id}_texified.md")
        save_content(purified_content, save_dir, f"{article_id}_purified.txt")

    # 返回 文章名称，raw_filename 和下载时间
    return title, raw_filename, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 获取 result 文件名
def get_result_path(csv_path):
    """
    根据原始文件路径生成结果文件路径
    :param csv_path: 原始 CSV 文件路径
    :return: 结果 CSV 文件路径
    """
    base, ext = os.path.splitext(csv_path)
    return base + '_result' + ext

# 合并 csv 文件
def merge_results(input_file, result_file):
    """
    合并原始 CSV 文件和结果 CSV 文件。直接将结果文件的内容合并到原始文件中，
    然后清空结果文件。
    :param input_file: 原始 CSV 文件
    :param result_file: 结果 CSV 文件
    """
    # 检查结果文件是否存在
    if os.path.exists(result_file):
        with open(result_file, 'r', newline='', encoding='utf-8') as resultfile:
            reader = csv.DictReader(resultfile)
            result_data = {row['article_url']: row for row in reader}

        # 读取原始 CSV 文件
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            # 如果原始文件中没有某些字段，添加到 fieldnames 中
            for field in ['raw_filename', 'download_time', 'article_name']:
                if field not in fieldnames:
                    fieldnames.append(field)

            original_data = [row for row in reader]

            # 更新原始数据为结果文件中的内容
            for row in original_data:
                if row['article_url'] in result_data:
                    row.update(result_data[row['article_url']])  # 更新已有数据

        # 写入合并后的内容到原始文件
        with open(input_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头
            writer.writerows(original_data)  # 写入更新后的数据

        # 清空结果文件
        open(result_file, 'w').close()

#处理 CSV 文件（文件列表，需要能够多次执行）
def process_csv(csv_path, downloader_url, save_dir, save_processed):
    """
    处理 CSV 文件，逐行下载并更新 CSV 中的文章信息，日志实时保存到结果文件。
    :param csv_path: 原始 CSV 文件路径
    :param downloader_url: 文章下载器 URL
    :param save_dir: 保存下载文件的目录
    :param save_processed: 是否保存处理后的文章
    """
    # 动态生成结果文件路径
    result_path = get_result_path(csv_path)

    # 合并原始文件和结果文件（如果存在）
    merge_results(csv_path, result_path)

    # 打开原始文件进行处理
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # 读取 CSV 文件中的每一行
        fieldnames = reader.fieldnames  # 获取 CSV 文件的列名

        # 如果 CSV 文件没有 'raw_filename' 或 'download_time' 列，添加这些列
        if 'raw_filename' not in fieldnames:
            fieldnames.append('raw_filename')
        if 'download_time' not in fieldnames:
            fieldnames.append('download_time')
        if 'article_name' not in fieldnames:
            fieldnames.append('article_name')

        # 打开结果文件进行写入
        with open(result_path, 'a', newline='', encoding='utf-8') as resultfile:
            writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
            # 先写入 header
            writer.writeheader()

            # 逐行读取 CSV 中的每一行
            for row in reader:
                article_url = row['article_url']  # 获取每一行中的 article_url
                raw_filename = row.get('raw_filename', '')  # 获取当前行的 raw_filename
                title = row.get('article_name', '')  # 获取当前行的 article_name（文件名）

                # 如果 raw_filename 为空、显示为 "Failed" 或 title 为空
                if not raw_filename or raw_filename == "Failed" or title == ".md":
                    print(f"Downloading article from {article_url}...")

                    # 下载并获取文章的文件名和下载时间
                    title, raw_filename, download_time = download_article(downloader_url, article_url, save_dir, save_processed)

                    # 如果下载成功，更新文件名和下载时间
                    if raw_filename:
                        row['raw_filename'] = raw_filename  # 更新 raw_filename
                        row['download_time'] = download_time  # 更新 download_time
                        row['article_name'] = title  # 更新 article_name（标题）
                    else:
                        # 如果下载失败，标记为下载失败
                        row['raw_filename'] = "Failed"
                        row['download_time'] = "N/A"
                        row['article_name'] = "N/A"

                    # 随机休眠 1 到 5 秒之间
                    sleep_time = random.randint(1, 5)
                    print(f"Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    # 如果文章已经下载过，跳过此行
                    print(f"Skipping {article_url}, already downloaded.")

                # 写入更新后的行到结果文件
                writer.writerow(row)
                resultfile.flush()

    # 合并结果文件
    merge_results(csv_path, result_path)

# 主程序入口
def main():
    """
    解析命令行参数并执行下载和处理任务
    """
    # 配置命令行参数解析器
    parser = argparse.ArgumentParser(description='Batch download and process WeChat articles from a CSV file.')
    
    # 添加命令行参数
    parser.add_argument('--downloader-url', type=str, required=True, help='WeChat article downloader URL.')
    parser.add_argument('--csv-file', type=str, required=True, help='Path to the CSV file containing article URLs.')
    parser.add_argument('--dir', type=str, required=True, help='Directory to save the downloaded articles.')
    parser.add_argument('--save-processed', action='store_true', help='Save the processed article in Markdown and Text format.')

    # 解析命令行参数
    args = parser.parse_args()

    # 处理 CSV 文件，下载并更新 CSV 文件
    process_csv(args.csv_file, args.downloader_url, args.dir, args.save_processed)

# 程序执行入口
if __name__ == "__main__":
    main()