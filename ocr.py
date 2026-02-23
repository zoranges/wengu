import requests
import time
import hashlib
import random
import os
import urllib3

# 禁用 SSL 警告（解决之前的 SSLError 报错）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 已填入你的 SimpleTex 凭据 ---
APP_ID = "UnBxBhrkZpz2sMdVALIoSTEu"
APP_SECRET = "nXLrNARCwUP7Lc9HUesS5dcs0dAXeYGS"


def extract_text(image_path: str) -> str:
    """调用 SimpleTex 标准公式识别接口 (APP鉴权版)"""
    if not os.path.exists(image_path):
        return "错误：找不到图片文件"

    # 1. 接口地址：标准公式识别模型
    url = "https://server.simpletex.cn/api/latex_ocr"

    # 2. 生成鉴权所需参数
    # 生成 16 位随机字符串
    random_str = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 16))
    timestamp = str(int(time.time()))

    # 3. 签名算法实现
    # 将参数放入字典，准备按 key 升序排序
    params = {
        "app-id": APP_ID,
        "random-str": random_str,
        "timestamp": timestamp
    }

    # 步骤：按 key 排序并用 & 拼接
    sorted_keys = sorted(params.keys())
    kv_pairs = [f"{k}={params[k]}" for k in sorted_keys]
    sign_string = "&".join(kv_pairs)

    # 步骤：末尾加上 secret
    sign_string += f"&secret={APP_SECRET}"

    # 步骤：MD5 加密生成 32 位签名
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

    # 4. 构建官方要求的 Header
    headers = {
        "app-id": APP_ID,
        "random-str": random_str,
        "timestamp": timestamp,
        "sign": sign,
        "Host": "server.simpletex.cn"
    }

    try:
        # 5. 发送请求
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=20,
                verify=False  # 绕过本地 DNS/SSL 限制
            )

        # 6. 处理返回结果
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") is True:
                # 关键：根据截图示例，识别内容在 res 下的 latex 字段
                res_body = res_json.get('res', {})
                latex_result = res_body.get('latex')

                if latex_result:
                    return latex_result
                else:
                    return "识别成功，但返回内容为空 [EMPTY]"
            else:
                # 记录详细错误代码
                return f"业务失败: {res_json.get('err', '未返回错误码')}"
        else:
            return f"HTTP 响应异常: {response.status_code}"

    except Exception as e:
        return f"接口调用崩溃: {str(e)}"


if __name__ == "__main__":
    # --- 测试 ---
    # 确保当前目录下有一张 test.jpg
    TEST_FILE = "test.jpg"
    if os.path.exists(TEST_FILE):
        print(f"🚀 正在调用 SimpleTex (ID: {APP_ID[:4]}...)")
        result = extract_text(TEST_FILE)
        print("\n=== 识别出的 LaTeX 公式 ===")
        print(result)
    else:
        print(f"❌ 请先在目录下放置测试图片: {TEST_FILE}")