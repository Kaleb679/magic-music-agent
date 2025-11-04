# src/lib/generators/RandomGenerator.py
import asyncio
import random
from src.lib.generators.BaseGenerator import BaseGenerator


class RandomGenerator(BaseGenerator):
    """Simple procedural generator that plays random notes."""

    async def run(self):
        try:
            while self.active:
                note = random.randint(40, 80)
                velocity = random.uniform(0.5, 1.0)
                print(f"🎵 Playing random note {note} (vel={velocity:.2f})")
                await self.synth.play(note)
                await asyncio.sleep(60.0 / self.tempo)  # delay per beat
        except asyncio.CancelledError:
            print("🧩 RandomGenerator loop canceled.")