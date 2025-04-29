import discord

from bot import utils
from bot.bot_context import BotContext
from bot.exceptions import MissingBotContext
from bot.models import GlobalContext

bot_id = None
bot_avatar_url = None
bot_context = None


async def set_bot_up(bot: discord.Client):
    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "17179929600"

    global bot_avatar_url

    bot_user = bot.user
    if bot_user is not None:
        bot_avatar_url = utils.get_display_avatar(bot_user).url

    global bot_context
    bot_context = BotContext(bot)

    invite_parameters = f"client_id={str(bot_id)}&permissions={permission_id}&scope=bot"
    invite_link = f"https://discordapp.com/api/oauth2/authorize?{invite_parameters}"
    print(f"\n\nReady! bot invite:\n\n{invite_link}\n\n")


def ctx() -> GlobalContext:
    if bot_context is not None:
        return bot_context.context
    else:
        raise MissingBotContext

def get_bot_id():
    return bot_id