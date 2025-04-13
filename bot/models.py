from discord import Guild
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    gallery: Channel
    logs: Channel
    debug: Channel|None
    def __init__(self,
            server: Guild,
            gallery: Channel,
            logs: Channel,
            debug: Channel|None
            ) -> None:
        self.server = server
        self.gallery = gallery
        self.logs = logs
        self.debug = debug


class GlobalContext():
    doodledoo: ServerContext
    pif: ServerContext
    def __init__(self,
                 doodledoo: ServerContext,
                 pif: ServerContext
                 ) -> None:
        self.doodledoo = doodledoo
        self.pif = pif
