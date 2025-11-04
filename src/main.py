import asyncio
from src.controller import Controller

async def main():
    # Choose between 'manual' or 'ai' mode
    # mode = (input("Select mode (manual/ai): ").strip().lower()) or "manual"
    # if mode not in {"manual", "ai"}:
    #     print("⚠️ Invalid mode; defaulting to 'manual'.")
    #     mode = "manual"
    mode = "ai"
    controller = Controller(mode=mode)
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main())