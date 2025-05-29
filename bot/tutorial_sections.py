class TutorialSection:
    title: str
    description: str
    content: str

    def __init__(self, title, description, content):
        self.title = title
        self.description = description
        self.content = content


filename = TutorialSection(
    title="Filename",
    description="What should my filename be? What's the correct format?",
    content="With fusion sprites, your filename should be 2 numbers, with a dot in between.\n"
            "For instance: **102.463.png** (most likely, your program will add the png part on its own)\n"
            "The numbers represent the pokedex numbers of the pokemon in your fusion. "
            "**Warning:** Infinite Fusion uses different pokedex numbers, so don't take them from the main games!"
            "Instead, use the **dex command** to know the filenames. For example, write: `dex Ludicolo/Probopass`"
            "in a message, and you will trigger the command.\n"
            "For triple fusions, it'd be 3 numbers, and for custom bases, only one."
)

colors = TutorialSection(
    title="Color count",
    description="What's the color count? How many colors can I use?",
    content="In pixel art, and particularly here, the amount of colors used in a sprite matters. Pokemon sprites "
            "were limited to 16 but we use more.\nIf it's for a fusion, try to keep it below 32. Make each color "
            "count and try to re-use colors whenever possible."
)

similarity = TutorialSection(
    title="Similarity score",
    description="What does it mean? How much is too much similarity?",
    content="A common misconception is that it's measuring how similar your sprite is to something else. Far from it! "
            "It's grabbing the colors you used on your sprite, and comparing them against eachother. This is to ensure "
            "that your colors are distinct enough.\nIf it's for a fusion, try to keep your similarity to 7 or below. "
            "Anything over 10 most of the time means that you have some unaccounted colors in there that are *almost "
            "identical* to others you used, yet not quite the same shade.\nWrite ?tag analyser for a link to a website"
            "that will show you which color pairs are the most similar, so that you can convert them into a single "
            "color.\nYou can use the /similar command to check the color pairs too!"
)


sections = {
    "filename" : filename,
    "colors" : colors,
    "similarity" : similarity
}

