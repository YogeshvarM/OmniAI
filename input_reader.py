from constants import *
import os
import requests
import PyPDF2
from bs4 import BeautifulSoup
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)

class InputReader:
    def transcribe_audio(self, audio_fp: str, language: str = "en") -> str:
        with open(audio_fp, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_fp, file.read()), 
                model="whisper-large-v3", 
                prompt="Specify context or spelling",
                response_format="json",
                language=language,
                temperature=0.0
            )
        return transcription.text

    def read_pdf_file(self, file_path: str) -> str:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def read_text_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def read_website(self, url: str) -> str:
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch content from {url}")
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = f"""Translate the following text from {source_lang} to {target_lang}:

    {text}

    Translation guidelines:
    1. Maintain the original meaning and tone.
    2. Use natural, fluent language in the target language.
    3. Avoid word-for-word translation if it doesn't sound natural.
    4. Do not repeat information or phrases.
    5. Ensure the translation is concise and clear.
    6. If the original text contains repetitions, consolidate the information in the translation.
    7. Maintain paragraph structure, but feel free to combine sentences for better flow.

    Translated text:"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert translator. Provide accurate, natural-sounding translations without any repetition. Consolidate information if the source text is repetitive."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.2-90b-vision-preview",
            temperature=0.1,
            max_tokens=3000  # Slightly reduce token limit
        )
        
        return chat_completion.choices[0].message.content.strip()
