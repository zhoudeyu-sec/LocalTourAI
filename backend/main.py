import logging
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Query as SAQuery, Session

import database
import models
import schemas
from doubao_client import DoubaoClient
from tts_client import TTSClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="景区数字人导游系统 API",
    description="支持管理后台与游客交互端的核心后端服务（接入豆包大模型）",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

# 初始化豆包客户端
doubao = DoubaoClient()

# 初始化 TTS 客户端
tts_client = TTSClient()


def ok(data: Any = None, message: str = "success") -> dict:
    body: dict = {"code": 200, "message": message}
    if data is not None:
        body["data"] = data
    return body


def paginate(query: SAQuery, skip: int, limit: int) -> tuple[list, int]:
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_kb_or_404(db: Session, kb_id: int) -> models.KnowledgeBase:
    item = db.get(models.KnowledgeBase, kb_id)
    if not item:
        raise HTTPException(status_code=404, detail="条目不存在")
    return item


def get_config_or_create(db: Session) -> models.DigitalHumanConfig:
    config = db.query(models.DigitalHumanConfig).first()
    if config:
        return config
    config = models.DigitalHumanConfig(
        avatar_style="古风导游",
        voice_type="温柔女声",
        greeting_text="您好，我是您的灵山数字导游，请问有什么可以帮您？",
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    return response


# --- 问答 ---

@app.post("/api/v1/chat/ask", tags=["游客交互"])
async def ask_question(request: schemas.ChatRequest, db: Session = Depends(database.get_db)):
    """接收游客提问，调用豆包大模型，记录对话日志"""
    start = time.perf_counter()
    try:
        # 检索知识库（RAG - 简单关键词匹配）
        query = db.query(models.KnowledgeBase)
        keywords = request.question.split()
        relevant_kb = []
        for kb in query.all():
            if any(k in kb.title or k in kb.content for k in keywords):
                relevant_kb.append(f"【{kb.title}】\n{kb.content}")
                if len(relevant_kb) >= 3:
                    break

        # 构建系统提示词（注入知识库内容）
        system_prompt = """你是景区数字人导游小景，请热情友好地回答游客问题。

## 景区知识库（请优先使用以下信息回答）：
"""
        if relevant_kb:
            for ctx in relevant_kb:
                system_prompt += f"\n{ctx}\n"
        else:
            system_prompt += "\n（当前知识库暂无相关信息，请根据你的通用知识回答）\n"

        system_prompt += """
## 要求：
1. 优先使用知识库信息回答，确保信息准确
2. 回答简洁明了，100字左右，适合语音播报
3. 不知道的问题要诚实告知，建议咨询景区服务台
"""

        # 调用豆包大模型
        ai_response = await doubao.chat(request.question, system_prompt)

        duration_ms = int((time.perf_counter() - start) * 1000)

        new_log = models.ConversationLog(
            user_id=request.user_id,
            question=request.question,
            answer=ai_response,
            response_time=duration_ms,
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return ok(
            {
                "answer": ai_response,
                "log_id": new_log.id,
                "response_time": f"{duration_ms}ms",
            }
        )
    except Exception as e:
        logger.error("问答接口异常: %s", e)
        db.rollback()
        raise HTTPException(status_code=500, detail="系统处理对话时出现异常")


# --- 知识库 CRUD ---

@app.get("/api/v1/kb/list", tags=["知识库管理"])
def get_kb_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(database.get_db),
):
    query = db.query(models.KnowledgeBase)
    if keyword:
        query = query.filter(models.KnowledgeBase.title.contains(keyword))
    query = query.order_by(models.KnowledgeBase.id.desc())
    items, total = paginate(query, skip, limit)
    return ok({"items": items, "total": total})


@app.post("/api/v1/kb/add", tags=["知识库管理"])
def create_kb_item(item: schemas.KBBase, db: Session = Depends(database.get_db)):
    try:
        db_item = models.KnowledgeBase(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return ok(db_item, "添加成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存失败: {e}")


@app.put("/api/v1/kb/update/{kb_id}", tags=["知识库管理"])
def update_kb_item(kb_id: int, item: schemas.KBBase, db: Session = Depends(database.get_db)):
    db_item = get_kb_or_404(db, kb_id)
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return ok(db_item, "更新成功")


@app.delete("/api/v1/kb/delete/{kb_id}", tags=["知识库管理"])
def delete_kb_item(kb_id: int, db: Session = Depends(database.get_db)):
    db.delete(get_kb_or_404(db, kb_id))
    db.commit()
    return ok(message="删除成功")


@app.post("/api/v1/kb/upload", tags=["知识库管理"])
async def upload_kb_file(file: UploadFile = File(...)):
    safe_name = Path(file.filename or "upload").name
    dest = UPLOAD_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)
    return ok(message=f"文件 {safe_name} 上传成功，已通知大模型模块进行解析。")


# --- 数据统计 ---

@app.get("/api/v1/stats/overview", tags=["数据统计"])
def get_stats_overview(db: Session = Depends(database.get_db)):
    try:
        total_kb = db.query(func.count(models.KnowledgeBase.id)).scalar()
        total_logs = db.query(func.count(models.ConversationLog.id)).scalar()
        avg_rt = db.query(func.avg(models.ConversationLog.response_time)).scalar() or 0
        return ok(
            {
                "total_kb_count": total_kb,
                "total_chat_count": total_logs,
                "avg_response_time": round(float(avg_rt), 2),
            }
        )
    except Exception:
        raise HTTPException(status_code=500, detail="获取统计信息失败")


# --- 日志 ---

@app.get("/api/v1/logs/list", tags=["日志管理"])
def get_logs_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(database.get_db),
):
    query = db.query(models.ConversationLog).order_by(models.ConversationLog.id.desc())
    items, total = paginate(query, skip, limit)
    return ok({"items": items, "total": total})


# --- 数字人配置 ---

@app.get("/api/v1/config", tags=["数字人配置"])
def get_config(db: Session = Depends(database.get_db)):
    return ok(get_config_or_create(db))


@app.post("/api/v1/config", tags=["数字人配置"])
def update_config(config_data: schemas.ConfigBase, db: Session = Depends(database.get_db)):
    config = db.query(models.DigitalHumanConfig).first()
    if not config:
        config = models.DigitalHumanConfig(**config_data.model_dump())
        db.add(config)
    else:
        for key, value in config_data.model_dump().items():
            setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return ok(config, "保存成功")


# --- TTS 语音合成 ---

@app.post("/api/v1/tts/synthesize", tags=["语音合成"])
async def synthesize_speech(request: dict):
    """
    文本转语音接口
    请求格式: {"text": "要朗读的文字", "style": "ancient|modern|cartoon"}
    响应: {"code": 200, "data": {"audio": "base64编码的音频"}}
    """
    text = request.get("text", "")
    style = request.get("style", "ancient")
    
    if not text:
        return {"code": 400, "message": "文本不能为空"}
    
    audio_b64 = await tts_client.synthesize(text, style)
    
    if audio_b64:
        return {"code": 200, "data": {"audio": audio_b64}, "message": "success"}
    else:
        return {"code": 500, "message": "语音合成失败"}


# --- 健康检查 ---

@app.get("/api/v1/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"code": 200, "status": "healthy", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)