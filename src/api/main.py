import re
from pathlib import Path
from typing import List
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from src.config.settings import load_app_config
from src.llm.client import LLMClient,Message
from src.memory.sqlite_memory import SQLiteChatMemory
from src.memory.summary_memory import (SummaryMemory,build_system_prompt,compress_memory_if_needed)

config=load_app_config()
client=LLMClient(config=config)
DB_PATH="data/api_chat_memory.db"
SUMMARY_DIR=Path("data/summaries")

app=FastAPI(
    title="LLM Agent Workbench API",
    description="一个支持多轮记忆和长期摘要记忆的大模型api",
    version="0.1.0"
)

class ChatRequest(BaseModel):
    message:str=Field(...,min_length=1,description="用户输入的问题")
    session_id:str=Field(default="default",description="会话ID,用来区分不同聊天")
    max_history:int=Field(default=6,ge=0,le=20,description="传给大模型的最近聊天数量")
    
class ChatResponse(BaseModel):
    answer:str
    session_id:str
    history_count:int
    summary:str

class HistoryResponse(BaseModel):
    session_id:str
    messages:List[Message]
    count:int

class SummaryResponse(BaseModel):
    session_id:str
    summary:str

class ClearResponse(BaseModel):
    session_id:str
    message:str

class HealthResponse(BaseModel):
    status:str
    provider:str
    model:str

def normalize_session_id(session_id:str)->str:
    session_id=session_id.strip()
    if not session_id:
        return "default"
    return re.sub(r"[^a-zA-Z0-9_-]","_",session_id)

def create_memory(session_id:str)->SQLiteChatMemory:
    return SQLiteChatMemory(db_path=DB_PATH,session_id=session_id)

def create_summary_memory(session_id)->SummaryMemory:
    summary_path=SUMMARY_DIR/f"{session_id}.txt"
    return SummaryMemory(file_path=str(summary_path))

@app.get("/health",response_model=HealthResponse)
def health()->HealthResponse:
    model=config.ollama_model if config.llm_provider=="ollama" else config.openai_model
    return HealthResponse(
        status="ok",
        provider=config.llm_provider,
        model=model
    )
    
@app.post("/chat",response_model=ChatResponse)
def chat(request:ChatRequest)->ChatResponse:
    session_id=normalize_session_id(request.session_id)
    memory=create_memory(session_id)
    summary_memory=create_summary_memory(session_id)
    
    try:
        system_prompt=build_system_prompt(summary_memory)
        recent_history=memory.get_recent_messages(max_messages=request.max_history)
        if config.debug:
            print(f"[DEBUG] session_id:{session_id}")
            print(f"[DEBUG] recent_history_count:{len(recent_history)}")
            print(f"[DEBUG] user_message:{request.message}")
        answer=client.chat(
            user_message=request.message,
            system_prompt=system_prompt,
            history=recent_history
        )
        memory.add_message("user",request.message)
        memory.add_message("assistant",answer)
        compress_memory_if_needed(
            memory=memory,
            summary_memory=summary_memory,
            client=client,
            trigger_count=14,
            keep_recent=6
        )
        return ChatResponse(
            answer=answer,
            session_id=session_id,
            history_count=memory.count(),
            summary=summary_memory.get_summary()
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    finally:
        memory.close()
        
@app.get("/sessions/{session_id}/history",response_model=HistoryResponse)
def get_history(session_id:str,limit:int=20)->HistoryResponse:
    session_id=normalize_session_id(session_id)
    memory=create_memory(session_id)
    try:
        messages = memory.get_recent_messages(max_messages=limit)

        return HistoryResponse(
            session_id=session_id,
            messages=messages,
            count=memory.count(),
        )

    finally:
        memory.close()
        
@app.get("sessions/{session_id}/summary",response_model=SummaryResponse)
def get_summary(session_id:str)->SummaryResponse:
    session_id=normalize_session_id(session_id)
    summary_memory=create_summary_memory(session_id)
    return SummaryResponse(session_id,summary_memory)

@app.post("sessions/{session_id}/clear",response_model=ClearResponse)
def clear_session(session_id:str)->ClearResponse:
    session_id=normalize_session_id(session_id)
    memory=create_memory(session_id)
    summary_memory=create_summary_memory(session_id)
    try:
        memory.clear()
        summary_memory.clear()
        return ClearResponse(
            session_id=session_id,
            message="短期记忆和长期摘要已清空。"
            )
    finally:
        memory.close()