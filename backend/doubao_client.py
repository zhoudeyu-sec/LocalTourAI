import httpx
import logging
import os



logger = logging.getLogger(__name__)


class DoubaoClient:
    """豆包大模型客户端（火山方舟）"""

    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY", "")
        self.endpoint_id = os.getenv("DOUBAO_ENDPOINT_ID", "")
        self.base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        print(f"🔧 初始化: API_KEY长度={len(self.api_key)}, ENDPOINT_ID={self.endpoint_id}")

    async def chat(self, question: str, system_prompt: str = None) -> str:
        """调用豆包大模型进行对话"""
        if not self.api_key or not self.endpoint_id:
            logger.warning("豆包 API 配置缺失，使用模拟回答")
            return self._mock_response(question)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": "你是景区数字人导游小景，热情友好地回答游客问题。"
                })

            messages.append({"role": "user", "content": question})

            payload = {
                "model": self.endpoint_id,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"豆包 API 调用失败: {e}")
            return self._mock_response(question)

    def _mock_response(self, question: str) -> str:
        return f"您好！关于「{question}」，我是导游小景。目前我还在学习景区知识，请稍后再试哦！😊"
