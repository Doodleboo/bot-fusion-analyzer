import datetime
from discord import Embed, Message, Thread


async def get_spritework_thread_times(message: Message) -> Embed:
    description = ""
    channel_mentions = message.channel_mentions
    for spritework_thread in channel_mentions:
        if not isinstance(spritework_thread, Thread):
            continue
        creation_date = spritework_thread.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        time_delta = now - creation_date
        if time_delta.days >= 1:
            description += f"**{spritework_thread.name}**: created **over a day ago**\n"
        else:
            hours_delta = time_delta.seconds / 3600
            if (hours_delta >= 1) and (hours_delta < 2):
                hours = "hour"
            else:
                hours = "hours"
            description += f"**{spritework_thread.name}**: created **{hours_delta:.0f} {hours} ago**\n"

    if description == "":
        description = "No linked threads have been found.\nPerhaps they were linked directly instead of using #"

    return Embed(title="Spritework thread creation dates", description=description)