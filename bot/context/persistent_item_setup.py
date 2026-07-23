from discord import Client

from bot.handler import RetryButton, DismissRetry
from bot.spritework.tutorial_mode import StartTutorial, DismissTutorialPrompt, ExitTutorial, TutorialSelect


def add_persistent_items(bot: Client):
    # Tutorial mode
    bot.add_dynamic_items(StartTutorial)
    bot.add_dynamic_items(DismissTutorialPrompt)
    bot.add_dynamic_items(ExitTutorial)
    bot.add_dynamic_items(TutorialSelect)
    # Retry analysis
    bot.add_dynamic_items(RetryButton)
    bot.add_dynamic_items(DismissRetry)
