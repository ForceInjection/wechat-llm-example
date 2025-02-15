import json
import re
from json import JSONDecodeError
from typing import List, Callable
from api.base import LLMApi, same

# 关键词提取的提示模板
_KEYWORD_PROMPT_TEMPLATE = """{
  "instruction": {
    "description": "分析提供的文章，并提取出对理解其主要内容至关重要的{count}个关键词。",
    "task_details": [
      "识别并提取文章中最重要的{count}个关键词。",
      "这些关键词应能够帮助读者快速理解文章的核心内容。"
    ],
    "input_specification": {
      "article_content": "{article}",
      "count": "{count}"
    },
    "output_requirements": {
      "format": "输出必须是一个有效的JSON数组，包含{count}个最重要的关键词。",
      "example": ["关键词1", "关键词2", "关键词3"]
    },
    "special_instructions": [
      "确保最终输出严格遵循指定的JSON格式。",
      "输出中不得包含任何额外的文本或Markdown。",
      "如果文章中的关键词不足{count}个，则返回所有找到的关键词。"
    ]
}"""

def extract_by_llm(content: str, count: int, api: LLMApi, handle_response: Callable[[str], str] = same) -> str:
    """
    使用 LLM API 提取文章中的关键词。

    参数：
    content (str): 文章内容，作为关键词提取的输入。
    count (int): 需要提取的关键词数量。
    api (LLMApi): LLM API 实例，用于生成和处理提示。
    handle_response (Callable[[str], str], 可选): 用于处理 API 响应的回调函数，默认使用 `same` 函数。

    返回：
    List[str]: 提取的关键词列表。如果解析失败，则返回空列表。
    """
    # 使用 json.dumps 对 content 进行转义
    escaped_content = json.dumps(content)

    # 使用 format 替换占位符
    prompt = _KEYWORD_PROMPT_TEMPLATE.replace('{count}', str(count)).replace('{article}', escaped_content)
    
    # 调用 API 生成响应并处理响应
    response = api.generate(prompt, handle_response)
    
    try:
        # 尝试将响应解析为 JSON 对象（关键词数组）
        keywords = json.dumps(json.loads(re.sub(r'```json\n|\n```', '', response).strip()), ensure_ascii=False)
        # 返回解析后的关键词列表
        return keywords
    except JSONDecodeError as e:
        # 如果 JSON 解码失败，打印错误并返回空列表
        print(f"JSON decode error: {e}")
        return ""
    except TypeError as e:
        # 如果响应数据类型不正确，打印错误并返回空列表
        print(f"TypeError decoding json string: {e}")
        return ""