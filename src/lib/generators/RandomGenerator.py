import asyncio
import random
from src.lib.generators.BaseGenerator import BaseGenerator


class RandomGenerator(BaseGenerator):
    """
    Simple procedural generator that emits random notes.
    """

    async def run(self):
        print(f"Ai generator running...\n")
        self.active = True  # Ensure the loop actually runs
        try:
            while self.active:
                # Random note range (MIDI 40–80 = roughly E2–G5)
                note = random.randint(40, 80)

                # Random velocity (0.5–1.0 scaled to 0–127)
                velocity = int(random.uniform(0.5, 1.0) * 127)

                # Random rhythmic length (quarter, half, whole)
                beats = random.choice([1.0, 3.0, 6.0, 12.0])
                duration = self.beat_to_seconds(beats)

                print(f"🎵 Playing note {note} | vel={velocity} | dur={duration:.2f}s")

                # Send note to synth
                await self.synth.play(note, velocity=velocity, duration=duration)

                # Short delay before generating next note
                await asyncio.sleep(duration * 0.25)

        except asyncio.CancelledError:
            print("🧩 RandomGenerator loop canceled.")
        finally:
            self.active = False
            print("✅ RandomGenerator stopped cleanly.")