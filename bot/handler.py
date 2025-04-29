import asyncio

import discord
import utils
from discord import Message, Thread, HTTPException, PartialEmoji
from bot.analysis import generate_bonus_file
from bot.analyzer import send_bot_logs, generate_analysis
from bot.setup import ctx
from bot.enums import AnalysisType, Severity
from bot.message_identifier import is_assets_gallery
from bot.spritework_checker import get_spritework_thread_times


ERROR_EMOJI_NAME = "NANI"
ERROR_EMOJI_ID = f"<:{ERROR_EMOJI_NAME}:770390673664114689>"
ERROR_EMOJI = PartialEmoji(name=ERROR_EMOJI_NAME).from_str(ERROR_EMOJI_ID)
MAX_SEVERITY = [Severity.refused, Severity.controversial]


# Handler methods

async def handle_sprite_gallery(message: Message):
    await handle_gallery(message, is_assets=False)


async def handle_assets_gallery(message: Message):
    await handle_gallery(message, is_assets=True)


async def handle_gallery(message: Message, is_assets: bool = False):
    if is_assets:
        utils.log_event("Assets Gallery>", message)
    else:
        utils.log_event("Sprite Gallery>", message)

    for specific_attachment in message.attachments:
        if is_assets:
            analysis_type = AnalysisType.assets_gallery
        else:
            analysis_type = AnalysisType.sprite_gallery
        analysis = generate_analysis(message, specific_attachment, analysis_type)
        if analysis.severity in MAX_SEVERITY:
            try:
                await message.add_reaction(ERROR_EMOJI)
            except HTTPException:
                await message.add_reaction("😡")  # Nani failsafe
        try:
            await send_bot_logs(analysis, message.author.id)
        except HTTPException:  # Rate limit
            await asyncio.sleep(300)
            await send_bot_logs(analysis, message.author.id)


async def handle_zigzag_galpost(message: Message):
    utils.log_event("Zigzag>", message)

    if is_assets_gallery(message):
        analysis_type = AnalysisType.zigzag_base
    else:
        analysis_type = AnalysisType.zigzag_fusion

    analysis = generate_analysis(message, specific_attachment=None, analysis_type=analysis_type)
    if analysis.severity == Severity.refused:       # Controversial won't ping
        ping_zigzagoon = "<@&1182898845563228232>"
        await ctx().pif.logs.send(embed=analysis.embed, content=ping_zigzagoon)
    else:
        await ctx().pif.logs.send(embed=analysis.embed)


async def handle_reply_message(message: Message):
    utils.log_event("Reply>", message.channel)
    channel = message.channel
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, AnalysisType.ping_reply)
        try:
            await channel.send(embed=analysis.embed)
            if analysis.transparency_issue:
                await channel.send(
                    embed=analysis.transparency_embed,
                    file=generate_bonus_file(analysis.transparency_image)
                )
            if analysis.half_pixels_issue:
                await channel.send(
                    embed=analysis.half_pixels_embed,
                    file=generate_bonus_file(analysis.half_pixels_image)
                )
        except discord.Forbidden:
            print(f"Reply> Missing permissions in {channel}")


async def handle_spriter_application(thread: Thread):
    await asyncio.sleep(10)
    try:
        application_message = await thread.fetch_message(thread.id)
    except discord.errors.NotFound:
        last_message_id = thread.last_message_id
        try:
            application_message = await thread.fetch_message(last_message_id)
        except discord.errors.NotFound:
            await ctx().doodledoo.debug.send("Discord returned Not Found twice")
            return
    except discord.errors.Forbidden:
        await ctx().doodledoo.debug.send("Discord returned Forbidden while fetching thread message")
        return
    if application_message is None:
        await ctx().doodledoo.debug.send("Could not fetch message on thread creation")
        return
    print("Spriter Application>", application_message.channel)
    try:
        await handle_reply_message(application_message)
        await handle_spritework_thread_times(application_message)
    except Exception as message_exception:
        print(" ")
        print(application_message)
        print(" ")
        await ctx().doodledoo.debug.send(
            f"ERROR in #{application_message.channel} ({application_message.jump_url})")
        raise RuntimeError from message_exception


async def handle_spritework_thread_times(message: Message):
    times_embed = await get_spritework_thread_times(message)
    try:
        await message.channel.send(embed=times_embed)
    except discord.Forbidden:
        print(f"Spriter Application> Missing permissions in {message.channel}")


async def handle_reply(message: Message):
    reply_message = await utils.get_reply_message(message)
    await handle_reply_message(reply_message)
