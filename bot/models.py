from discord import Guild, ForumChannel
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    logs: Channel
    debug: Channel
    zigzagoon: Channel
    def __init__(self,
            server: Guild,
            logs: Channel,
            debug: Channel,
            zigzagoon: Channel
            ) -> None:
        self.server = server
        self.logs = logs
        self.debug = debug
        self.zigzagoon = zigzagoon


class GlobalContext():
    doodledoo: ServerContext
    pif: ServerContext
    def __init__(self,
                 doodledoo: ServerContext,
                 pif: ServerContext
                 ) -> None:
        self.doodledoo = doodledoo
        self.pif = pif
