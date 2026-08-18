from pathlib import Path
import subprocess
import tempfile
import wave

from piper import PiperVoice


class PiperTTS:

    def __init__(
        self,
        model_path: str | Path,
    ) -> None:
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo no encontrado: {self.model_path}"
            )

        self.voice = PiperVoice.load(
            str(self.model_path)
        )

    def save(
        self,
        text: str,
        output: str | Path,
    ) -> None:

        with wave.open(
            str(output),
            "wb",
        ) as wav:

            self.voice.synthesize_wav(
                text,
                wav,
            )

    def speak(
        self,
        text: str,
    ) -> None:

        if not text.strip():
            return

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=True,
        ) as temp:

            self.save(
                text,
                temp.name,
            )

            subprocess.run(
                [
                    "pw-play",
                    temp.name,
                ],
                check=True,
            )
