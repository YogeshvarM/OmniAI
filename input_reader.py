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
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=1024
        )
        
        return chat_completion.choices[0].message.content.strip()