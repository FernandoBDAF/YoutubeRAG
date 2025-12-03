"""
Backfill transcripts for videos without captions by downloading audio and
transcribing via Amazon Transcribe. Requires:
- AWS creds in env (AWS_ACCESS_KEY_ID/SECRET/SESSION_TOKEN, AWS_REGION)
- An S3 bucket for staging audio (TRANSCRIBE_S3_BUCKET or S3_BUCKET_NAME)
- Mongo URI/DB from ../.env
- yt-dlp installed (added to requirements.txt)
"""
from __future__ import annotations

import os
import tempfile
import time
import uuid
from typing import Optional

import boto3
import pymongo
import requests
from dotenv import load_dotenv
from yt_dlp import YoutubeDL


def download_audio(video_id: str, output_dir: str) -> str:
    """Download audio for the given YouTube video ID as mp3."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    filename = os.path.join(output_dir, f"{video_id}.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
        "noprogress": True,
        "extractor_args": {"youtube": {"player_client": ["default"]}},
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    mp3_path = filename.replace("%(ext)s", "mp3")
    return mp3_path


def start_transcribe_job(
    transcribe_client,
    media_uri: str,
    language_code: str = "en-US",
) -> str:
    job_name = f"yt-transcribe-{uuid.uuid4()}"
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_uri},
        MediaFormat="mp3",
        LanguageCode=language_code,
    )
    return job_name


def wait_for_transcript(transcribe_client, job_name: str, timeout_s: int = 900) -> Optional[str]:
    """Poll Transcribe until the job completes; return transcript text."""
    start = time.time()
    while True:
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        if status == "COMPLETED":
            uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            resp = requests.get(uri, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            transcripts = data.get("results", {}).get("transcripts", [])
            return " ".join(t.get("transcript", "") for t in transcripts)
        if status == "FAILED":
            raise RuntimeError(f"Transcribe job failed: {job}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Transcribe job {job_name} timed out after {timeout_s}s")
        time.sleep(5)


def main() -> None:
    load_dotenv("../.env", override=True)

    mongo_uri = os.environ["MONGODB_ATLAS_URI"]
    db_name = os.getenv("MONGODB_DB") or os.getenv("ATLAS_DB_NAME") or "AWSAgentCoreDemoDB"
    s3_bucket = os.getenv("TRANSCRIBE_S3_BUCKET") or os.getenv("S3_BUCKET_NAME")
    s3_prefix = os.getenv("TRANSCRIBE_S3_PREFIX", "transcribe_uploads")
    region = os.environ["AWS_REGION"]
    language_code = os.getenv("TRANSCRIBE_LANGUAGE_CODE", "en-US")

    if not s3_bucket:
        raise RuntimeError("Set TRANSCRIBE_S3_BUCKET or S3_BUCKET_NAME for audio staging.")

    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    raw = db["raw_videos"]

    # Find videos with missing/empty transcripts
    videos = list(
        raw.find(
            {
                "$or": [
                    {"transcript_raw": {"$exists": False}},
                    {"transcript_raw": {"$in": [None, ""]}},
                ]
            },
            {"video_id": 1, "playlist_id": 1},
        )
    )
    if not videos:
        print("No videos with missing transcripts.")
        return

    s3_client = boto3.client("s3", region_name=region)
    transcribe_client = boto3.client("transcribe", region_name=region)

    with tempfile.TemporaryDirectory() as tmpdir:
        for v in videos:
            vid = v.get("video_id")
            if not vid:
                continue
            print(f"[transcribe] Processing {vid}...")
            try:
                audio_path = download_audio(vid, tmpdir)
                key = f"{s3_prefix}/{vid}/{os.path.basename(audio_path)}"
                s3_client.upload_file(audio_path, s3_bucket, key)
                media_uri = f"s3://{s3_bucket}/{key}"
                job_name = start_transcribe_job(transcribe_client, media_uri, language_code)
                transcript_text = wait_for_transcript(transcribe_client, job_name)
                if transcript_text:
                    raw.update_one(
                        {"video_id": vid},
                        {
                            "$set": {
                                "transcript_raw": transcript_text,
                                "transcript_language": language_code,
                            }
                        },
                    )
                    print(f"[transcribe] Saved transcript for {vid} (chars={len(transcript_text)})")
                else:
                    print(f"[transcribe] No transcript text returned for {vid}")
            except Exception as exc:  # noqa: BLE001
                print(f"[transcribe] Failed for {vid}: {exc}")

    client.close()


if __name__ == "__main__":
    main()
