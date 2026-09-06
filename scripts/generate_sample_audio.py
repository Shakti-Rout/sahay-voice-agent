import io
import math
import wave
import struct
from pathlib import Path


def create_sample_wav(output_path: Path, frequency: float, duration_s: float = 2.0, tremor: bool = False):
    """Generate a clean PCM WAV audio file with specified acoustics."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    num_samples = int(sample_rate * duration_s)

    with wave.open(str(output_path), "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        for i in range(num_samples):
            envelope = min(1.0, i / 1000) * min(1.0, (num_samples - i) / 1000)
            f_inst = frequency
            if tremor:
                # Add 8Hz tremor frequency modulation
                f_inst += 15.0 * math.sin(2 * math.pi * 8 * (i / sample_rate))

            sample = int(4000 * envelope * math.sin(2 * math.pi * f_inst * (i / sample_rate)))
            wav.writeframesraw(struct.pack("<h", sample))

    print(f"[Generated] {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent / "data" / "test_audio"

    # 1. Odia Threat Audio (High pitch with tremor)
    create_sample_wav(base_dir / "odia" / "threat_01.wav", frequency=280.0, duration_s=2.5, tremor=True)

    # 2. Hindi Calm Audio (Steady low pitch)
    create_sample_wav(base_dir / "hindi" / "calm_01.wav", frequency=140.0, duration_s=2.0, tremor=False)

    # 3. English Distress Audio (Modulated pitch)
    create_sample_wav(base_dir / "english" / "distress_01.wav", frequency=240.0, duration_s=2.0, tremor=True)

    print("Sample test audio generation complete.")
