import logging
import uuid
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

class TTSClient:
    def __init__(self):
        self.app_id = os.getenv("VOLC_TTS_APP_ID", "")
        self.token = os.getenv("VOLC_TTS_ACCESS_TOKEN", "")
        self.cluster = "volcano_tts"
        
        self.voice_map = {
            "ancient": "zh_female_manman",
            "modern": "zh_male_jingying",
            "cartoon": "zh_female_tianmei",
        }
        self.default_voice = "zh_female_manman"
        self.base_url = "https://openspeech.bytedance.com/api/v1/tts"

        if not all([self.app_id, self.token]):
            logger.warning("TTS 配置缺失，启用浏览器降级")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"TTS 客户端初始化成功，APP ID: {self.app_id}")

    async def synthesize(self, text: str, style: str = "ancient") -> str:
        if not self.enabled or not text.strip():
            return None

        voice = self.voice_map.get(style, self.default_voice)
        reqid = str(uuid.uuid4())

        # ✅ 严格按照官方文档：operation 放在 request 内部
        payload = {
            "app": {
                "appid": self.app_id,
                "cluster": self.cluster
            },
            "user": {
                "uid": "tourist_guide"
            },
            "audio": {
                "voice_type": voice,
                "encoding": "mp3",
                "speed_ratio": 1.0
            },
            "request": {
                "reqid": reqid,
                "text": text,
                "text_type": "plain",
                "operation": "query"  # ✅ 放这里！！！
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.token}"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                logger.info(f"TTS 状态码: {response.status_code}")
                res = response.json()

                if response.status_code == 200 and res.get("code") == 3000:
                    audio_data = res.get("data")
                    if audio_data:
                        logger.info(f"✅ 合成成功 reqid:{reqid}")
                        return audio_data
                logger.error(f"错误: {res}")
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
        return None