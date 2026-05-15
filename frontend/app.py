import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Resume Agent", layout="wide")
st.title("Resume Agent")
st.markdown("Chat with your candidates' resumes.")

with st.sidebar:
    st.header("Upload Resumes")
    uploaded = st.file_uploader(
        "Choose resume files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded and st.button("Process Resumes", type="primary"):
        for file in uploaded:
            with st.spinner(f"Processing {file.name}..."):
                resp = requests.post(
                    f"{API_BASE_URL}/upload",
                    files={"file": (file.name, file.getvalue(), file.type)},
                )
                if resp.ok:
                    data = resp.json()
                    st.success(f"{file.name}: {data['chunks']} chunks indexed")
                else:
                    st.error(f"{file.name}: {resp.text}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about a candidate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_BASE_URL}/query",
                json={"question": prompt},
            )
            if resp.ok:
                data = resp.json()
                answer = data["answer"]
                st.markdown(answer)
                st.caption(f"Sources: {', '.join(data.get('sources', []))}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                st.error(resp.text)
