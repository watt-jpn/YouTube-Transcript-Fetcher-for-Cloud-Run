import re
import unicodedata
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI(title="YouTube Transcript API")
ytt_api = YouTubeTranscriptApi()

class TranscriptRequest(BaseModel):
    video_id: str

def clean_text_optimized(text: str) -> str:
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\[.*?\]|\(.*?\)|（.*?）', '', text)
    text = re.sub(r'[、。]|\u1366', '', text)
    return text

def get_best_transcript(video_id: str) -> str:
    transcript_list = ytt_api.list(video_id)
    
    selected_transcript = None

    # 1. 第一候補: 手動生成字幕 (ja -> en -> その他)
    manual_transcripts = {t.language_code: t for t in transcript_list if not t.is_generated}
    if manual_transcripts:
        if 'ja' in manual_transcripts:
            selected_transcript = manual_transcripts['ja']
        elif 'en' in manual_transcripts:
            selected_transcript = manual_transcripts['en']
        else:
            selected_transcript = list(manual_transcripts.values())[0]

    # 2. 第二候補: 自動生成字幕 (ja -> en のみ)
    if not selected_transcript:
        generated_transcripts = {t.language_code: t for t in transcript_list if t.is_generated}
        if 'ja' in generated_transcripts:
            selected_transcript = generated_transcripts['ja']
        elif 'en' in generated_transcripts:
            selected_transcript = generated_transcripts['en']

    if not selected_transcript:
        raise ValueError(f"動画ID '{video_id}' に利用可能な字幕が見つかりませんでした。")
    
    transcript_data = selected_transcript.fetch()
    
    cleaned_snippets = [clean_text_optimized(snippet.text) for snippet in transcript_data]
    full_text = " ".join([s for s in cleaned_snippets if s.strip()])
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    
    return full_text

@app.post("/transcript")
def fetch_transcript(req: TranscriptRequest):
    try:
        text = get_best_transcript(req.video_id)
        return {
            "status": "success",
            "video_id": req.video_id,
            "transcript": text
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部エラーが発生しました: {str(e)}")