# app.py
import streamlit as st
import requests

st.set_page_config(page_title="AI Study-Buddy", layout="wide")

st.title("📚 AI Study-Buddy for BMSCE")
st.write("Upload your course PDFs and ask any question!")

# File Uploader
with st.sidebar:
    st.header("Upload Your Notes")
    uploaded_files = st.file_uploader(
        "Choose your PDF files", accept_multiple_files=True, type="pdf"
    )
    if st.button("Process Documents"):
        if uploaded_files:
            with st.spinner("Indexing documents... this may take a moment."):
                files_to_send = [("files", file.getvalue()) for file in uploaded_files]
                response = requests.post("http://127.0.0.1:8000/upload/", files=files_to_send)
                if response.status_code == 200:
                    st.success("Documents indexed successfully!")
                else:
                    st.error("Failed to index documents.")
        else:
            st.warning("Please upload at least one PDF file.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post("http://127.0.0.1:8000/chat/", json={"prompt": prompt})
            full_response = response.json().get("response", "Sorry, something went wrong.")
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})