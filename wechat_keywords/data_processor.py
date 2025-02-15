import os
import argparse
import re
import csv
import random
import time
from api import OpenAIApi, OllamaApi
from keywords import extract_by_llm
from keywords import classify_by_llm

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
            for field in ['category', 'keywords']:
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

# 获取 result 文件名
def get_result_path(csv_path):
    """
    根据原始文件路径生成结果文件路径
    :param csv_path: 原始 CSV 文件路径
    :return: 结果 CSV 文件路径
    """
    base, ext = os.path.splitext(csv_path)
    return base + '_result' + ext

# 处理文章内容
def data_process(base_path: str, csv_file_name: str, api_type: str, api_url: str, api_key: str, llm_model: str, keyword_count: int) -> None:
    """
    处理文章内容并提取关键词。
    
    参数：
    article_path (str): 文章文件的路径。
    api_type (str): 使用的 LLM API 类型（'openai' 或 'ollama'）。
    api_url (str): LLM API 的 URL。
    api_key (str): LLM API 的 API 密钥。
    llm_model (str): 要使用的 LLM 模型。
    keyword_count (int): 需要提取的关键词数量。
    """

    # 1. 根据 api_type 选择对应的 LLM API 实例
    if api_type == 'openai':
        llm_api = OpenAIApi(api_url, api_key, llm_model)
    elif api_type == 'ollama':
        llm_api = OllamaApi(api_url, llm_model)
    else:
        print(f"Unsupported LLM API type: {api_type}")
        exit(1)

    # 2. 输入文件的绝对路径
    csv_path = os.path.join(base_path, csv_file_name)

    # 2. 动态生成结果文件路径，用于记录执行结果
    result_path = get_result_path(csv_path)

    # 3. 合并原始文件和结果文件（如果存在）,这种一般是执行一半退出，而没有将结果合并到输入文件中
    merge_results(csv_path, result_path)

    # 打开原始文件进行处理
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # 读取 CSV 文件中的每一行
        fieldnames = reader.fieldnames  # 获取 CSV 文件的列名

        # 如果原始文件中没有某些字段，添加到 fieldnames 中
        for field in ['category', 'keywords']:
            if field not in fieldnames:
                fieldnames.append(field)
        try:
        # 打开结果文件进行写入
            with open(result_path, 'a', newline='', encoding='utf-8') as resultfile:
                writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
                # 先写入 header
                writer.writeheader()
                # 逐行读取 CSV 中的每一行
                for row in reader:
                    # 获取每一行中的 article_url, 作为 ID
                    article_url = row['article_url']  # 
                    # 获取当前行的 category
                    category = row.get('category', '')
                    # 获取当前行的 keywords
                    keywords = row.get('keywords', '')  

                    # 提取文章 URL 中的文章 ID（例如：https://mp.weixin.qq.com/s/kXAQdC0xxVQqfljamNPTQQ 最后一部分）
                    match = re.search(r"s/([^/]+)", article_url)
                    article_id = match.group(1) if match else ''

                    # 拼装 texified 路径
                    texified_path = os.path.join(base_path, f"{article_id}_texified.md")

                    # 如果 category 为空
                    if not category:
                        print(f"Start text classification of {article_url}...")
                        # 打开文件并读取内容
                        with open(texified_path, 'r', encoding='utf-8') as file:
                            texified_content = file.read()

                        # 调用 LLM API 分类
                        try:
                            category = classify_by_llm(texified_content, llm_api)
                        except Exception as e:
                            print(f"An error occurred while classifying text: {e}")
                            category = ""
                        
                        print(f"Tag extracted: {category}")

                        # 如果分类成功
                        if category:
                            row['category'] = category  # 更新 category
                        else:
                            row['category'] = ""
                    else:
                        # 如果文章已经下载过，跳过此行
                        print(f"Skipping {article_url}, already processed.")

                    # 使用 LLM API 提取关键词
                    if category and category != 'none' and not keywords:
                        # 调用 LLM API 分类
                        try:
                            keywords = extract_by_llm(texified_content, keyword_count, llm_api)
                        except Exception as e:
                            print(f"An error occurred while extracting keywords from text: {e}")
                            keywords = ""

                        print(f"Keywords extracted: {keywords}")
                        
                        #如果提取关键字成功
                        if keywords:
                            row['keywords'] = f'"{keywords}"'  # 转义
                        else:
                            row['keywords'] = ""
                    
                    # 写入更新后的行到结果文件
                    writer.writerow(row)
                    resultfile.flush()
                    
                     # 随机休眠 1 到 5 秒之间
                    sleep_time = random.randint(1, 5)
                    print(f"Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)

        except FileNotFoundError:
            print(f"Error: The texified file '{csv_path}' does not exist. Skipping...")
        except Exception as e:
            print(f"An error occurred while reading '{csv_path}': {e}")

    # 合并结果文件
    merge_results(csv_path, result_path)

# 主程序入口
def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="Process an article and extract keywords using a specified LLM API.")
    
    #添加命令参数
    parser.add_argument('--base_path', type=str, required=True, help="Base path of csv file.")
    parser.add_argument('--csv_file_name', type=str, required=True, help="Csv file name.")
    parser.add_argument('--api_type', type=str, required=True, choices=['openai', 'ollama'], help="LLM API type to use.")
    parser.add_argument('--api_url', type=str, required=True, help="URL of the LLM API.")
    parser.add_argument('--api_key', type=str, required=True, help="API key for the LLM API.")
    parser.add_argument('--llm_model', type=str, required=True, help="Model to use with the LLM API.")
    parser.add_argument('--keyword_count', type=int, required=False, default=3, help="Number of keywords to extract (default: 3).")
    
    # 解析命令行参数
    args = parser.parse_args()

    # 调用数据处理函数
    data_process(args.base_path, args.csv_file_name, args.api_type, args.api_url, args.api_key, args.llm_model, args.keyword_count)

# 程序执行入口
if __name__ == "__main__":
    main()
