from typing import Callable

class LLMApi(object):
    """
    一个简化的 LLM API 类，用于生成基于输入提示的文本输出。

    方法：
    - generate(prompt: str, handle_output: Callable[[str], str]) -> str: 发送生成请求并处理输出。
    """
    
    def __init__(self, api_url: str, api_key: str, model: str):
        """
        初始化 LLM API 类实例。

        参数：
        api_url (str): LLM API 的 URL 地址。
        api_key (str): 用于访问 LLM API 的 API 密钥。
        model (str): 使用的 LLM 模型名称或 ID。
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, handle_output: Callable[[str], str]) -> str:
        """
        发送生成请求并处理输出。

        参数：
        prompt (str): 发送给 LLM 的输入文本，通常是用户的请求或文章内容。
        handle_output (Callable[[str], str]): 用于处理 API 响应输出的回调函数。

        返回：
        str: 经过处理的输出结果。
        """
        # 在这里，我们模拟调用 LLM API（实际情况下会发送 HTTP 请求到 API 服务器）
        print(f"Sending prompt to {self.api_url} with model {self.model}...")

        # 模拟生成的模型输出，这里只是一个简单的模拟
        model_output = f"Generated response for: {prompt}"

        # 使用 `handle_output` 回调函数处理模型输出
        return handle_output(model_output)

def same(model_output: str) -> str:
    """
    一个简单的处理函数，直接返回传入的模型输出。

    参数：
    model_output (str): 模型返回的输出字符串。

    返回：
    str: 输入的原始输出字符串。
    """
    print (model_output)
    # 返回结果
    return model_output