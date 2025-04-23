import math

import numpy
import numpy as np

import utils
from discord import Message, Member, Embed

from bot.rocket_villains import villain_pokemon_points


ROCKET_GRUNT_ROLE_ID = 1361797020578480369
BASE_POINTS = 5
DIMINISHING_FACTOR = 0.3
LIKES_LIMIT = math.ceil(25 * DIMINISHING_FACTOR)
LOVES_LIMIT = math.ceil(46 * DIMINISHING_FACTOR)
ROCKET_TIER_1 = BASE_POINTS + LIKES_LIMIT
ROCKET_TIER_2 = BASE_POINTS + LOVES_LIMIT
NEW_HOENN_DEX_NUM = 502
HOENN_BONUS_POINTS = 2


async def is_replying_to_rocket_grunt(message: Message) -> bool:
    if message.reference is None:
        return False

    reply_id = message.reference.message_id
    if reply_id is None:
        return False

    original_message = await message.channel.fetch_message(reply_id)

    return await author_is_rocket_grunt(original_message)


async def author_is_rocket_grunt(message: Message) -> bool:
    author = message.author
    if author is None:
        return False
    if not isinstance(author, Member):
        return False

    roles = author.roles

    for role in roles:
        if role.id == ROCKET_GRUNT_ROLE_ID:
            return True

    return False


async def handle_rocket_analysis(message:Message) -> (Embed, int):
    if not message.attachments:
        return
    attachment = message.attachments[0]

    filename = attachment.filename
    ids, is_custom_base = utils.get_fusion_id_from_filename(filename)
    if ids is None:
        return

    if is_custom_base:
        id_number = int(ids)
        extra_points = calc_rocket_points_list(id_number)
        hoenn_bonus = (id_number >= NEW_HOENN_DEX_NUM)
    else:
        head, body = ids.split(".")
        head_number = int(head)
        body_number = int(body)
        extra_points_head = calc_rocket_points_list(head_number)
        extra_points_body = calc_rocket_points_list(body_number)
        extra_points = (extra_points_head + extra_points_body) / 2
        hoenn_bonus = (head_number >= NEW_HOENN_DEX_NUM) or (body_number >= NEW_HOENN_DEX_NUM)

    # Diminish factor
    extra_points = extra_points * DIMINISHING_FACTOR
    integer_points = np.ceil(extra_points)

    return generate_rocket_embed(integer_points, hoenn_bonus)


def calc_rocket_points_list(id:int) -> numpy.array:
    scores_array = []
    for villain in villain_pokemon_points:
        villain_dict = villain_pokemon_points[villain]
        score = 0
        if id in villain_dict:
            score = int(villain_dict[id])
        scores_array.append(score)

    return np.array(scores_array)





def generate_rocket_embed(integer_points: numpy.array(float), hoenn_bonus: bool=False) -> (Embed, int):
    text_list = "\n"
    i = 0
    for villain in villain_pokemon_points:
        name = villain
        score = integer_points[i]
        if score > 0:
            if score <= LIKES_LIMIT:
                text_list += name + " likes it.\n"
            elif score <= LOVES_LIMIT:
                text_list += name + " loves it!\n"
            else:
                text_list += "It's among " + name + "'s favorites!\n"
        i += 1

    total_score = numpy.ceil(np.sum(integer_points)) + BASE_POINTS
    total_score_int = str(total_score.astype(int))
    if hoenn_bonus:
        text_list = "Axie and Maxie give you 1 bonus point each for helping document newly-discovered Hoenn pokemon.\n"
        total_score_int += HOENN_BONUS_POINTS  # To not affect the Rainbow Rocket review
    text_list += "\n**TOTAL POINTS**: " + str(total_score_int) + "\n"

    if total_score <= BASE_POINTS:
        text_list += "Rainbow Rocket accepts your contribution."
    elif total_score <= ROCKET_TIER_1:
        text_list += "Rainbow Rocket appreciates your contribution."
    elif total_score <= ROCKET_TIER_2:
        text_list += "Rainbow Rocket is enthused about your contribution."
    else:
        text_list += "Rainbow Rocket thanks you profusely for your contribution."

    embed = Embed(title="Rainbow Rocket Analysis",
                  description=text_list)
    return (embed, total_score_int)

