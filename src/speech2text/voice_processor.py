import re
import secrets
import string
from dataclasses import dataclass

import whisper
import huggingface_hub
from django.conf import settings
from pydub import AudioSegment
from pyannote.audio import Pipeline


SPEAKERS_TO_LETTERS = {
    "SPEAKER_00": "А",
    "SPEAKER_01": "Б",
    "SPEAKER_02": "В",
    "SPEAKER_03": "Г",
    "SPEAKER_04": "Д",
}


@dataclass
class Recording:
    path: str
    original_track_time_interval: tuple[str, str]
    original_track_time_interval_ms: tuple[int, int]
    speaker: str
    text: str


def time_str_to_millisecond(time_str):
    h, m, s = time_str.split(":")
    ms = int(
        (int(h) * 3600 + int(m) * 60 + float(s)) * 1000
    )
    return ms


def millisecond_to_time_str(ms):
    h = ms // (1000 * 3600)
    ms -= h * 1000 * 3600
    m = ms // (1000 * 60)
    ms -= m * 1000 * 60
    s = ms / 1000
    return f"{h}:{m}:{s}"


def transcribe_mp3_file(filename: str, binary_data: bytes):
    temp_dirname = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    temp_dir = settings.SPEECH2TEXT_TEMP_DIR / temp_dirname
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:

        with open(temp_dir / filename, "wb") as f:
            f.write(binary_data)

        spacer_millisecond = 2000

        spacer = AudioSegment.silent(duration=spacer_millisecond)
        audio = AudioSegment.from_mp3(temp_dir / filename)
        audio = spacer.append(audio, crossfade=0)
        filepath_wav = (temp_dir / filename).with_suffix('.wav')
        audio.export(filepath_wav, format="wav")

        huggingface_hub.login(token=settings.HUGGINGFACE_API_TOKEN)
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization", use_auth_token=True,

        )

        dz = pipeline({"uri": "blabla", "audio": filepath_wav})
        dz = dz.rename_labels(SPEAKERS_TO_LETTERS)

        with open(temp_dir / "diarization.txt", "w") as text_file:
            text_file.write(str(dz))
        with open(temp_dir / "diarization.txt") as f:
            dzs = f.read().splitlines()

        groups = []
        g = []
        last_end = 0

        for d in dzs:
            if g and (g[0].split()[-1] != d.split()[-1]):  # same speaker
                groups.append(g)
                g = []

            g.append(d)

            end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
            end = time_str_to_millisecond(end)
            if last_end > end:  # segment engulfed by a previous segment
                groups.append(g)
                g = []
            else:
                last_end = end
        if g:
            groups.append(g)

        audio = AudioSegment.from_wav(filepath_wav)
        gidx = -1
        speeches = []
        model = whisper.load_model("small")

        for g in groups:
            start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
            end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
            start_ms = time_str_to_millisecond(start)  # - spacer_millisecond
            end_ms = time_str_to_millisecond(end)  # - spacer_millisecond
            gidx += 1
            audio[start_ms:end_ms].export(temp_dir / f'{gidx}.wav', format='wav')
            result = model.transcribe(str(temp_dir / f'{gidx}.wav'), language="ru", fp16=False)
            speeches.append(
                {
                    "start": millisecond_to_time_str(start_ms - spacer_millisecond),
                    "end": millisecond_to_time_str(end_ms - spacer_millisecond),
                    "speaker": g[0].split()[-1],
                    "text": result["text"]
                }
            )
    finally:
        for f in temp_dir.glob('*'):
            f.unlink()
        temp_dir.rmdir()
    print(speeches)
    return speeches
