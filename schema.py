from typing import List
from pydantic import BaseModel

class Thread(BaseModel):
    thread_content: str

class YTVideo(BaseModel):
    yt_video_description: str

class LinkedIn(BaseModel):
    linkedin_post_content: str

class Twitter(BaseModel):
    twitter_threads: List[Thread]