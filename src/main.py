import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from query import query_rag_pipeline

st.set_page_config(
    page_title="Document Q&A Bot",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Document Q&A Bot")
st.markdown("Ask any question about your uploaded documents. Answers are grounded with citations.")

st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Ask a question about your documents...")

if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                result = query_rag_pipeline(user_query)
                answer = result["answer"]
                citations = result["citations"]

                st.markdown(answer)

                if citations:
                    st.divider()
                    st.markdown("**📚 Sources Used:**")
                    for cite in set(citations):
                        st.markdown(f"- {cite}")

                full_response = answer + "\n\n**Sources:** " + ", ".join(set(citations))
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})

            except Exception as e:
                err_msg = f"❌ Error: {str(e)}"
                st.error(err_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": err_msg})

with st.sidebar:
    st.header("📁 About")
    st.info("This bot answers questions using only your documents stored in the `data/` folder.")
    st.markdown("**How to use:**")
    st.markdown("1. Add PDFs or DOCX files to the `data/` folder")
    st.markdown("2. Run `python -m src.ingest` to index them")
    st.markdown("3. Ask questions in the chat!")
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()