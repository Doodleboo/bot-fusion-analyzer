import json
import os

import aiofiles
import discord
from discord import Member, ButtonStyle, Interaction, User, Message, HTTPException, Forbidden, NotFound
from discord.ui import View, Button

from bot.misc.enums import OptedType
from bot.misc.utils import fancy_print

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OPTED_OUT_FILE = os.path.join(CURRENT_DIR, "..", "..", "data", "AnalysisOptedOutUsers.json")
TIMESTAMP_FILE = os.path.join(CURRENT_DIR, "..", "..", "data", "TimestampOptedOutUsers.json")

ANALYSIS_MESSAGE = "Do you want to permanently opt out of automatic Fusion Bot analysis on new spritework posts?"
TIMESTAMP_MESSAGE = "Do you want to permanently opt out of the timestamp showing when a sprite can be posted?"


class HideFeature(View):
    message: Message

    def __init__(self, caller: Member|User, feature: OptedType):
        self.original_caller = caller
        self.feature = feature
        if self.feature.is_auto_analysis():
            self.hide_button = "Hide auto analysis"
        else:
            self.hide_button = "Hide reminder"
        super().__init__(timeout=60)   # After a minute it won't show the remove/opt out buttons anymore

    @discord.ui.button(label="Hide", style=ButtonStyle.secondary)
    async def hide_once(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.original_caller.id:
            await different_user_response(interaction, self.original_caller)
            return

        await interaction.message.delete()
        self.stop()

    @discord.ui.button(label="Opt out", style=ButtonStyle.secondary)
    async def opt_out_button(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.original_caller.id:
            await different_user_response(interaction, self.original_caller)
            return

        await interaction.message.edit(view=None)
        opt_out_view = OptOutConfirmation(self.original_caller, self.feature)
        if self.feature.is_auto_analysis():
            message_text = ANALYSIS_MESSAGE
        else:
            message_text = TIMESTAMP_MESSAGE
        await interaction.response.send_message(content=message_text, view=opt_out_view, delete_after=60)

    async def on_timeout(self) -> None:
        if not self.message:
            return
        try:
            await self.message.edit(view=None)
        except (HTTPException, Forbidden, NotFound, TypeError) as error:
            error_log = f"Exception {error} while trying to timeout auto feature buttons"
            if self.message.thread:
                error_log = error_log + f" in {self.message.thread.name}"
            elif self.message.channel:
                error_log = error_log + f" in {self.message.channel.name}"
            print(error_log)
        self.stop()



class OptOutConfirmation(View):

    def __init__(self, caller: Member|User, feature: OptedType):
        self.original_caller = caller
        self.feature  = feature
        super().__init__()

    @discord.ui.button(label="Confirm opt out", style=ButtonStyle.danger)
    async def opt_user_out(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.original_caller.id:
            await different_user_response(interaction, self.original_caller)
            return
        await add_to_opt_out_list(interaction.user, self.feature)
        fancy_print("Opt Out >",interaction.user.name,interaction.channel.name, self.feature.name)
        await interaction.response.edit_message(content="Opted out successfully.", view=None, delete_after=20)

    @discord.ui.button(label="Cancel (keep the automatic feature)", style=ButtonStyle.secondary)
    async def cancel_opt_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = f"Hi {interaction.user.mention}! That's meant for {og_user.name}."
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)


async def is_opted_out_user(user: Member | User, feature: OptedType) -> bool:
    user_list = await grab_user_list(feature)
    return user.id in user_list


async def add_to_opt_out_list(user: Member|User, feature: OptedType):
    user_list = await grab_user_list(feature)
    user_list.append(user.id)
    json_data = json.dumps(user_list)
    list_file = get_file(feature)
    async with aiofiles.open(list_file, 'w', encoding='utf-8') as f:
        await f.write(json_data)


async def grab_user_list(feature: OptedType) -> list:
    list_file = get_file(feature)
    async with aiofiles.open(list_file, 'r', encoding='utf-8') as f:
        content = await f.read()
        user_list = json.loads(content)

        if not isinstance(user_list, list):
            return []
        return user_list


def get_file(feature: OptedType) -> str:
    if feature.is_auto_analysis():
        return OPTED_OUT_FILE
    else:
        return TIMESTAMP_FILE
