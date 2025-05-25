import discord
from discord import Member, ButtonStyle, Interaction, User
from discord.ui import View, Button


class HideAutoAnalysis(View):

    def __init__(self, caller: Member|User):
        self.original_caller = caller
        super().__init__()

    @discord.ui.button(label="Hide analysis", style=ButtonStyle.secondary)
    async def discard_tutorial_prompt(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Opt out", style=ButtonStyle.secondary)
    async def engage_tutorial_mode(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.edit(view=None)
            opt_out_view = OptOutConfirmation(self.original_caller)
            await interaction.response.send_message(
                content="Do you want to permanently opt out of automatic Fusion Bot analysis on new spritework posts?",
                view=opt_out_view,delete_after=60
            )
        else:
            await different_user_response(interaction, self.original_caller)



class OptOutConfirmation(View):

    def __init__(self, caller: Member|User):
        self.original_caller = caller
        super().__init__()

    @discord.ui.button(label="Confirm opt out", style=ButtonStyle.danger)
    async def opt_user_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            # TODO: Add to opt out list
            await interaction.response.edit_message(content="Opted out successfully.", view=None, delete_after=20)
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Cancel (keep automatic analysis)", style=ButtonStyle.secondary)
    async def cancel_opt_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = f"Hi {interaction.user.mention}! That's meant for {og_user.name}."
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)
