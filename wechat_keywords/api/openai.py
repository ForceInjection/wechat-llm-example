from openai import OpenAI
from typing import Callable
from .base import LLMApi, same

class OpenAIApi(LLMApi):
    """
    一个与 OpenAI API 交互的类，继承自 LLMApi。
    
    方法：
    - generate(prompt: str, handle_output: Callable[[str], str]) -> str: 向 OpenAI API 发送请求并处理响应。
    """
    
    def __init__(self, base_url: str, api_key: str, model: str):
        """
        初始化 OpenAIApi 实例，配置 OpenAI 客户端。

        参数：
        base_url (str): OpenAI API 的基础 URL（如：https://api.openai.com）。
        api_key (str): 用于访问 OpenAI API 的密钥。
        model (str): 使用的 OpenAI 模型名称或 ID（如：`gpt-3.5-turbo`）。
        """
        super().__init__(api_url=base_url, api_key=api_key, model=model)
        self._client = OpenAI(base_url=base_url, api_key=api_key)  # 创建 OpenAI 客户端实例
        self._model = model  # 模型名称，指定要使用的 OpenAI 模型
    
    def generate(self, prompt: str, handle_output: Callable[[str], str] = same) -> str:
        """
        向 OpenAI API 发送生成请求，并处理输出。

        参数：
        prompt (str): 向模型发送的提示文本。
        handle_output (Callable[[str], str], 可选): 用于处理 API 输出的回调函数，默认使用 `same` 函数。

        返回：
        str: 处理后的模型输出。
        """
        # 向 OpenAI 客户端发送请求，获取响应
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {'role': 'user', 'content': prompt} # 将提示作为用户的消息发送
            ],  
            stream=False
        )

        # 使用回调函数处理响应内容并返回
        return handle_output(response.choices[0].message.content)