

from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import sqlite3
from datetime import datetime

from ocr import extract_text
from llm import format_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
DB_PATH = "db/mistakes_vangu.db"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 这里的字段顺序要和下面插入时完全对应
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT,
            status TEXT,
            formatted_question TEXT,
            knowledge_points TEXT,
            analysis TEXT,
            answer TEXT,
            created_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/history")
async def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mistakes ORDER BY created_at DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[-1].lower()
    if file_ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="仅支持图片格式")

    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. OCR 识别
        raw_text = extract_text(file_path)
        if not raw_text or "错误" in raw_text:
            return {"error": "OCR 识别失败", "detail": raw_text}

        # 2. LLM 格式化解析
        result = format_question(raw_text)

        # 3. 数据库插入 (关键修复点：使用 str() 包裹所有变量)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO mistakes (
                        raw_text, status, formatted_question, 
                        knowledge_points, analysis, answer, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(raw_text),                             # 1. raw_text
                    str(result.get("status")),                 # 2. status
                    str(result.get("formatted_question")),     # 3. formatted_question (报错位置)
                    str(result.get("knowledge_points")),       # 4. knowledge_points
                    str(result.get("analysis")),               # 5. analysis
                    str(result.get("answer")),                 # 6. answer
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 7. created_at
                ))
                conn.commit()
        except sqlite3.Error as db_err:
            print(f"数据库操作失败: {db_err}")
            # 如果报字段缺失，通常是因为旧表结构不对，建议删除 db 文件
            return {"error": "数据库同步失败", "detail": str(db_err)}

        return {"raw_ocr": raw_text, "ai_analysis": result}

    except Exception as e:
        print(f"服务器崩溃: {str(e)}")
        return {"error": "服务器内部错误", "detail": str(e)}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# 替换原来的 mount 代码
app.mount("/", StaticFiles(directory=".", html=True), name="static")