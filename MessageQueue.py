import asyncio
from collections import deque
from typing import Optional

from agent import Agent
from database import get_raw_message_by_id


class MessageQueue:
    def __init__(self):
        self.queue = deque()
        self.processing = False
        self.processor_task: Optional[asyncio.Task] = None

    async def add_queue(self, message_id):
        """Add a message_id to the queue and start processing if not already running"""
        self.queue.append(message_id)
        print(f"Added to queue: {message_id}. Queue size: {len(self.queue)}")

        # Start the processor if it's not already running
        if not self.processing:
            self.processor_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process messages from the queue every 4 seconds"""
        self.processing = True
        agent = Agent()

        try:
            while self.queue:
                # Get the next message from the queue
                message_id = self.queue.popleft()
                message = await asyncio.to_thread(get_raw_message_by_id, message_id)
                print(f"Processing: {message_id}")

                # Call Agent().ask() with the message
                try:
                    result = await agent.ask(message)
                    print(f"Result: {result}")
                except Exception as e:
                    print(f"Error processing message {message_id}: {e}")

                # Wait 4 seconds before processing the next message
                if self.queue:  # Only wait if there are more messages
                    await asyncio.sleep(4)
        finally:
            self.processing = False
            print("Queue processing finished")
