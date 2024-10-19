from input_reader import InputReader
from llm import create_platform_content
import streamlit as st
import os
from io import BytesIO
import tempfile

st.title("Omnipost AI")
st.write("Choose an operation: Process Input & Translate, or Generate Platform Content")

operation = st.radio("Choose operation", ["Process Input & Translate", "Generate Platform Content"])

reader = InputReader()

def download_text_file(text: str, filename: str):
    """Generate a download link for a text file."""
    buffer = BytesIO()
    buffer.write(text.encode())
    buffer.seek(0)
    return st.download_button(
        label="Download as TXT",
        data=buffer,
        file_name=filename,
        mime="text/plain"
    )

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"An error occurred while saving the file: {str(e)}")
        return None

if 'processed_text' not in st.session_state:
    st.session_state.processed_text = None

if operation == "Process Input & Translate":
    input_type = st.selectbox("Select input type", ["Audio", "PDF", "Text File"])
    
    if input_type == "Audio":
        uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
    elif input_type == "PDF":
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    elif input_type == "Text File":
        uploaded_file = st.file_uploader("Choose a text file", type=["txt"])
    
    source_lang = st.selectbox("Select source language", options=["en", "hi", "es", "fr", "de"])
    target_lang = st.selectbox("Select target language for translation", options=["en", "hi", "es", "fr", "de"])
    output_dir = st.text_input("Enter output directory path", value="./output")
    
    if st.button("Process & Translate"):
        with st.spinner("Processing..."):
            try:
                file_location = f"temp_{uploaded_file.name}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(uploaded_file.read())
                
                if input_type == "Audio":
                    content = reader.transcribe_audio(file_location, source_lang)
                elif input_type == "PDF":
                    content = reader.read_pdf_file(file_location)
                elif input_type == "Text File":
                    content = reader.read_text_file(file_location)
                
                translated_content = reader.translate_text(content, source_lang, target_lang)
                
                st.success("Translation completed successfully!")
                st.text_area("Translated Content", translated_content, height=300)
                
                # Store the translated content in session state
                st.session_state.processed_text = translated_content
                
                # Add download button
                download_text_file(translated_content, "translated_content.txt")
                
                os.remove(file_location)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif operation == "Generate Platform Content":
    input_type = st.selectbox("Select input type", ["Previous Output", "Text Input", "Audio", "PDF", "Text File"])
    
    temp_file_path = None
    
    if input_type == "Previous Output":
        if st.session_state.processed_text is None:
            st.error("No previous output available. Please process some input first.")
            st.stop()
        else:
            input_text = st.session_state.processed_text
    elif input_type == "Text Input":
        input_text = st.text_area("Enter your text here")
    else:
        if input_type == "Audio":
            uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
        elif input_type == "PDF":
            uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        elif input_type == "Text File":
            uploaded_file = st.file_uploader("Choose a text file", type=["txt"])
        
        if uploaded_file is not None:
            temp_file_path = save_uploaded_file(uploaded_file)
            if temp_file_path is None:
                st.error("Failed to save the uploaded file.")
                st.stop()
            
            if input_type == "Audio":
                input_text = reader.transcribe_audio(temp_file_path)
            elif input_type == "PDF":
                input_text = reader.read_pdf_file(temp_file_path)
            elif input_type == "Text File":
                input_text = reader.read_text_file(temp_file_path)
            
            st.session_state.processed_text = input_text
        else:
            st.warning("Please upload a file.")
            st.stop()

    platform = st.selectbox("Select platform", ["Twitter", "LinkedIn", "YouTube"])

    if st.button("Generate Content"):
        with st.spinner("Generating content..."):
            try:
                generated_content = create_platform_content(input_text, platform.lower())
                st.success("Content generated successfully!")
                st.text_area("Generated Content", generated_content, height=300)
                
                # Add download button
                download_text_file(generated_content, f"{platform.lower()}_content.txt")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Clean up the temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

st.success("Processing completed successfully!")
