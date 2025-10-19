from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            user_transcript TEXT NOT NULL,
            user_audio_url TEXT,
            gpt_response TEXT NOT NULL,
            gpt_audio_url TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ConversationLog(BaseModel):
    userId: str
    timestamp: datetime
    userTranscript: str
    userAudioUrl: str | None = None
    gptResponse: str
    gptAudioUrl: str | None = None

@app.post("/logs")
async def log_conversation(log: ConversationLog):
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_logs (
                user_id, timestamp, user_transcript, user_audio_url, gpt_response, gpt_audio_url
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            log.userId,
            log.timestamp.isoformat(),
            log.userTranscript,
            log.userAudioUrl,
            log.gptResponse,
            log.gptAudioUrl
        ))
        conn.commit()
        conn.close()
        return {"message": "Conversation log stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
