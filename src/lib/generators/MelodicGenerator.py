# src/lib/generators/MelodicGenerator.py
import asyncio
import random
import math
from typing import Optional, List, Tuple
from src.lib.generators.BaseGenerator import BaseGenerator


# --------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------- #

def clamp(value: int, lo: int, hi: int) -> int:
    """Clamp numeric value to [lo, hi]."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


# --------------------------------------------------------------------- #
# MelodicGenerator v3 — Harmonic + Melodic async generator
# --------------------------------------------------------------------- #

class MelodicGenerator(BaseGenerator):
    """
    Async procedural generator with both harmonic and melodic structure.
    - Produces evolving, handpan-like metallic textures.
    - Adds chord layers and soft voicing under melodic phrases.
    - Safe for async playback with the existing Synth queue.
    """

    LOW_LIMIT = 20   # C2
    HIGH_LIMIT = 71  # C5
    DEFAULT_TEMPO_MIN = 68.0
    DEFAULT_TEMPO_MAX = 115.0

    MODES: List[Tuple[int, List[int]]] = [
        (0,  [0, 3, 5, 7, 10]),   # Aeolian pentatonic
        (2,  [0, 2, 5, 7, 9]),    # Dorian
        (5,  [0, 3, 5, 8, 10]),   # Phrygian
    ]

    CHORD_PATTERNS = [
        [0, 3],     # minor triad
        [0, 5,],    # sus2 / add9
        [0, 7],    # fifth & octave
        [0, 3],    # minor 7th color
        [0, 5],     # airy 6th color
    ]

    def __init__(self, synth, tempo: float = 84.0, root_note: int = 60):
        super().__init__(synth, tempo)
        self.root_note = root_note
        self.scale = [0, 3, 5, 7, 10]
        self.octaves = [-24, -12, 0]
        self._bg_drone_task: Optional[asyncio.Task] = None
        self._recent_notes: List[int] = []
        self._phrase_memory: List[int] = []
        self._section_clock = 0
        self._section = "intro"
        self._density = 0.6
        self._vel_center = 90
        self._dur_choice = [0.5, 0.75, 1.0]
        self._dyad_prob = 0.18
        self._bowl_prob = 0.25
        self._chord_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------ #
    # MAIN RUN LOOP
    # ------------------------------------------------------------------ #

    async def run(self):
        print(f"🎶 MelodicGenerator v3 @ {self.tempo:.1f} BPM  |  Pitch band [{self.LOW_LIMIT}–{self.HIGH_LIMIT}]\n")
        self.active = True
        self._bg_drone_task = asyncio.create_task(self._background_drone())

        try:
            while self.active:
                await self._bar()
        except asyncio.CancelledError:
            print("🧩 MelodicGenerator loop canceled.")
        finally:
            await self._stop_bg_drone()
            await self._stop_chord_layer()
            print("✅ MelodicGenerator stopped cleanly.")
            self.active = False

    # ------------------------------------------------------------------ #
    # MAIN BAR STRUCTURE
    # ------------------------------------------------------------------ #

    async def _bar(self):
        """Each bar can contain a chord layer + melodic motion."""
        beat = 60.0 / self.tempo
        base = clamp(self.root_note + random.choice(self.octaves), self.LOW_LIMIT, self.HIGH_LIMIT)

        # Launch new chord layer occasionally
        if not self._chord_task or self._chord_task.done():
            if random.random() < 0.9:
                await self._launch_chord(base, beat)

        # Play 1–2 melodic phrases on top of the current harmony
        for _ in range(random.choice([1, 2])):
            await self._phrase(base, beat)

        # Add low bowl hit occasionally
        if random.random() < self._bowl_prob:
            await self._strike_bowl(base - 12, beat * 2.5)

        await asyncio.sleep(beat * random.uniform(0.5, 1.2))

    # ------------------------------------------------------------------ #
    # CHORD ENGINE
    # ------------------------------------------------------------------ #

    async def _launch_chord(self, base: int, beat: float):
        """Launch a slow chord pad as an async task."""
        pattern = random.choice(self.CHORD_PATTERNS)
        dur = self.beat_to_seconds(random.choice([4.0, 6.0, 8.0]))
        vel = random.randint(65, 90)
        chord_notes = [clamp(base + i, self.LOW_LIMIT, self.HIGH_LIMIT) for i in pattern]

        async def play_chord(notes, velocity, duration):
            """Play sustained chord with gentle delay between attacks."""
            delay = 0.05
            for note in notes:
                asyncio.create_task(self.synth.play(note, velocity=velocity, duration=duration))
                await asyncio.sleep(delay)
            await asyncio.sleep(duration)

        self._chord_task = asyncio.create_task(play_chord(chord_notes, vel, dur))

    async def _stop_chord_layer(self):
        """Stop chord layer task if running."""
        if self._chord_task:
            self._chord_task.cancel()
            try:
                await self._chord_task
            except asyncio.CancelledError:
                pass
            self._chord_task = None

    # ------------------------------------------------------------------ #
    # MELODIC PHRASE GENERATOR
    # ------------------------------------------------------------------ #

    async def _phrase(self, base_note: int, beat: float):
        motif_len = random.randint(4, 8)
        energy = random.random()
        vel_center = int(lerp(80, 104, energy))
        dur_pool = [0.25, 0.5, 0.75, 1.0]

        for i in range(motif_len):
            if not self.active:
                break
            interval = random.choice(self.scale)
            note = clamp(base_note + interval, self.LOW_LIMIT, self.HIGH_LIMIT)

            # Optional octave lift
            if random.random() < 0.2:
                note += 12

            velocity = clamp(int(vel_center + 18 * math.sin(i / 2.0)), 60, 115)
            dur_beats = random.choice(dur_pool)
            dur_sec = self.beat_to_seconds(dur_beats)

            # Add harmonic color — fifth or suspended tone
            if random.random() < 0.25:
                color = clamp(note + random.choice([7, 5, 10]), self.LOW_LIMIT, self.HIGH_LIMIT)
                asyncio.create_task(self.synth.play(color, velocity=max(60, velocity - 15), duration=dur_sec * 1.2))

            asyncio.create_task(self.synth.play(note, velocity=velocity, duration=dur_sec))
            await asyncio.sleep(dur_sec * random.uniform(0.6, 1.0))

        await asyncio.sleep(beat * random.uniform(0.3, 0.8))

    # ------------------------------------------------------------------ #
    # BACKGROUND DRONE + LOW STRIKES
    # ------------------------------------------------------------------ #

    async def _background_drone(self):
        """Low pedal tones for depth."""
        try:
            while self.active:
                base = clamp(self.root_note - 24, self.LOW_LIMIT, self.HIGH_LIMIT)
                fifth = clamp(base + 7, self.LOW_LIMIT, self.HIGH_LIMIT)
                dur = self.beat_to_seconds(random.choice([8.0, 12.0, 16.0]))
                v1 = random.randint(60, 76)
                asyncio.create_task(self.synth.play(base, velocity=v1, duration=dur))
                if random.random() < 0.5:
                    asyncio.create_task(self.synth.play(fifth, velocity=max(55, v1 - 10), duration=dur * 0.9))
                await asyncio.sleep(dur * random.uniform(0.8, 1.2))
        except asyncio.CancelledError:
            pass

    async def _stop_bg_drone(self):
        if self._bg_drone_task:
            self._bg_drone_task.cancel()
            try:
                await self._bg_drone_task
            except asyncio.CancelledError:
                pass
            self._bg_drone_task = None

    async def _strike_bowl(self, note: int, duration: float):
        note = clamp(note, self.LOW_LIMIT, self.HIGH_LIMIT)
        vel = random.randint(92, 115)
        asyncio.create_task(self.synth.play(note, velocity=vel, duration=duration))
        await asyncio.sleep(duration * 0.25)