import asyncio
from abc import ABC, abstractmethod

class BaseGenerator(ABC):
    """
    Abstract base class for all AI or procedural note generators.
    """

    def __init__(self, synth, tempo: float = 120.0):
        self.synth = synth
        self.tempo = tempo
        self.active = False
        self._task: asyncio.Task | None = None

    @abstractmethod
    async def run(self):
        """Main coroutine for generating notes."""
        raise NotImplementedError

    async def start(self):
        """Begin generator loop."""
        if self.active:
            print("⚠️ Generator already running.")
            return
        self.active = True
        print(f"🧠 Starting generator: {self.__class__.__name__}")
        self._task = asyncio.create_task(self.run())

    async def stop(self):
        """Stop the generator gracefully."""
        if not self.active:
            return
        print(f"🛑 Stopping generator: {self.__class__.__name__}")
        self.active = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("✅ Generator stopped cleanly.")

    def beat_to_seconds(self, beats: float) -> float:
        """Convert musical beats to seconds using tempo."""
        return (60.0 / self.tempo) * beats