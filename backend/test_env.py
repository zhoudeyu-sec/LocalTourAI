import os

# 绕过 dotenv bug，直接手动赋值
os.environ["DOUBAO_API_KEY"] = "apikey-20260517002719-bc48x"
os.environ["DOUBAO_ENDPOINT_ID"] = "ep-m-20260517004545-vwkx7"
os.environ["DOUBAO_BASE_URL"] = "https://ark.cn-beijing.volces.com/api/v3"

print("读取 DOUBAO_API_KEY =", os.getenv("DOUBAO_API_KEY"))
print("读取 DOUBAO_ENDPOINT_ID =", os.getenv("DOUBAO_ENDPOINT_ID"))