from constants import *
from prompts import *
from schema import *
from typing import Union, Optional
from groq import Groq
import json

groq = Groq(api_key=GROQ_API_KEY)

def format_prompt(platform: str):
    if platform == "linkedin":
        return LINKEDIN_PROMPT + JSONIFY_PROMPT
    elif platform == "ytvideo":
        return YT_VIDEO_PROMPT + JSONIFY_PROMPT
    elif platform == "twitter":
        return TWITTER_PROMPT + JSONIFY_PROMPT

def llm_call(input_content: str, platform: str, schema: Optional[Union[YTVideo, Twitter, LinkedIn]]) -> Union[YTVideo, Twitter, LinkedIn, str]:
    system_prompt = format_prompt(platform)

    chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt +
                f"The JSON object must use the schema: {json.dumps(schema.model_json_schema(), indent=2)}. Ensure the output is a valid JSON object.",
            },
            {
                "role": "user",
                "content": input_content,
            },
        ],
        model="llama3-70b-8192",
        temperature=0.2,
        stream=False,
        response_format={"type": "json_object"},
        max_tokens=8192
    )
    
    try:
        content = json.loads(chat_completion.choices[0].message.content)
        return schema.model_validate(content)
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw content
        return chat_completion.choices[0].message.content

def create_twitter_content(input_content: str) -> str:
    content = llm_call(input_content, "twitter", Twitter)
    if isinstance(content, Twitter):
        return "\n\n".join([thread.thread_content for thread in content.twitter_threads])
    return str(content)

def create_linkedin_content(input_content: str) -> str:
    content = llm_call(input_content, "linkedin", LinkedIn)
    if isinstance(content, LinkedIn):
        return content.linkedin_post_content
    return str(content)

def create_ytvideo_content(input_content: str) -> str:
    content = llm_call(input_content, "ytvideo", YTVideo)
    if isinstance(content, YTVideo):
        return content.yt_video_description
    return str(content)

def create_platform_content(input_text: str, platform: str) -> str:
    if platform.lower() == "youtube":
        return create_ytvideo_content(input_text)
    elif platform.lower() == "linkedin":
        return create_linkedin_content(input_text)
    elif platform.lower() == "twitter":
        return create_twitter_content(input_text)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
