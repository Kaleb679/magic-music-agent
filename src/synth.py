import asyncio
import fluidsynth


class Synth:
    """
    Async, idle-safe FluidSynth consumer.
    """

    def __init__(self,
                 soundfont: str = "soundfonts/FluidR3_GM.sf2",
                 driver: str = "coreaudio"):
        self.fs = fluidsynth.Synth(samplerate=44100)
        self.fs.start(driver=driver)
        sfid = self.fs.sfload(soundfont)
        self.fs.program_select(0, sfid, bank=0, preset=114)  # Steel Drums
        # self.fs.program_select(0, sfid, 0, 0)

        self.queue: asyncio.Queue[tuple[int, int, float]] = asyncio.Queue()
        self.running = False
        self.consumer_task: asyncio.Task | None = None

        self.fs.setting("synth.reverb.active", 1)
        self.fs.setting("synth.reverb.level", 0.7)
        self.fs.setting("synth.reverb.room-size", 0.8)
        
        

        
        print(f"✅ Synth ready with {soundfont}")

    # -------------------------------------------------------------
    
    async def start(self):
        """Start background consumer loop if not already running."""
        if self.running:
            return
        self.running = True
        self.consumer_task = asyncio.create_task(self._consume())
        print("🎧 Synth consumer started.")

    async def play(self, note: int, velocity: int = 100, duration: float = 0.4):
        """Queue a note for playback."""
        if not self.running:
            raise RuntimeError("Synth not started; call await start() first.")
        await self.queue.put((note, velocity, duration))

    async def _consume(self):
        """Continuously read notes from queue and play them."""
        try:
            while self.running:
                try:
                    note, vel, dur = await asyncio.wait_for(
                        self.queue.get(), timeout=0.05
                    )
                except asyncio.TimeoutError:
                    continue

                # play one note
                self.fs.noteon(0, note, vel)
                await asyncio.sleep(dur)
                self.fs.noteoff(0, note)
                self.queue.task_done()
        except asyncio.CancelledError:
            pass
        finally:
            # turn off any possible hanging notes
            for n in range(128):
                self.fs.noteoff(0, n)
            print("🧹 Consumer exited cleanly.")

    async def stop(self):
        """Stop playback even if idle."""
        if not self.running:
            return
        self.running = False
        # cancel consumer and wait for it to finish
        if self.consumer_task:
            self.consumer_task.cancel()
            try:
                await self.consumer_task
            except asyncio.CancelledError:
                pass
        self.fs.delete()
        print("🧩 Synth stopped.")
        self.consumer_task = None