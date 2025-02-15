from ollama import Client
from typing import Callable
from .base import LLMApi, same

class OllamaApi(LLMApi):
    """
    一个与 Ollama API 交互的类，继承自 LLMApi。
    
    方法：
    - generate(prompt: str, handle_output: Callable[[str], str]) -> str: 向 Ollama API 发送请求并处理响应。
    """
    
    def __init__(self, host: str, model: str):
        """
        初始化 OllamaApi 实例，连接 Ollama 客户端。

        参数：
        host (str): Ollama API 服务器的主机地址（如：`http://localhost:11411`）。
        model (str): 使用的模型名称或 ID。
        """
        super().__init__(api_url=host, api_key=None, model=model)
        self._client = Client(host=host)  # 创建 Ollama 客户端实例，连接到指定的主机
        self._model = model  # 模型名称，指定使用哪个模型
    
    def generate(self, prompt: str, handle_output: Callable[[str], str] = same) -> str:
        """
        向 Ollama API 发送生成请求，并处理输出。

        参数：
        prompt (str): 向模型发送的提示文本。
        handle_output (Callable[[str], str], 可选): 用于处理 API 输出的回调函数，默认使用 `same` 函数。

        返回：
        str: 处理后的模型输出。
        """
        # 向 Ollama 客户端发送请求，获取响应
        response = self._client.chat(
            model=self._model,
            messages=[
                {'role': 'user', 'content': prompt}
            ],  # 将提示作为用户的消息发送
            stream=False
        )

        # 使用回调函数处理响应内容并返回
        return handle_output(response.message.content)
