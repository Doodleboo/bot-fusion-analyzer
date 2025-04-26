from discord import Guild, ForumChannel
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    logs: Channel
    debug: Channel|None
    def __init__(self,
            server: Guild,
            logs: Channel,
            debug: Channel|None
            ) -> None:
        self.server = server
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
