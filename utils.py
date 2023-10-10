import asyncio
from datetime import datetime


async def delete_message(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


def get_timestamp():
    timestamp = int(datetime.now().timestamp())
    return f'<t:{timestamp}:R>'