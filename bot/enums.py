from enum import Enum, auto

import discord


class Description(str, Enum):
    missing_file        = "Missing sprite"
    missing_file_name   = "Missing file name"
    missing_fusion_id   = "Unable to identify fusion sprite"
    different_fusion_id = "Different ID"
    colour_excess       = "Color excess"
    transparency_amount = "Transparency"
    half_pixels_amount  = "Half-pixels"
    colour_amount       = "Colors"
    file_name           = "Filename"
    invalid_fusion_id   = "Invalid fusion ID"
    sprite_error        = "Invalid sprite"
    invalid_size        = "Invalid size"
    icon                = "Icon sprite"
    custom              = "custom base"
    egg                 = "Egg sprite"
    incomprehensible    = "Incomprehensible name"
    test                = "Description test"
    no_transparency     = "Missing transparency"
    aseprite_user       = "Aseprite"
    graphics_gale_user  = "GraphicsGale"
    similarity_amount   = "Similarity"
    high_similarity     = "High number of similar color pairs"
    refused_similarity  = "Over maximum limit of similar color pairs"
    misplaced_grid      = "Not aligned in the grid (it's fine)"


class Severity(Enum):
    accepted        = "Valid"
    ignored         = "Ignored"
    controversial   = "Controversial"
    refused         = "Invalid"


class DiscordColour(Enum):
    green   = discord.Colour(0x2ecc71)
    orange  = discord.Colour(0xe67e22)
    red     = discord.Colour(0xe74c3c)
    gray    = discord.Colour(0xcdcdcd)
    pink    = discord.Colour(0xff00ff)

class AnalysisType(Enum):
    sprite_gallery  = auto()
    assets_gallery  = auto()
    ping_reply      = auto()
    zigzag_fusion   = auto()
    zigzag_base     = auto()

    def is_gallery(self):
        return self in (AnalysisType.assets_gallery, AnalysisType.sprite_gallery)

    def is_assets_gallery(self):
        return (self == AnalysisType.assets_gallery) or (self == AnalysisType.zigzag_base)

    def is_sprite_gallery(self):
        return (self == AnalysisType.sprite_gallery) or (self == AnalysisType.zigzag_fusion)

    def is_reply(self):
        return self == AnalysisType.ping_reply

    def is_zigzag_galpost(self):
        return (self == AnalysisType.zigzag_fusion) or (self == AnalysisType.zigzag_base)