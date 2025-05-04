import datetime
import re
import math

from aiohttp.abc import HTTPException
from discord import Embed, Message, Thread, Forbidden, NotFound, HTTPException

from bot.setup import get_bot_client, ctx

CHANNEL_URL_PATTERN = r"discord\.com/channels/(\d+)/(\d+)"

async def get_spritework_thread_times(message: Message) -> Embed:
    description = ""
    channel_mentions = message.channel_mentions
    if not channel_mentions:
        channel_mentions = await get_threads_from_urls_in_message(message)
    for spritework_thread in channel_mentions:
        if not isinstance(spritework_thread, Thread):
            continue
        creation_date = spritework_thread.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        time_delta = now - creation_date
        if time_delta.days >= 1:
            description += f"**{spritework_thread.name}**: created **over a day ago**\n"
        else:
            hours_delta = math.floor(time_delta.seconds / 3600)
            if (hours_delta >= 1) and (hours_delta < 2):
                hours = "hour"
            else:
                hours = "hours"
            description += f"**{spritework_thread.name}**: created **{hours_delta:.0f} {hours} ago**\n"

    if description == "":
        description = "No linked threads have been found."

    return Embed(title="Spritework thread creation dates", description=description)


async def get_threads_from_urls_in_message(message: Message) -> list[Thread]:
    urls = re.finditer(CHANNEL_URL_PATTERN, message.content)
    threads = []
    # Format: discord.com/channels/SERVER_ID/THREAD_ID
    for url_match in urls:
        url_string = url_match.group(0)
        url_parts = url_string.split("/")
        if len(url_parts) < 4:
            continue
        client = get_bot_client()
        thread_id = url_parts[3]
        try:
            linked_thread = await client.fetch_channel(thread_id)
        except (HTTPException, NotFound, Forbidden) as exception:
            error_message = f"Exception {exception} retrieving linked thread {thread_id}"
            print(error_message)
            await ctx().doodledoo.debug.send(error_message)
            continue

        if isinstance(linked_thread, Thread):
            threads.append(linked_thread)

    return threads
