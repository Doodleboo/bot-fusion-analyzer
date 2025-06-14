import os

import discord
from discord import Member, User, Thread, TextChannel, DMChannel, SelectOption, File
from discord.ui import View, Button, Select
from discord import ButtonStyle, Interaction

from bot.tutorial_sections import sections
from bot.utils import fancy_print

SPRITER_ROLE_ID = 392803830900850688
MANAGER_ROLE_ID = 900867033175040101
WATCHOG_ROLE_ID = 1100903960476385350
MOD_ROLE_ID     = 306953740651462656
UNOWN_ROLE_ID   = 1210701164426039366
NON_TUTORIAL_ROLES = [SPRITER_ROLE_ID, MANAGER_ROLE_ID, WATCHOG_ROLE_ID,
                      MOD_ROLE_ID, UNOWN_ROLE_ID]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = os.path.join(CURRENT_DIR, "..", "resources")


async def user_is_potential_spriter(user: User|Member) -> bool:
    if not isinstance(user, Member):
        return False
    for role in user.roles:
        if role.id in NON_TUTORIAL_ROLES:
            return False
    return True


async def send_tutorial_mode_prompt(user: Member, channel: TextChannel|Thread|DMChannel):
    prompt_text = (f"**Hi {user.display_name}!** If you're unsure what some of that means (for instance, "
                   f"similarity is probably not what you think!), press the **Tutorial Mode** button below.")
    prompt_view = PromptButtonsView(user)
    await channel.send(content=prompt_text, view=prompt_view)


# Views

class PromptButtonsView(View):

    def __init__(self, caller: Member):
        self.original_caller = caller
        super().__init__()

    @discord.ui.button(label="Tutorial Mode", style=ButtonStyle.primary, emoji="✏")
    async def engage_tutorial_mode(self, interaction: Interaction, _button: Button):
        fancy_print("TutMode >", interaction.user.name, interaction.channel.name, "Tutorial Mode engaged")
        if interaction.user.id == self.original_caller.id:
            await interaction.response.edit_message(content="Tutorial Mode engaged",
                                                    view=TutorialMode(self.original_caller))
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Discard", style=ButtonStyle.secondary)
    async def discard_tutorial_prompt(self, interaction: Interaction, _button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)


class TutorialMode(View):
    def __init__(self, caller: Member):
        self.original_caller = caller
        super().__init__()
        self.add_item(TutorialSelect(self.original_caller))

    @discord.ui.button(label="Exit Tutorial Mode", style=ButtonStyle.secondary)
    async def exit_tutorial_mode(self, interaction: Interaction, _button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.response.edit_message(content="Thanks for using Tutorial Mode!",
                                                    view=None, attachments=[])
        else:
            await different_user_response(interaction, self.original_caller)


class TutorialSelect(Select):
    def __init__(self, caller: Member):
        self.original_caller = caller
        options = []
        for section_name in sections:
            section = sections[section_name]
            option = SelectOption(label=section.title, description=section.description, value=section_name)
            options.append(option)
        super().__init__(placeholder="Choose a tutorial section", options=options)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.original_caller.id:
            await different_user_response(interaction, self.original_caller)
            return

        section = sections[self.values[0]]
        if not section:
            print(f"ERROR: No section found for element: {self.values[0]}")
        full_section = f"**Tutorial Mode: {section.title}**\n\n{section.content}"
        attachments = []
        section_image = section.image
        if section_image:
            attachment_file = File(os.path.join(IMAGES_PATH, section_image))
            attachments.append(attachment_file)
        await interaction.response.edit_message(content=full_section, attachments=attachments)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = (f"Hi {interaction.user.mention}! That's meant for {og_user.name}, but if you want to use "
                     f"the Tutorial Mode yourself, you can use /help in a channel such as "
                     f"<#1031005766359982190> to do so.")
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)



