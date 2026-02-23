import dashscope
import json
import re

# ⚡ 替换为你自己的 Dashscope API Key
dashscope.api_key = "sk-f20d0f9c2c6f41fda8b7f2fde114ba4e"

SYSTEM_PROMPT = """
你是一名极其资深的数学教育专家。请将 OCR 识别的 LaTeX 片段还原为高质量题目并解析。
必须只返回 JSON，格式如下：
{
  "status": "success | invalid",
  "formatted_question": "题目内容...",
  "knowledge_points": "考点...",
  "analysis": "解题步骤...",
  "answer": "最终答案"
}
"""


def format_question(ocr_text: str) -> dict:
    # 初始保底数据，防止任何环节出错导致 None
    default_res = {
        "status": "invalid",
        "formatted_question": "解析失败：无法从图片提取题目",
        "knowledge_points": "未知",
        "analysis": "请尝试拍摄更清晰的图片",
        "answer": "无"
    }

    if not ocr_text or ocr_text.strip() == "":
        return default_res

    try:
        response = dashscope.Generation.call(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"内容：{ocr_text}"}
            ],
            result_format="message",
            temperature=0.1
        )

        content = response["output"]["choices"][0]["message"]["content"]

        # 1. 清洗可能存在的 Markdown 标签
        json_str = re.sub(r'^```json\s*|```$', '', content.strip(), flags=re.MULTILINE)

        # 2. 尝试解析 JSON
        try:
            result = json.loads(json_str)
        except Exception:
            # 如果解析失败，可能是格式不规范，返回保底
            return default_res

        # 3. 强制确保所有字段不为 None 且为字符串 (修复 Parameter 3 错误的关键)
        processed_res = {
            "status": str(result.get("status", "invalid")),
            "formatted_question": str(result.get("formatted_question") or "题目还原缺失"),
            "knowledge_points": str(result.get("knowledge_points") or "未知考点"),
            "analysis": str(result.get("analysis") or "暂无解析步骤"),
            "answer": str(result.get("answer") or "暂无答案")
        }
        return processed_res

    except Exception as e:
        print(f"LLM 运行异常: {str(e)}")
        return default_res