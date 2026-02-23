
import sys
import os
import time
import asyncio

# Add current directory to path so we can import utils
sys.path.append(os.getcwd())

from utils.glogger import GLogger
from config import env

def test_log():
    print(f"Testing GLogger with URL: {env.RABBIT_URL}")
    print(f"Queue Name: {env.QUEUE_NAME}")
    
    logger = GLogger()
    
    print("Sending test log...")
    logger.log(
        module="TestModule",
        order_id="TEST_123",
        action_type="TestConnection",
        remarks="Testing if logs reach RabbitMQ",
        severity="INFO"
    )
    
    print("Log call made. Waiting 5 seconds for background thread to process...")
    # Give it some time to connect and send
    time.sleep(5)
    print("Done. If there were errors, they should have been printed above.")

if __name__ == "__main__":
    test_log()
