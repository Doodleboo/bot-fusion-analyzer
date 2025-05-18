import asyncio

import discord
import utils
from discord import Message, Thread, HTTPException, PartialEmoji
from analysis import generate_file_from_image, Analysis, get_autogen_file
from analyzer import send_full_analysis, generate_analysis
from issues import DifferentSprite # If the package is named bot.issues, Python thinks they're different types
from bot.setup import ctx
from enums import AnalysisType, Severity
from message_identifier import is_assets_gallery
from spritework_checker import get_spritework_thread_times


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

        if analysis.issues.has_issue(DifferentSprite):
            await handle_misnumbered_in_gallery(message, analysis)
            return

        if analysis.severity in MAX_SEVERITY:
            try:
                await message.add_reaction(ERROR_EMOJI)
            except HTTPException:
                await message.add_reaction("😡")  # Nani failsafe
        try:
            await send_full_analysis(analysis, ctx().pif.logs, message.author)
        except HTTPException:  # Rate limit
            await asyncio.sleep(300)
            await send_full_analysis(analysis, ctx().pif.logs, message.author)


async def handle_zigzag_galpost(message: Message):
    print("Zigzag> " + message.embeds[0].title)

    if is_assets_gallery(message):
        analysis_type = AnalysisType.zigzag_base
    else:
        analysis_type = AnalysisType.zigzag_fusion

    analysis = generate_analysis(message, specific_attachment=None, analysis_type=analysis_type)
    if analysis.severity == Severity.refused:       # Controversial won't ping
        zigzagoon_message = "This Zigzag galpost seems to have issues. If this is incorrect, contact Doodledoo."
        await ctx().pif.zigzagoon.send(embed=analysis.embed, content=zigzagoon_message)
    else:
        await ctx().pif.logs.send(embed=analysis.embed)


async def handle_reply_message(message: Message):
    channel = message.channel
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, AnalysisType.ping_reply)
        try:
            await send_full_analysis(analysis, message.channel, message.author)
        except discord.Forbidden:
            await ctx().doodledoo.debug.send(f"Missing permissions in {channel.name}: {channel.jump_url}")


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
    utils.log_event("Spriter Application>", application_message)
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
    utils.log_event("Reply>", reply_message)
    await handle_reply_message(reply_message)


async def handle_misnumbered_in_gallery(message: Message, analysis: Analysis):
    misnumbered_issue = None
    for issue in analysis.issues.issue_list:
        if isinstance(issue, DifferentSprite):
            misnumbered_issue = issue
            break

    if misnumbered_issue is None:
        return

    copied_message = await ctx().pif.logs.send(f"Hi {message.author.mention}, here's your gallery message, you can copy the block "
                                               f"below and it will have the same text you just sent:\n```{message.content}```")
    await message.channel.send(content=
                               f"Hi {message.author.mention}, \n\nUnfortunately your latest gallery message had a "
                               f"**misnumbered dex id**, either in the message or filename, because they didn't match eachother:\n\n"
                               f"* **Filename ID: {misnumbered_issue.filename_fusion_id}**\n"
                               f"* **Message ID: {misnumbered_issue.content_fusion_id}**\n\n"
                               f"You can recover and copy your message text at: {copied_message.jump_url} "
                               f"so that you can fix the issue and post it here again.\n\nThank you!",
                               delete_after=20)
    await message.delete()