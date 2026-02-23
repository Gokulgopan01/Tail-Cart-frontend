# # glogger.py
# import aio_pika, asyncio, json
# from copy import deepcopy
# from datetime import datetime
# import os
# from config import env

# RABBIT_URL = env.RABBIT_URL
# QUEUE_NAME = env.QUEUE_NAME
# connection = None
# channel = None


# class GLogger:
#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance.connection = None
#             cls._instance.channel = None
#             cls._instance.loop = asyncio.get_event_loop()
#         return cls._instance

#     async def _init_rabbit(self):
#         if not self.connection or self.connection.is_closed:
#             self.connection = await aio_pika.connect_robust(RABBIT_URL)
#             self.channel = await self.connection.channel()
#             await self.channel.declare_queue(QUEUE_NAME, durable=True)

#     async def _send(self, data):
#         await self._init_rabbit()
#         await self.channel.default_exchange.publish(
#             aio_pika.Message(body=json.dumps(data).encode()),
#             routing_key=QUEUE_NAME
#         )

#     def log(self, user_id="", module="", order_id="", action_type="", old_status="", new_status="", remarks="", severity="INFO"):
#         """This is the function other files can call directly (sync)."""
#         log_entry = {
#             "user_id": user_id,
#             "module": module,
#             "order_id": order_id,
#             "action_type": action_type,
#             "old_status": old_status,
#             "new_status": new_status,
#             "remarks": remarks,
#             "severity": severity,
#             "timestamp": datetime.now().isoformat()
#         }
#         # Run async send in the event loop
#         try:
#             self.loop.run_until_complete(self._send(log_entry))
#         except RuntimeError:
#             # If loop is already running (e.g., inside asyncio app), create a task instead
#             asyncio.create_task(self._send(log_entry))
#Glogger
import aio_pika, asyncio, json, threading
from datetime import datetime
from config import env

RABBIT_URL = env.RABBIT_URL
QUEUE_NAME = env.QUEUE_NAME

class GLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.connection = None
                cls._instance.channel = None
                cls._instance.loop = None
                cls._instance._start_background_loop()
        return cls._instance

    def _start_background_loop(self):
        """Starts a background thread to run a dedicated asyncio event loop."""
        self.ready_event = threading.Event()
        thread = threading.Thread(target=self._run_loop, daemon=True, name="GLoggerThread")
        thread.start()
        self.ready_event.wait() # Wait for loop to be initialized

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ready_event.set()
        self.loop.run_forever()

    async def _init_rabbit(self):
        """Initialize RabbitMQ connection and channel."""
        try:
            if not self.connection or self.connection.is_closed:
                self.connection = await aio_pika.connect_robust(RABBIT_URL)
                self.channel = await self.connection.channel()
                await self.channel.declare_queue(QUEUE_NAME, durable=True)
        except Exception as e:
            print(f"[GLogger] RabbitMQ init error: {e}")

    async def _send(self, data):
        """Send log message to RabbitMQ."""
        try:
            await self._init_rabbit()
            if not self.channel:
                return

            await self.channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(data).encode()),
                routing_key=QUEUE_NAME
            )
        except Exception as e:
            print(f"[GLogger] Error sending log: {e}")

    def log(self, user_id="", module="", order_id="", action_type="",
            old_status="", new_status="", remarks="", severity="INFO"):
        """Public log function (completely non-blocking)."""
        log_entry = {
            "user_id": user_id,
            "module": module,
            "order_id": order_id,
            "action_type": action_type,
            "old_status": old_status,
            "new_status": new_status,
            "remarks": remarks,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }

        if self.loop and self.loop.is_running():
            # Schedule the coroutine in the background loop safely
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._send(log_entry))
            )
        else:
            print("[GLogger] WARN: Background loop is not running.")
