import asyncio
import fluidsynth


class Synth:
    """
    Async, polyphonic FluidSynth engine.
    Each note is spawned as its own asyncio task for overlapping playback.
    """

    def __init__(self,
                 soundfont: str = "soundfonts/FluidR3_GM.sf2",
                 driver: str = "coreaudio"):
        # Initialize FluidSynth backend
        self.fs = fluidsynth.Synth(samplerate=44100)
        self.fs.start(driver=driver)
        sfid = self.fs.sfload(soundfont)

        # 🎵 Preset: Steel Drums (metal bowl-like timbre)
        self.fs.program_select(0, sfid, bank=0, preset=114)

        # Configure acoustic properties
        self.fs.setting("synth.reverb.active", 1)
        self.fs.setting("synth.reverb.level", 0.8)
        self.fs.setting("synth.reverb.room-size", 0.9)
        self.fs.setting("synth.chorus.active", 1)
        self.fs.setting("synth.chorus.nr", 3)
        self.fs.setting("synth.chorus.level", 1.2)
        self.fs.setting("synth.chorus.speed", 0.25)

        # Runtime state
        self.running = False
        self.note_tasks: set[asyncio.Task] = set()

        print(f"✅ Synth ready with {soundfont} (Steel Drums preset)")

    # -------------------------------------------------------------
    async def start(self):
        """Mark the synth as active."""
        if self.running:
            return
        self.running = True
        print("🎧 Synth started (polyphonic async mode).")

    async def play(self, note: int, velocity: int = 100, duration: float = 0.4):
        """
        Play a note asynchronously — spawns a background note task.
        Multiple notes can overlap naturally.
        """
        if not self.running:
            raise RuntimeError("Synth not started; call await start() first.")

        # Ensure integer velocity for FluidSynth API
        velocity = int(velocity)

        # Launch note task
        task = asyncio.create_task(self._play_note(note, velocity, duration))
        self.note_tasks.add(task)

        # Cleanup finished tasks automatically
        task.add_done_callback(self.note_tasks.discard)

    async def _play_note(self, note: int, vel: int, dur: float):
        """Play a single note for the given duration."""
        try:
            self.fs.noteon(0, note, vel)
            await asyncio.sleep(dur)
        finally:
            self.fs.noteoff(0, note)

    async def stop(self):
        """Stop all active notes and cleanup."""
        if not self.running:
            return
        self.running = False

        # Cancel or await all remaining note tasks
        for task in list(self.note_tasks):
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.note_tasks, return_exceptions=True)
        self.note_tasks.clear()

        # Ensure no hanging notes
        for n in range(128):
            self.fs.noteoff(0, n)

        # Tear down the synth engine
        self.fs.delete()
        print("🧩 Synth stopped cleanly.")