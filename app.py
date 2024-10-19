from input_reader import InputReader
from llm import create_platform_content
import streamlit as st
import os

st.title("Omnipost AI")
st.write("Choose an operation: Process Input & Translate, or Generate Platform Content")

operation = st.radio("Choose operation", ["Process Input & Translate", "Generate Platform Content"])

reader = InputReader()

if operation == "Process Input & Translate":
    input_type = st.selectbox("Select input type", ["Audio", "PDF", "Website", "Text File"])
    
    if input_type == "Audio":
        uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
    elif input_type == "PDF":
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    elif input_type == "Text File":
        uploaded_file = st.file_uploader("Choose a text file", type=["txt"])
    elif input_type == "Website":
        url = st.text_input("Enter website URL")
    
    source_lang = st.selectbox("Select source language", options=["en", "hi", "es", "fr", "de"])
    target_lang = st.selectbox("Select target language for translation", options=["en", "hi", "es", "fr", "de"])
    output_dir = st.text_input("Enter output directory path", value="./output")
    
    if st.button("Process & Translate"):
        with st.spinner("Processing..."):
            try:
                if input_type == "Website":
                    content = reader.read_website(url)
                else:
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
                
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"translated_output.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(translated_content)
                
                st.session_state.translated_text = translated_content
                st.subheader("Processed & Translated Content:")
                st.write(translated_content)
                st.success(f"Translated content saved to {output_file}")
                
                if input_type != "Website":
                    os.remove(file_location)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif operation == "Generate Platform Content":
    input_type = st.selectbox("Select input type", ["Previous Output", "Text Input", "Audio", "PDF", "Website", "Text File"])
    
    input_text = None  # Initialize input_text to None

    if input_type == "Previous Output":
        if 'translated_text' in st.session_state:
            st.write("Using previously processed text:")
            st.write(st.session_state.translated_text)
            input_text = st.session_state.translated_text
        else:
            st.warning("No previous output available. Please choose another input type.")
    elif input_type == "Text Input":
        input_text = st.text_area("Enter text for content generation")
    elif input_type == "Audio":
        uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            with st.spinner("Transcribing audio..."):
                file_location = f"temp_{uploaded_file.name}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(uploaded_file.read())
                input_text = reader.transcribe_audio(file_location)
                os.remove(file_location)
    elif input_type == "PDF":
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file:
            with st.spinner("Reading PDF..."):
                file_location = f"temp_{uploaded_file.name}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(uploaded_file.read())
                input_text = reader.read_pdf_file(file_location)
                os.remove(file_location)
    elif input_type == "Website":
        url = st.text_input("Enter website URL")
        if url:
            with st.spinner("Fetching website content..."):
                input_text = reader.read_website(url)
    elif input_type == "Text File":
        uploaded_file = st.file_uploader("Choose a text file", type=["txt", "doc", "docx"])
        if uploaded_file:
            with st.spinner("Reading file..."):
                file_location = f"temp_{uploaded_file.name}"
                with open(file_location, "wb+") as file_object:
                    file_object.write(uploaded_file.read())
                input_text = reader.read_text_file(file_location)
                os.remove(file_location)

    if input_text:
        st.write("Input content preview:")
        st.write(input_text[:500] + "..." if len(input_text) > 500 else input_text)

    if input_text is None or input_text.strip() == "":
        st.warning("Please provide input for content generation.")
    else:
        platform = st.selectbox("Select platform", options=["ytvideo", "linkedin", "twitter"])
        
        if st.button("Generate Content"):
            with st.spinner("Generating content..."):
                try:
                    response = create_platform_content(input_text, platform)
                    st.subheader("Generated Platform Content:")
                    st.write(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

st.success("Processing completed successfully!")
