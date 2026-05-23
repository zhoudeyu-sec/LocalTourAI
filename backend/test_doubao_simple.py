import os
import asyncio
import httpx

# ======================
# 正确密钥在这里！
# ======================
os.environ["DOUBAO_API_KEY"] = "ark-a60fa04d-1691-4a3f-ac7e-dfba18d4a641-4a661"
os.environ["DOUBAO_ENDPOINT_ID"] = "ep-m-20260517004545-vwkx7"
os.environ["DOUBAO_BASE_URL"] = "https://ark.cn-beijing.volces.com/api/v3"

API_KEY = os.getenv("DOUBAO_API_KEY", "")
ENDPOINT_ID = os.getenv("DOUBAO_ENDPOINT_ID", "")
BASE_URL = os.getenv("DOUBAO_BASE_URL")

async def test_doubao():
    print("=" * 50)
    print("豆包 API 配置测试")
    print("=" * 50)

    print(f"\n📋 当前配置:")
    print(f"   API_KEY: {API_KEY[:20]}... (长度: {len(API_KEY)})")
    print(f"   ENDPOINT_ID: {ENDPOINT_ID}")
    print(f"   BASE_URL: {BASE_URL}")

    if not API_KEY or not ENDPOINT_ID:
        print("\n❌ 配置缺失")
        return

    print("\n🚀 开始测试...")

    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": ENDPOINT_ID,
            "messages": [
                {"role": "system", "content": "你是测试助手"},
                {"role": "user", "content": "你好"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
            print(f"📥 状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("\n✅ 调用成功！")
                print("🤖 回答:", result["choices"][0]["message"]["content"])
            else:
                print("\n❌ 失败:", response.text)
    except Exception as e:
        print("\n❌ 错误:", e)

if __name__ == "__main__":
    asyncio.run(test_doubao())