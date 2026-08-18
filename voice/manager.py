import threading
from pathlib import Path

from voice.tts import PiperTTS


class VoiceManager:

    def __init__(self) -> None:
        model = (
            Path(__file__).parent
            / "voices"
            / "es_ES-sharvard-medium.onnx"
        )

        self.engine = PiperTTS(model)

    def speak(
        self,
        text: str,
    ) -> None:
        if not text.strip():
            return

        self.engine.speak(text)

    def speak_async(
        self,
        text: str,
    ) -> None:
        threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True,
        ).start()
