import streamlit as st
import numpy as np
import os
import tempfile
import speech_recognition as sr
from jamaibase import JamAI, protocol as p

# Set your API Key and Project ID directly in the script
API_KEY = "Your API KEY HERE"
PROJECT_ID = "YOUR PROJECT ID HERE"
TABLE_ID = "YOUR ACTION TABLE ID HERE"

# Initialize JamAI client
jamai = JamAI(api_key=API_KEY, project_id=PROJECT_ID)

# Set page configuration for a better chat-like UI
st.set_page_config(page_title="Audio to Action Table Chat UI", layout="wide")

# Custom CSS to style the chat UI
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e1e;
            color: #f0f0f0;
        }
        .chat-container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        .user-message, .bot-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: #007BFF;
            color: #fff;
            text-align: right;
        }
        .bot-message {
            background-color: #333333;
            color: #fff;
        }
        .response-container {
            background-color: #444;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
        }
        .response-container h4 {
            color: #FFA500;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title of the app
st.markdown("<div class='chat-container'><h2>🎙️ Audio/Text Input Chat Interface</h2></div>", unsafe_allow_html=True)

# Speech recognizer instance
recognizer = sr.Recognizer()

# Chat-like interface for inputting audio or text
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_choice = st.radio("Select Input Type", ("Audio", "Text"), index=0)

        if input_choice == "Audio":
            audio_file = st.file_uploader("Upload your audio file", type=["wav", "mp3", "flac"])
            if audio_file is not None:
                # Save the uploaded audio to a temporary file
                temp_file_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                        temp_audio_file.write(audio_file.read())
                        temp_file_path = temp_audio_file.name

                    # Use speech recognition to convert audio to text
                    with sr.AudioFile(temp_file_path) as source:
                        audio = recognizer.record(source)
                        transcript = recognizer.recognize_google(audio)

                    # Display the transcript in a generative way
                    st.markdown(f"<div class='user-message'>{transcript}</div>", unsafe_allow_html=True)

                    # Add user transcript to the action table
                    try:
                        completion = jamai.add_table_rows(
                            "action",
                            p.RowAddRequest(
                                table_id=TABLE_ID,
                                data=[{"user_input": transcript}],
                                stream=False
                            )
                        )

                        # Display the output generated in the "response", "casual_response", and "angry_response" columns
                        if completion.rows:
                            response_output = completion.rows[0].columns.get("response")
                            casual_response = completion.rows[0].columns.get("casual_response")
                            angry_response = completion.rows[0].columns.get("angry_response")
                            if response_output and casual_response and angry_response:
                                st.markdown(
                                    f"<div class='response-container'><h4>Response:</h4><p>{response_output.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    f"<div class='response-container'><h4>Casual Response:</h4><p>{casual_response.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    f"<div class='response-container'><h4>Angry Response:</h4><p>{angry_response.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error("No output found in the 'response', 'casual_response', or 'angry_response' columns.")
                        else:
                            st.error("Failed to get a response. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred while adding the transcript to the action table: {e}")

                except Exception as e:
                    st.error(f"An error occurred while processing the audio: {e}")
                finally:
                    if temp_file_path:
                        # Delete temporary file
                        os.remove(temp_file_path)

        elif input_choice == "Text":
            user_input_text = st.text_area("Enter your text below:")
            if st.button("Submit Text Input", key="text_submit_button"):
                if user_input_text:
                    # Add user input text to the action table
                    try:
                        completion = jamai.add_table_rows(
                            "action",
                            p.RowAddRequest(
                                table_id=TABLE_ID,
                                data=[{"user_input": user_input_text}],
                                stream=False
                            )
                        )

                        # Display the output generated in the "response", "casual_response", and "angry_response" columns
                        if completion.rows:
                            response_output = completion.rows[0].columns.get("response")
                            casual_response = completion.rows[0].columns.get("casual_response")
                            angry_response = completion.rows[0].columns.get("angry_response")
                            if response_output and casual_response and angry_response:
                                st.markdown(
                                    f"<div class='response-container'><h4>Response:</h4><p>{response_output.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    f"<div class='response-container'><h4>Casual Response:</h4><p>{casual_response.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    f"<div class='response-container'><h4>Angry Response:</h4><p>{angry_response.text.replace('**', '<strong>').replace('**', '</strong>')}</p></div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error("No output found in the 'response', 'casual_response', or 'angry_response' columns.")
                        else:
                            st.error("Failed to get a response. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred while adding the text input to the action table: {e}")
