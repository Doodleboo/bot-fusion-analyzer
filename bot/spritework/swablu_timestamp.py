from discord import Member, TextChannel, Thread

from bot.spritework.opt_out_options import HideAutoAnalysis


async def send_swablu_timestamp(user: Member, channel: TextChannel | Thread):
    timestamp_text = (f"This can be submitted to the gallery after: ")
    prompt_view = HideAutoAnalysis(user)
    view_message = await channel.send(content=timestamp_text, view=prompt_view)
    prompt_view.message = view_message