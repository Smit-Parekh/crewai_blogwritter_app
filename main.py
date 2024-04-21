import streamlit as st
import crewai_langchain

callback_logs_location = "F:/Smit Python Projects/GitHub Projects/New folder/crewai_blogwritter_app/crew_callback_logs.txt"

st.title("🦜🔗 Langchain and CrewAI Agents based Blog Generator App")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "On which topic should I write blog post for you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    msg = crewai_langchain.blog_result(prompt)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    st.chat("Here is Crew's Callback Logs:", callback_logs_location)