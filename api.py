from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from input_reader import InputReader
from llm import create_platform_content
import os
import uvicorn

app = FastAPI()

@app.post("/process_audio/")
async def process_audio(
    file: UploadFile = File(...),
    source_lang: str = Form("en"),
    translate: bool = Form(False),
    target_lang: str = Form("en"),
    platform: str = Form("twitter")
):
    try:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        reader = InputReader()
        transcribed_content = reader.transcribe_audio(file_location, source_lang)

        if translate:
            content_for_platform = reader.translate_text(transcribed_content, target_lang)
        else:
            content_for_platform = transcribed_content

        platform_content = create_platform_content(content_for_platform, platform)

        os.remove(file_location)

        return JSONResponse(content={
            "transcribed_content": transcribed_content,
            "translated_content": content_for_platform if translate else None,
            "platform_content": str(platform_content)
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/transcribe_audio/")
async def transcribe_audio(
    file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("en"),
    platform: str = Form("twitter")
):
    try:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        reader = InputReader()
        input_content = reader.transcribe_and_translate_audio(file_location, source_lang, target_lang)

        content = create_platform_content(input_content, platform)

        os.remove(file_location)

        return JSONResponse(content={
            "transcribed_content": input_content,
            "platform_content": str(content)
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

