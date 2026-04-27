import streamlit as st
from crew import MentalHealthApp
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

st.set_page_config(page_title="Mental Health Assistant", layout="centered")

st.title("🧠 Mental Health Assistant")
st.caption("AI-powered emotional support with voice guidance")

# User input
user_input = st.text_area("How are you feeling?")

# Text to audio
def text_to_audio(text):
    try:
        tts = gTTS(text[:300])
        tts.save("output.mp3")
    except Exception as e:
        st.error(f"Audio generation failed: {e}")

# Button
if st.button("Get Support 🚀"):

    if not user_input or user_input.strip() == "":
        st.warning("Please enter something first.")
    else:
        with st.spinner("Analyzing and generating support..."):

            try:
                result = MentalHealthApp().crew().kickoff(
                    inputs={"user_input": user_input}
                )

                result = str(result)

                voice_text = f"""
                Hey, right now you're dealing with something important.

                {result[:250].rsplit('.', 1)[0] + '.'}

                Take this step by step. You don’t have to figure everything out at once.
                """

                text_to_audio(voice_text)

                st.success("Personalized AI support ready 🎧")

                st.divider()

                st.subheader("Guidance")
                st.write(result.strip())

                st.audio("output.mp3")

            except Exception as e:
                st.error(f"Something went wrong: {e}")