from discord import Guild, ForumChannel
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    gallery: Channel
    logs: Channel
    debug: Channel|None
    spriter_apps: ForumChannel|None
    def __init__(self,
            server: Guild,
            gallery: Channel,
            logs: Channel,
            debug: Channel|None,
            spriter_apps: ForumChannel = None
            ) -> None:
        self.server = server
        self.gallery = gallery
        self.logs = logs
        self.debug = debug
        self.spriter_apps = spriter_apps


class GlobalContext():
    doodledoo: ServerContext
    pif: ServerContext
    def __init__(self,
                 doodledoo: ServerContext,
                 pif: ServerContext
                 ) -> None:
        self.doodledoo = doodledoo
        self.pif = pif
