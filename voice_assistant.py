import subprocess
import textwrap

VOICE_ENABLED = True

WELCOME_MESSAGE = (
    "সম্রাট ভাই YT টুলে আপনাকে স্বাগতম... "
    "আশা করি, আমাদের এই টুলটি আপনার ভালো লাগবে। "
    "চাইলে অবসর সময়ে সম্রাট ভাই YT-এর ইউটিউব চ্যানেলটিও ঘুরে দেখতে পারেন... "
    "আপনাকে অসংখ্য ধন্যবাদ... এবং শুভকামনা রইল।"
)

def speak(text):
    if not VOICE_ENABLED or not text:
        return

    text = str(text).strip()
    if not text:
        return

    chunks = textwrap.wrap(
        text,
        width=350,
        break_long_words=False,
        break_on_hyphens=False
    )

    try:
        for chunk in chunks:
            subprocess.run(
                ["termux-tts-speak", chunk],
                timeout=60,
                check=False
            )
    except Exception:
        pass

def speak_result(text):
    speak("ফলাফল। " + str(text))

def speak_warning(text):
    speak("সতর্কবার্তা। " + str(text))

def speak_error(text):
    speak("সমস্যা হয়েছে। " + str(text))

def welcome():
    speak(WELCOME_MESSAGE)

def toggle_voice():
    global VOICE_ENABLED
    VOICE_ENABLED = not VOICE_ENABLED
    return VOICE_ENABLED
