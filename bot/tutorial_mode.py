import discord
from discord import Member, User, Thread, TextChannel, DMChannel
from discord.ui import View, Button
from discord import ButtonStyle, Interaction

SPRITER_ROLE_ID = 392803830900850688
MANAGER_ROLE_ID = 900867033175040101
WATCHOG_ROLE_ID = 1100903960476385350
MOD_ROLE_ID     = 306953740651462656
UNOWN_ROLE_ID   = 1210701164426039366
NON_TUTORIAL_ROLES = [SPRITER_ROLE_ID, MANAGER_ROLE_ID, WATCHOG_ROLE_ID,
                      MOD_ROLE_ID, UNOWN_ROLE_ID]


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
    async def engage_tutorial_mode(self, interaction: Interaction, button: Button):
        #if interaction.user.id == self.original_caller.id:
        #    await interaction.response.edit_message(content="New state")
        #else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Discard", style=ButtonStyle.secondary)
    async def discard_tutorial_prompt(self, interaction: Interaction, button: Button):
        #if interaction.user.id == self.original_caller.id:
        #    await interaction.message.delete()
        #else:
            await different_user_response(interaction, self.original_caller)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = (f"Hi {interaction.user.mention}! That's meant for {og_user.name}, but if you want to use "
                     f"the Tutorial Mode yourself, you can use /help in a channel such as #ask_a_bot to do so.")
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)



