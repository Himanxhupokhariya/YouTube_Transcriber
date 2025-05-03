# Copy youtube link address after than paste the link the search bar
# remove all part after '&' from the link
# run code with streamlit run appp.py(filename)

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # Load all the environment variables
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


# Configure Gemini Pro
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}.  Please ensure you have set the GOOGLE_API_KEY environment variable.")
    st.stop()


prompt = """You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


# Getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID robustly
        parsed_url = urlparse(youtube_video_url)
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            video_id = query_params['v'][0]
        else:
            raise ValueError("Invalid YouTube URL:  Video ID ('v' parameter) not found.")


        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        st.error(f"Error extracting transcript: {e}") # Corrected: Display error in Streamlit
        return None  #Crucial: Return None in case of error. This avoids further errors downstream.


# Getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary with Gemini: {e}")
        return None  #Crucial: Return None if Gemini fails.


st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        # Extract video ID robustly
        parsed_url = urlparse(youtube_link)
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            video_id = query_params['v'][0]
        else:
            st.error("Invalid YouTube URL:  Video ID ('v' parameter) not found.")
            video_id = None # crucial for stopping execution later.
        if video_id: # only proceed if video_id is valid.
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying YouTube thumbnail: {e}")
        video_id = None  #  Need to set video_id to None for error handling

if st.button("Get Detailed Notes"):
    if youtube_link: # Added check: Only proceed if a YouTube link is provided.
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:  # Check if transcript_text is not None before proceeding
            summary = generate_gemini_content(transcript_text, prompt)

            if summary: #Check for None returned from Gemini
                st.markdown("## Detailed Notes:")
                st.write(summary)
            else:
                st.error("Failed to generate summary. Check console for errors.")
        else:
            st.error("Failed to extract transcript.  Check console for errors and ensure a valid YouTube link is provided.")
    else:
        st.warning("Please enter a YouTube video link.")
