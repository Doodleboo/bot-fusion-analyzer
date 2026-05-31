from discord import Client

from bot.spritework.tutorial_mode import StartTutorial, DismissTutorialPrompt, ExitTutorial, TutorialSelect


def add_persistent_items(bot: Client):
    bot.add_dynamic_items(StartTutorial)
    bot.add_dynamic_items(DismissTutorialPrompt)
    bot.add_dynamic_items(ExitTutorial)
    bot.add_dynamic_items(TutorialSelect)
