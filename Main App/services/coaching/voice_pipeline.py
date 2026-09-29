import time
import streamlit as st
from services.coaching.form_rules import find_form_issue


class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0

    def _find_form_issue(self, exercise, metrics):
        return find_form_issue(exercise, metrics)

    def process_event(self, event, exercise, metrics):
        issue = self._find_form_issue(exercise, metrics)

        now = time.time()

        is_major_issue = event in ["workout_started", "set_completed", "workout_completed"]

        if not is_major_issue:
            if not issue:
                return None
            
            if now - self.last_spoken_at < 5:
                return None
            
        # Mark as spoken even if the call fails, so a network problem doesn't retry every frame
        self.last_spoken_at = now

        try:
            text = self.llm.give_feedback(event, issue)
        except Exception as e:
            print(f"[VoicePipeline] AI coach unavailable: {e}")
            return None

        try:
            voice = self.tts.speak(text)
        except Exception as e:
            print(f"[VoicePipeline] Text-to-speech failed: {e}")
            voice = None

        return voice, text
    

def autoplay_audio(audio_bytes):
    if not audio_bytes:
        return
    
    st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
    
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
