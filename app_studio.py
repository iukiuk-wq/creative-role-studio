# Creative Role Studio
# Extended version of the original Role-based Creative Chatbot.
# Features: conversation memory, custom role, answer language, creativity,
# and conversation download.

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🎭 Creative Role Studio", page_icon="🎭", layout="wide")
st.title("🎭 Creative Role Studio")
st.caption("Arts and Advanced Big Data | Chat with a creative role")

ROLES = {
    "🎥 Video Director": (
        "You are a professional film director. Give concrete advice on visual storytelling, "
        "camera movement, lighting, framing, editing rhythm, and emotional tone."
    ),
    "💃 Dance Instructor": (
        "You are a dance instructor. Explain ideas through movement, rhythm, choreography, "
        "body expression, and stage presence. Give practical step-by-step guidance."
    ),
    "👗 Fashion Stylist": (
        "You are a creative fashion stylist. Explain ideas through color palettes, textures, "
        "silhouettes, outfits, and styling choices."
    ),
    "🎭 Acting Coach": (
        "You are an acting coach. Give practical advice about emotion, voice, gesture, timing, "
        "character building, and body language."
    ),
    "🎨 Art Curator": (
        "You are an art curator. Discuss artistic themes, visual language, art history, "
        "and exhibition concepts in an analytical yet imaginative way."
    ),
    "✍️ Custom role": "",
}

# Sidebar settings
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input(
    "OpenAI API key",
    type="password",
    placeholder="sk-...",
    help="Enter your own OpenAI API key. Do not put it in your GitHub code."
)
model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
role_name = st.sidebar.selectbox("Creative role", list(ROLES.keys()))

if role_name == "✍️ Custom role":
    role_description = st.sidebar.text_area(
        "Describe your custom role",
        value="You are a poet who explains ideas through seasons, images, and metaphors.",
        height=120,
    )
else:
    role_description = ROLES[role_name]
    st.sidebar.info(role_description)

language = st.sidebar.selectbox(
    "Answer language",
    ["Same as my question", "English", "한국어"],
)
temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.7, 0.1)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("🗑️ Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# Conversation display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    st.info(f"Choose a role in the sidebar and ask a question below.")

question = st.chat_input("Type your question or idea...")

if question:
    if not api_key.strip():
        st.warning("Please enter your OpenAI API key in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        system_prompt = role_description
        if language == "English":
            system_prompt += " Always answer in English."
        elif language == "한국어":
            system_prompt += " 항상 한국어로 답변하세요."

        # Send the conversation so the model can use previous turns as context.
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(st.session_state.messages)

        with st.chat_message("assistant"):
            try:
                client = OpenAI(api_key=api_key.strip())
                with st.spinner("AI is thinking..."):
                    response = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        temperature=temperature,
                    )
                answer = response.choices[0].message.content or ""
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as error:
                # Remove the unanswered user turn so the chat history stays consistent.
                st.session_state.messages.pop()
                st.error(f"Could not generate a response: {error}")

# Download chat transcript
if st.session_state.messages:
    transcript_lines = []
    for message in st.session_state.messages:
        speaker = "You" if message["role"] == "user" else role_name
        transcript_lines.append(f"{speaker}:\n{message['content']}")
    transcript = "\n\n".join(transcript_lines)
    st.sidebar.download_button(
        "💾 Download conversation",
        data=transcript,
        file_name="creative_role_studio_conversation.txt",
        mime="text/plain",
    )

st.markdown("---")
st.caption("Built for 'Art & Advanced Big Data' • Prof. Jahwan Koo (SKKU)")
