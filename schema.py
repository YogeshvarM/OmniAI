from typing import List
from pydantic import BaseModel

class Thread(BaseModel):
    thread_content: str


class LinkedIn(BaseModel):
    linkedin_post_content: str

class Twitter(BaseModel):
    twitter_threads: List[Thread]

class YTVideo:
    # Define the attributes of the YTVideo class
    def __init__(self, yt_video_description: str):
        self.yt_video_description = yt_video_description

    @classmethod
    def model_json_schema(cls):
        return {
            "type": "object",
            "properties": {
                "yt_video_description": {
                    "type": "string",
                    "title": "YT Video Description"
                },
            },
            "required": ["yt_video_description"],  # Ensure this field is required
            "title": "YTVideo"
        }

    @classmethod
    def model_validate(cls, content):
        # Implement validation logic if necessary
        # For example, you can check if content has the required fields
        if "yt_video_description" not in content:
            raise ValueError("Missing required field: yt_video_description")
        return cls(**content)  # Create an instance of YTVideo
