import asyncio
import random
import math
from src.lib.generators.BaseGenerator import BaseGenerator


def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


class MelodicGenerator(BaseGenerator):
    """
    Produces coherent, metallic-bowl melodic textures using
    minor pentatonic modal cells and soft arpeggiation.
    """

    def __init__(self, synth, tempo: float = 90.0, root_note: int = 60):
        super().__init__(synth, tempo)
        self.root_note = root_note
        self.scale = [0, 3, 5, 7, 10, 12]  # A minor pentatonic intervals
        self.octaves = [-12, 0, 12]
        self.max_polyphony = 4

    async def run(self):
        print(f"🎶 MelodicGenerator running at {self.tempo} BPM\n")
        self.active = True
        beat = 60.0 / self.tempo

        try:
            while self.active:
                # Select a tonal center and motif length
                base = self.root_note + random.choice(self.octaves)
                motif_len = random.randint(4, 8)

                # Occasionally play a resonant base hit (like a handpan)
                if random.random() < 0.25:
                    await self._strike_bowl(base - 12, beat * 2.0)

                # Create short melodic phrases
                for i in range(motif_len):
                    if not self.active:
                        break

                    interval = random.choice(self.scale)
                    note = clamp(base + interval, 36, 84)
                    velocity = int(80 + 40 * math.sin(i / 2.0))
                    dur_beats = random.choice([0.25, 0.5, 1.0])
                    dur_sec = self.beat_to_seconds(dur_beats)

                    # Staggered async layering for smooth shimmer
                    asyncio.create_task(
                        self.synth.play(note, velocity=velocity, duration=dur_sec)
                    )

                    await asyncio.sleep(dur_sec * random.choice([0.5, 0.75, 1.0]))

                # Pause between phrases (musical breathing)
                await asyncio.sleep(random.uniform(0.5, 2.0) * beat)

        except asyncio.CancelledError:
            print("🧩 MelodicGenerator loop canceled.")
        finally:
            print("✅ MelodicGenerator stopped cleanly.")
            self.active = False

    async def _strike_bowl(self, note: int, duration: float):
        """Low resonant strike accent."""
        note = clamp(note, 36, 72)
        vel = random.randint(90, 120)
        asyncio.create_task(self.synth.play(note, velocity=vel, duration=duration))
        await asyncio.sleep(duration * 0.3)