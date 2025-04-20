# Fusion Analyzer

Discord bot, provides feedback on custom sprites for the game [Pokémon Infinite Fusion](https://infinitefusion.fandom.com/wiki/Pok%C3%A9mon_Infinite_Fusion_Wiki).

# Credits

- **Aegide** as the original creator of the Fusion Bot
- **Doodledoo** is the creator of this fork and added features
- **Greystorm** for giving permission to use various utilities from spritebot

# Changelog
## Version 2.0
- **Similarity score** now works with **indexed mode** sprites (previously it was always 0)
- **Pokemon names** are now displayed when the dex IDs are valid
- **Similar command**: it will return a text list with at most 20 pairs of similar colors that could be merged into a single shade.
- **Assets gallery support** for custom bases, which will also display their pokemon name in the analysis.
- **High similarity warnings** and different similarity and color count restrictions, depending on if it's a fusion or custom base.
- Fix: the bot won't flip out when a single message has multiple different fusion with their IDs in the message
