import asyncio
import random

class RandomGenerator:
    """Async generator that feeds random notes to the synth."""

    def __init__(self, synth, tempo: float = 0.5):
        self.synth = synth
        self.tempo = tempo
        self._running = True

    async def run(self):
        print("Ai generator running...\n")
        try:
            while self._running:
                note = random.randint(48, 72)  # C3–C5 range
                vel = random.randint(70, 120)
                dur = random.uniform(0.3, 0.8)
                await self.synth.play(note, vel, dur)
                await asyncio.sleep(self.tempo)
        except asyncio.CancelledError:
            pass
        finally:
            print("Ai generator stopped.")