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
import aio_pika, asyncio, json
from copy import deepcopy
from datetime import datetime
import os
from config import env

RABBIT_URL = env.RABBIT_URL
QUEUE_NAME = env.QUEUE_NAME


class GLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
            cls._instance.channel = None
            try:
                cls._instance.loop = asyncio.get_event_loop()
            except RuntimeError:
                cls._instance.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(cls._instance.loop)
        return cls._instance

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
                print("[GLogger] WARN: Channel is not initialized.")
                return

            await self.channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(data).encode()),
                routing_key=QUEUE_NAME
            )
        except Exception as e:
            print(f"[GLogger] Error sending log: {e}")

    def log(self, user_id="", module="", order_id="", action_type="",
            old_status="", new_status="", remarks="", severity="INFO"):
        """Public log function (sync-safe)."""
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

        try:
            # Try running async function in sync environment
            self.loop.run_until_complete(self._send(log_entry))

        except RuntimeError:
            # In case loop is already running
            try:
                asyncio.create_task(self._send(log_entry))
            except Exception as e:
                print(f"[GLogger] Failed to create async task: {e}")

        except Exception as e:
            print(f"[GLogger] General log error: {e}")
