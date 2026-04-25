from datetime import datetime, timedelta

from discord import Member, TextChannel, Thread

from bot.misc.enums import OptedType
from bot.spritework.opt_out_options import HideFeature

MINIMUM_HOURS = 18

async def send_swablu_timestamp(user: Member, channel: TextChannel | Thread):
    posting_time = datetime.now() + timedelta(hours=MINIMUM_HOURS)
    epoch_time = int(posting_time.timestamp())
    timestamp_text = f"-# This sprite can be submitted to the gallery <t:{epoch_time}:R> (at <t:{epoch_time}:s>)"
    prompt_view = HideFeature(user, OptedType.timestamp)
    view_message = await channel.send(content=timestamp_text, view=prompt_view)
    prompt_view.message = view_message