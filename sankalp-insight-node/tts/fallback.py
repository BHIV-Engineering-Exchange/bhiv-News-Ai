import os
import pyttsx3

def simplify_text(text):
    t = (text or "").strip()
    if len(t) > 600:
        return t[:600]
    return t

def synthesize_local(text, voice="default", tone="calm", lang="en", out_path=None):
    eng = pyttsx3.init()
    rate = eng.getProperty('rate')
    if tone == "urgent":
        eng.setProperty('rate', int(rate * 1.2))
    elif tone == "calm":
        eng.setProperty('rate', int(rate * 0.9))
    voices = eng.getProperty('voices')
    chosen = None
    if voice and voice != "default":
        for v in voices:
            if voice.lower() in (v.id or '').lower() or voice.lower() in (v.name or '').lower():
                chosen = v
                break
    if not chosen:
        for v in voices:
            n = (v.name or '').lower()
            if lang.startswith('en') and 'english' in n:
                chosen = v
                break
    if chosen:
        eng.setProperty('voice', chosen.id)
    if out_path:
        eng.save_to_file(text, out_path)
        eng.runAndWait()
        return out_path
    eng.say(text)
    eng.runAndWait()
    return None