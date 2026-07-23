import asyncio
import re
from typing import Any

import discord
from discord import ButtonStyle, Interaction, Message, Thread, DMChannel, TextChannel
from discord.ui import View, Button, DynamicItem, Item

from bot.context.message_identifier import (is_assets_gallery as assets_check, has_correct_assets_gallery_keywords,
                                            is_message_from_ignored_bots, has_ignored_spritework_tags)
from bot.context.setup import ctx
from bot.context.user_identifier import user_is_potential_spriter, user_is_sprite_manager
from bot.core.analysis import Analysis
from bot.core.analyzer import send_full_analysis, generate_analysis, generate_gallery_analysis_list
from bot.gallery.emojis import react_with_emoji, replace_emoji
from bot.misc.enums import AnalysisType, Severity, OptedType
from bot.misc.exceptions import MisnumberedGalleryID
from bot.misc.utils import fancy_print, attachment_not_an_image
from bot.spritework.opt_out_options import is_opted_out_user
from bot.spritework.spritework_checker import get_spritework_thread_times
from bot.spritework.swablu_timestamp import send_swablu_timestamp
from bot.spritework.tutorial_mode import send_tutorial_mode_prompt

SPRITE_MANAGER_PING = "<@&900867033175040101>"
BASE_HANDLER_PING = "<@&1503605171849269268>"


# Handler methods

async def handle_sprite_gallery(message: Message):
    log_event("Gallery >", message)
    await handle_gallery(message, AnalysisType.sprite_gallery)


async def handle_assets_gallery(message: Message):
    log_event("Assets  >", message)
    if not has_correct_assets_gallery_keywords(message):
        return
    await handle_gallery(message, AnalysisType.assets_gallery)


async def handle_retried_analysis(message: Message, analysis_type: AnalysisType):
    log_event("Retry   >", message)
    await handle_gallery(message, analysis_type, retried_analysis=True)


async def handle_gallery(message: Message, analysis_type: AnalysisType, retried_analysis: bool = False):
    try:
        analysis_list = await generate_gallery_analysis_list(message, analysis_type, retried_analysis)
    except MisnumberedGalleryID as misnumbered_exception:
        await handle_misnumbered_in_gallery(message, misnumbered_exception)
        return
    for analysis in analysis_list:
        if analysis.can_be_retried:
            analysis.view = RetryView(message.author.id, analysis_type, message.id)
        await send_full_analysis(analysis, ctx().pif.logs)
    if retried_analysis:
        await replace_emoji(analysis_list, message)
    else:
        await react_with_emoji(analysis_list, message)


async def handle_zigzag_galpost(message: Message):
    embed = message.embeds[0]
    fancy_print("Zigzag  >", embed.author.name, message.channel.name, embed.title)

    if assets_check(message):
        analysis_type = AnalysisType.zigzag_base
    else:
        analysis_type = AnalysisType.zigzag_fusion

    analysis = generate_analysis(message, specific_attachment=None, analysis_type=analysis_type)
    if analysis.severity == Severity.refused:       # Only for refused tier
        channel = ctx().pif.zigzagoon
    else:
        channel = ctx().pif.logs
    await send_full_analysis(analysis, channel)
    if analysis.severity != Severity.refused:
        await react_with_emoji([analysis], message)


async def handle_regular_analysis(message: Message, auto_spritework: bool = False, reply_text: str|None = None):
    channel = message.channel
    if auto_spritework:
        analysis_type = AnalysisType.auto_spritework
    else:
        analysis_type = AnalysisType.ping_reply
    for specific_attachment in message.attachments:
        if attachment_not_an_image(specific_attachment):
            continue
        analysis = generate_analysis(message, specific_attachment, analysis_type, reply_text)
        try:
            await notify_if_ai(analysis, message, analysis_type, channel)
            await notify_base_handlers(analysis, message, analysis_type)
            await send_full_analysis(analysis, channel)
        except discord.Forbidden:
            await ctx().doodledoo.debug.send(f"Missing permissions in {channel.name}: {channel.jump_url}")


async def handle_spriter_application(thread: Thread):
    application_message = await fetch_thread_message(thread)
    if not application_message:
        return
    log_event("Spr App >", application_message)
    try:
        await handle_regular_analysis(application_message)
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
        await ctx().doodledoo.debug.send(f"Spriter Application: Missing permissions in {message.channel}")


async def handle_spritework_post(thread: Thread):
    if has_ignored_spritework_tags(thread):
        return

    spritework_message = await fetch_thread_message(thread)
    if not spritework_message:
        return

    author = spritework_message.author
    if not await is_opted_out_user(author, OptedType.auto_analysis):
        log_event("SprWork >", spritework_message)
        await handle_regular_analysis(message=spritework_message, auto_spritework=True)

        if user_is_potential_spriter(author):
            await asyncio.sleep(1)
            await send_tutorial_mode_prompt(author, thread)
            return

    if not await is_opted_out_user(author, OptedType.timestamp):
        await send_swablu_timestamp(author, thread)


async def handle_reply(message: Message):
    reply_message = await get_reply_message(message)
    if is_message_from_ignored_bots(reply_message):     # Ignore replies to Fusion Bot messages
        return
    log_event("Reply   >", reply_message)
    await handle_regular_analysis(message=reply_message, reply_text=message.content)


async def handle_direct_ping(message: Message):
    log_event("Ping    >", message)
    if len(message.attachments) >= 1:
        await handle_regular_analysis(message)
    else:
        await handle_ping_without_attachments(message)


async def handle_misnumbered_in_gallery(message: Message, exception: MisnumberedGalleryID):
    copied_message = await ctx().pif.logs.send(f"Hi {message.author.mention}, here's your gallery message, you can "
                                               f"copy the block below and it will have the same text you just sent:"
                                               f"\n```{message.content}```")
    await message.channel.send(content=
                               f"Hi {message.author.mention}, \n\nUnfortunately your latest gallery message had a "
                               f"**misnumbered dex id**, either in the message or filename, "
                               f"because they didn't match eachother:\n\n"
                               f"* **Filename ID: {exception.filename_fusion_id}**\n"
                               f"* **Message ID: {exception.content_fusion_id}**\n\n"
                               f"You can recover and copy your message text at: {copied_message.jump_url} "
                               f"so that you can fix the issue and post it here again.\n\nThank you!",
                               delete_after=20)
    await message.delete()


async def handle_ping_without_attachments(message: Message):
    await message.reply(f"Hi {message.author.name}, were you trying to analyze a sprite?\n"
                        f"You can either ping @Fusion Bot **in the same message where you upload your image**, or "
                        f"you can **reply to that image and ping @Fusion Bot in your reply**.")


def log_event(decorator: str, event: Message | Thread):
    if isinstance(event, Message):
        _log_message(decorator, event)


def _log_message(decorator: str, message: Message):
    channel_name = get_channel_name_from_message(message)
    split_lines = message.content.splitlines()
    if split_lines:
        first_line = split_lines[0]
    else:
        first_line = ""

    fancy_print(decorator, message.author.name, channel_name, first_line)


def get_channel_name_from_message(message: Message) -> str:
    try:
        channel = message.channel
        if isinstance(channel, DMChannel):
            return "DIRECT MESSAGE"
        channel_name = channel.name  # type: ignore
        if not isinstance(channel_name, str):
            return "INVALID"
    except SystemExit:
        raise
    except BaseException:
        channel_name = "UNKNOWN"
    return channel_name


async def get_reply_message(message: Message):
    if message.reference is None:
        raise RuntimeError(message)

    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)

    return await message.channel.fetch_message(reply_id)


async def fetch_thread_message(thread: Thread) -> Message|None:
    await asyncio.sleep(5)     # If it's too soon after thread creation, Discord returns errors
    try:
        caught_message = await thread.fetch_message(thread.id)
    except discord.errors.NotFound:
        last_message_id = thread.last_message_id
        try:
            caught_message = await thread.fetch_message(last_message_id)
        except discord.errors.NotFound:
            await ctx().doodledoo.debug.send(f"Could not fetch messages from thread {thread.name}: {thread.jump_url}")
            return None
    except discord.errors.Forbidden:
        await ctx().doodledoo.debug.send("Discord returned Forbidden while fetching thread message")
        return None
    if caught_message is None:
        await ctx().doodledoo.debug.send("Could not fetch message on thread creation")
        return None

    return caught_message


async def notify_if_ai(analysis: Analysis, message: Message, analysis_type: AnalysisType,
                       channel: TextChannel | Thread | DMChannel):
    new_user_in_spritework = (user_is_potential_spriter(message.author)
                              and analysis_type.is_automatic_spritework_analysis())
    if analysis.ai_suspicion >= 10 and new_user_in_spritework:
        warn_message = f"{SPRITE_MANAGER_PING} Potential AI sprite: {message.jump_url}"
        await ctx().pif.bot_chat.send(content=warn_message)
    if analysis.ai_suspicion >= 5 and new_user_in_spritework:
        await channel.send(content="Thanks for posting to spritework!\n"
                                   "As a general reminder to new users, sprites here are meant to be made by "
                                   "the users who submit them, without the use of AI at any stage.\n"
                                   "Welcome to the community!")
        await asyncio.sleep(5)


async def notify_base_handlers(analysis: Analysis, message: Message, analysis_type: AnalysisType):
    custom_base_in_spritework = (analysis.fusion_filename and analysis.fusion_filename.id_type.is_custom_base()
                                 and analysis_type.is_automatic_spritework_analysis())
    if custom_base_in_spritework:
        await ctx().pif.ditto.send(f"{BASE_HANDLER_PING} New custom base in Spritework: {message.jump_url}")



### RETRY BUTTONS CODE (it needs to be here to avoid circular imports)

class RetryView(View):
    def __init__(self, user_id: int, analysis_type: AnalysisType, message_id: int):
        super().__init__(timeout=None)
        self.add_item(RetryButton(user_id, analysis_type.value, message_id))
        self.add_item(DismissRetry(user_id))

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        await ctx().doodledoo.debug.send(f"RETRY ERROR in {interaction.channel} ({interaction.channel.jump_url})\n")
        raise RuntimeError from error


class RetryButton(DynamicItem[Button],
                  template=r'retry:(?P<userId>[0-9]+):(?P<gallery>[0-9]):(?P<messageId>[0-9]+)'):
    def __init__(self, user_id: int, gallery: int, message_id: int) -> None:
        self.user_id: int = user_id
        self.gallery = gallery
        self.is_assets_gallery = (gallery == AnalysisType.assets_gallery.value)
        self.message_id = message_id
        super().__init__(
            Button(label="Retry analysis (use after you've edited the message)", style=ButtonStyle.primary,
                   emoji="♻", custom_id=f"retry:{user_id}:{gallery}:{message_id}")
        )

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        user_id = int(match['userId'])
        gallery = int(match['gallery'])
        message_id = int(match['messageId'])
        return cls(user_id, gallery, message_id)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return is_analyzed_user_or_sprite_manager(self.user_id, interaction)

    async def callback(self, interaction: Interaction):
        gallery_message = await grab_gallery_message(self.is_assets_gallery, self.message_id)
        await handle_retried_analysis(gallery_message, AnalysisType(self.gallery))
        self.view.stop()
        await interaction.message.edit(content="**Analysis retried successfully below**", view=None)


class DismissRetry(DynamicItem[Button], template=r'dismissRetry:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        super().__init__(
            Button(label="Dismiss", style=ButtonStyle.secondary, custom_id=f"dismissRetry:{user_id}")
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        return is_analyzed_user_or_sprite_manager(self.user_id, interaction)

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        user_id = int(match['id'])
        return cls(user_id)

    async def callback(self, interaction: Interaction):
        self.view.stop()
        await interaction.message.edit(view=None)


def is_analyzed_user_or_sprite_manager(og_user_id: int, interaction: Interaction) -> bool:
    return (interaction.user.id == og_user_id) or (user_is_sprite_manager(interaction.user))


async def grab_gallery_message(is_assets_gallery: bool, message_id: int) -> Message:
    if is_assets_gallery:
        channel = ctx().pif.assets
    else:
        channel = ctx().pif.gallery
    return await channel.fetch_message(message_id)