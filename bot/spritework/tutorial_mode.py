import os
import re
from typing import Any

from discord import ButtonStyle, Interaction
from discord import (Member, Thread, TextChannel, DMChannel, SelectOption,
                     File)
from discord.ui import View, Button, Select, Item, DynamicItem

from bot.context.setup import ctx
from bot.misc.utils import fancy_print
from .tutorial_sections import sections

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = os.path.join(CURRENT_DIR, "..", "..", "resources")
FINISH_TUTORIAL = "Thanks for using Tutorial Mode!\nIf you'd like to use it again, use the /help command."
TUTORIAL_LOG_DECORATOR = "TutMode >"


async def send_tutorial_mode_prompt(user: Member, channel: TextChannel|Thread|DMChannel):
    prompt_text = (f"**Hi {user.display_name}!** If you're unsure what some of that means (for instance, "
                   f"similarity is probably not what you think!), press the **Tutorial Mode** button below.\n"
                   f"Also, make sure that if you edit your sprite, post updates in this same thread, don't "
                   f"create a new one please! Even if the analysis says 'controversial' or 'invalid', you can "
                   f"just edit it to make it valid.")
    prompt_view = PromptButtonsView(user.id)
    await channel.send(content=prompt_text, view=prompt_view)


# Views

class PromptButtonsView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(StartTutorial(user_id))
        self.add_item(DismissTutorialPrompt(user_id))

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        await view_error(interaction, error)


class TutorialMode(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(TutorialSelect(user_id))
        self.add_item(ExitTutorial(user_id))

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        await view_error(interaction, error)



# View items

class StartTutorial(DynamicItem[Button], template=r'startTutorial:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        super().__init__(
            Button(label="Tutorial Mode", style=ButtonStyle.primary, emoji="✏", custom_id=f"startTutorial:{user_id}")
        )

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        user_id = int(match['id'])
        return cls(user_id)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await different_user_response(interaction)
            return

        fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name, interaction.channel.name,
                    "Tutorial Mode engaged")
        tutorial_mode = TutorialMode(self.user_id)
        await interaction.response.edit_message(
            content="**Tutorial Mode**\nSelect a tutorial section from the dropdown below.",
            view=tutorial_mode)
        self.view.stop()


class DismissTutorialPrompt(DynamicItem[Button], template=r'dismissTutorialPrompt:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        super().__init__(
            Button(label="Dismiss", style=ButtonStyle.secondary, custom_id=f"dismissTutorialPrompt:{user_id}")
        )

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        user_id = int(match['id'])
        return cls(user_id)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await different_user_response(interaction)
            return

        self.view.stop()
        await interaction.message.delete()


class ExitTutorial(DynamicItem[Button], template=r'exitTutorial:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        super().__init__(
            Button(label="Exit Tutorial Mode", style=ButtonStyle.secondary, custom_id=f"exitTutorial:{user_id}")
        )

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button, match: re.Match[str], /):
        user_id = int(match['id'])
        return cls(user_id)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await different_user_response(interaction)
            return

        fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name,
                    interaction.channel.name, "Tutorial Mode finished")
        await interaction.response.edit_message(content=FINISH_TUTORIAL, view=None, attachments=[])
        self.view.stop()


class TutorialSelect(DynamicItem[Select], template=r'tutorialSelect:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        options = []
        for section_name in sections:
            section = sections[section_name]
            option = SelectOption(label=section.title, description=section.description, value=section_name)
            options.append(option)
        super().__init__(
            Select(placeholder="Choose a tutorial section", options=options, custom_id=f"tutorialSelect:{user_id}")
        )

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Select, match: re.Match[str], /):
        user_id = int(match['id'])
        return cls(user_id)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await different_user_response(interaction)
            return

        section = sections[self.item.values[0]]
        if not section:
            print(f"ERROR: No section found for element: {self.item.values[0]}")
        fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name, interaction.channel.name,
                    f"Section: {section.title}")
        full_section = f"**Tutorial Mode: {section.title}**\n\n{section.content}"
        attachments = []
        section_image = section.image
        if section_image:
            attachment_file = File(os.path.join(IMAGES_PATH, section_image))
            attachments.append(attachment_file)
        await interaction.response.edit_message(content=full_section, attachments=attachments)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member = None):
    if og_user:
        og_user_name = og_user.name
    else:
        og_user_name = 'another user'
    response_text = (f"Hi {interaction.user.mention}! That's meant for {og_user_name}, but if you want to use "
                     f"the Tutorial Mode yourself, you can use /help in a channel such as "
                     f"<#1031005766359982190> to do so.")
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)

async def view_error(interaction: Interaction, error: Exception):
    await ctx().doodledoo.debug.send(f"VIEW ERROR in {interaction.channel} ({interaction.channel.jump_url})\n")
    raise RuntimeError from error


