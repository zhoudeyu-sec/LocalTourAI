import pymysql

# 在这里填入你认为可能的密码列表，比如 ['123456', 'root', 'admin', '']
passwords_to_try = ['123456', 'root', '123qwe', ''] 

for pwd in passwords_to_try:
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password=pwd,
            database='mysql' # 先连系统库测试
        )
        print(f"成功了！正确的密码是: '{pwd}'")
        conn.close()
        break
    except Exception as e:
        print(f"尝试密码 '{pwd}' 失败: {e}")