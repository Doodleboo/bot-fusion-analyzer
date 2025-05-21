from discord import Member, User, Thread, TextChannel, DMChannel

SPRITER_ROLE_ID = 392803830900850688
MANAGER_ROLE_ID = 900867033175040101
WATCHOG_ROLE_ID = 1100903960476385350
MOD_ROLE_ID     = 306953740651462656
UNOWN_ROLE_ID   = 1210701164426039366
NON_TUTORIAL_ROLES = [SPRITER_ROLE_ID, MANAGER_ROLE_ID, WATCHOG_ROLE_ID,
                      MOD_ROLE_ID, UNOWN_ROLE_ID]


async def user_is_potential_spriter(user: User|Member) -> bool:
    if not isinstance(user, Member):
        return False
    for role in user.roles:
        if role.id in NON_TUTORIAL_ROLES:
            return False
    return True


async def send_tutorial_mode_prompt(user: Member, channel: TextChannel|Thread|DMChannel):
    await channel.send(f"Placeholder, {user.display_name}")



