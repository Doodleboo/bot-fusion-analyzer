from discord import User, Member

SPRITER_ROLE_ID = 392803830900850688
APPLICANT_ID    = 1136806607469150380
MANAGER_ROLE_ID = 900867033175040101
WATCHOG_ROLE_ID = 1100903960476385350
MOD_ROLE_ID     = 306953740651462656
UNOWN_ROLE_ID   = 1210701164426039366
NO_GALPOST_ID   = 1191178850713993236
NO_HARVEST_ID   = 1191179006578532372
NON_TUTORIAL_ROLES = [SPRITER_ROLE_ID, MANAGER_ROLE_ID, WATCHOG_ROLE_ID, MOD_ROLE_ID,
                      UNOWN_ROLE_ID, NO_GALPOST_ID, NO_HARVEST_ID, APPLICANT_ID]


def user_is_potential_spriter(user: User|Member) -> bool:
    if not isinstance(user, Member):
        return False
    for role in user.roles:
        if role.id in NON_TUTORIAL_ROLES:
            return False
    return True


def user_is_spriter(user: User|Member) -> bool:
    if not isinstance(user, Member):
        return False
    return SPRITER_ROLE_ID in user.roles