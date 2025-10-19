from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            transcript TEXT NOT NULL,
            raw_audio_url TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class VoiceLog(BaseModel):
    userId: str
    timestamp: datetime
    transcript: str
    rawAudioUrl: str | None = None

@app.post("/logs")
async def receive_log(log: VoiceLog):
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO voice_logs (user_id, timestamp, transcript, raw_audio_url)
            VALUES (?, ?, ?, ?)
        """, (log.userId, log.timestamp.isoformat(), log.transcript, log.rawAudioUrl))
        conn.commit()
        conn.close()
        return {"message": "Voice log stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
