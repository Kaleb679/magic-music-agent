import asyncio
from src.synth import Synth
from src.lib.generators.RandomGenerator import RandomGenerator
from src.lib.generators.MelodicGenerator import MelodicGenerator
# from src.lib.generators.RandomGenerator import RandomGenerator



class Controller:
    """
    High-level orchestrator for interactive or AI-driven synth control.
    Modes:
      - manual: waits for user note input
      - ai: runs AI generator coroutine
    """

    def __init__(self, mode: str = "manual"):
        self.mode = mode
        self.synth = Synth()
        self._input_task: asyncio.Task | None = None
        self._ai_task: asyncio.Task | None = None
        self._running = False

    # -------------------------------------------------------------
    async def start(self):
        """Boot the controller and start synth in chosen mode."""
        await self.synth.start()
        self._running = True

        print(f"🎛 Controller started in {self.mode.upper()} mode.")
        print("🧩 Synth engine online.\n")

        if self.mode == "manual":
            print("Type MIDI notes (0–127) or 'q' to quit.\n")
            await self._manual_loop()
        elif self.mode == "ai":
            print("Running AI generator. Press Ctrl+C to stop.\n")
            await self._ai_loop()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

    # -------------------------------------------------------------
    async def _manual_loop(self):
        """Manual keyboard input -> Synth."""
        loop = asyncio.get_running_loop()
        try:
            while self._running:
                user_input = await loop.run_in_executor(None, input, "note> ")

                if not user_input:
                    continue

                if user_input.lower() in {"q", "quit"}:
                    print("🛑 Quitting manual mode.")
                    break

                if user_input.isdigit():
                    note = int(user_input)
                    if 0 <= note <= 127:
                        await self.synth.play(note)
                    else:
                        print("⚠️ Note must be 0–127.")
                else:
                    print("⚠️ Invalid input.")
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    # -------------------------------------------------------------
    async def _ai_loop(self):
        """AI-driven generator loop (no manual input)."""
        generator = MelodicGenerator(self.synth)
        try:
            await generator.run()
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    # -------------------------------------------------------------
    async def stop(self):
        """Gracefully stop controller and synth."""
        if not self._running:
            return

        self._running = False
        print("🧩 Controller stopping...")

        await self.synth.stop()
        print("✅ Controller stopped cleanly.")