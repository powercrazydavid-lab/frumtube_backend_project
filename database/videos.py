import requests
from datetime import datetime, date
from typing import Dict,Optional, List, Any
from pydantic import BaseModel, HttpUrl, ValidationError

# --- Pydantic Models ---
class Creator(BaseModel):
    user_id: str
    user_name: str
    avatar: HttpUrl
    isVerified: bool
    subscribers: int

class VideoAnalytics(BaseModel):
    watchTime: int
    engagement: float
    retention: List[str]
    demographics: Dict[str, Dict[str, int]]

class VideoResponse(BaseModel):
    video_id: str
    title: str
    description: str
    thumbnail: HttpUrl
    videoUrl: HttpUrl
    duration: str
    views: int
    likes: int
    dislikes: int
    uploadDate: str
    creator: Creator
    category: str
    tags: List[str]
    status: str
    moderationFlags: List[str]
    analytics: Optional[VideoAnalytics]

class VideoService:
    def __init__(self, supabase, backblaze_bucket_url, backblaze_auth_token):
        self.supabase = supabase
        self.backblaze_bucket_url = backblaze_bucket_url
        self.backblaze_auth_token = backblaze_auth_token

    # --- Upload file to Backblaze ---
    def upload_to_backblaze(self, file_path: str, file_name: str) -> str:
        headers = {
            "Authorizaiton": f"Bearer {self.backblaze_auth_token}"
        }

        files = {"file": open(file_path, "rb")} 
        response = requests.post(f"{self.backblaze_bucket_url}/{file_name}", headers=headers, files=files)
        if response.status_code == 200:

            # --- Return publick file URL ---
            return f"{self.backblaze_bucket_url}/{file_name}"
        else:
            raise Exception(f"Backblaze upload failed: {response.text}")