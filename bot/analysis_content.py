import utils
from analysis import Analysis
from bot.analysis_sprite import detect_egg_size_early
from enums import Severity
from issues import (CustomBase, DifferentSprite, EggSprite, IconSprite,
                    IncomprehensibleSprite, MissingFilename, MissingSprite,
                    OutOfDex, FileName, PokemonNames)
from message_identifier import (have_icon_in_message, have_custom_in_message,
                                have_egg_in_message, have_base_in_message)


def exists(value):
    return value is not None


class ContentContext():
    def __init__(self, analysis: Analysis):

        self.filename_fusion_id, self.is_custom_base = analysis.extract_fusion_id_from_filename()

        self.content_fusion_ids_list = utils.extract_fusion_ids_from_content(analysis.message, self.is_custom_base)

        if self.content_fusion_ids_list:
            self.content_fusion_id = self.content_fusion_ids_list[0]
        else:
            self.content_fusion_id = None

        self.is_egg_sprite = self.is_custom_base and have_egg_in_message(analysis.message)

    def have_two_values(self):
        return exists(self.filename_fusion_id) and exists(self.content_fusion_id)

    def have_one_value(self):
        return exists(self.filename_fusion_id) or exists(self.content_fusion_id)

    def handle_one_value(self, analysis: Analysis):
        if self.content_fusion_id is not None:
            analysis.severity = Severity.refused
            analysis.issues.add(MissingFilename())
            filename = analysis.get_filename()
            analysis.issues.add(FileName(filename))
        elif self.filename_fusion_id is not None:
            analysis.fusion_id = self.filename_fusion_id
            # analysis.autogen_url = utils.get_autogen_url(analysis.fusion_id)
            self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_two_values(self, analysis: Analysis):
        if self.filename_fusion_id != self.content_fusion_id:
            if self.filename_fusion_id not in self.content_fusion_ids_list:
                self.handle_two_different_values(analysis)
            else:
                self.content_fusion_id = self.filename_fusion_id
                analysis.fusion_id = self.filename_fusion_id
        else:
            self.handle_two_same_values(analysis)
        if self.filename_fusion_id is not None:
            self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_two_different_values(self, analysis: Analysis):
        if self.filename_fusion_id is not None and self.content_fusion_id is not None:
            analysis.severity = Severity.refused
            issue = DifferentSprite(self.filename_fusion_id, self.content_fusion_id)
            analysis.issues.add(issue)
            self.handle_dex_verification(analysis, self.content_fusion_id)

    def handle_two_same_values(self, analysis: Analysis):
        if self.filename_fusion_id is not None:
            analysis.fusion_id = self.filename_fusion_id
        # if analysis.fusion_id is not None:
        # analysis.autogen_url = utils.get_autogen_url(analysis.fusion_id)

    def handle_dex_verification(self, analysis: Analysis, fusion_id: str):
        if ((self.is_custom_base and utils.is_invalid_base_id(fusion_id))
                or (not self.is_custom_base and utils.is_invalid_fusion_id(fusion_id))):

            analysis.severity = Severity.refused
            analysis.issues.add(OutOfDex(fusion_id))

        elif self.is_custom_base:
            handle_pokemon_name(analysis, fusion_id, self.is_egg_sprite)
        else:
            handle_pokemon_names(analysis, fusion_id)


def main(analysis: Analysis):
    if (analysis.specific_attachment is not None)\
            or analysis.have_attachment()\
            or analysis.have_zigzag_embed():
        handle_some_content(analysis)
        return

    handle_no_content(analysis)


def handle_some_content(analysis: Analysis):
    content_context = ContentContext(analysis)
    analysis.attachment_url = analysis.get_attachment_url()
    if content_context.have_two_values():
        content_context.handle_two_values(analysis)
    elif content_context.have_one_value():
        content_context.handle_one_value(analysis)
    else:
        handle_zero_value(analysis)


def handle_no_content(analysis: Analysis):
    analysis.severity = Severity.ignored
    analysis.issues.add(MissingSprite())


def handle_zero_value(analysis: Analysis):
    analysis.severity = Severity.ignored
    if have_egg_in_message(analysis.message):
        analysis.issues.add(EggSprite())
    elif have_icon_in_message(analysis.message):
        analysis.issues.add(IconSprite())
    elif have_custom_in_message(analysis.message):
        analysis.issues.add(CustomBase())
    elif have_base_in_message(analysis.message):
        analysis.issues.add(CustomBase())
    else:
        analysis.issues.add(IncomprehensibleSprite())
        filename = analysis.get_filename()
        analysis.issues.add(FileName(filename))


def handle_pokemon_names(analysis: Analysis, fusion_id: str):
    head, body = fusion_id.split(".")
    name_map = utils.id_to_name_map()
    head_name = name_map.get(head)
    body_name = name_map.get(body)
    analysis.issues.add(PokemonNames(head_name, body_name))


def handle_pokemon_name(analysis: Analysis, base_id: str, egg_sprite: bool = False):
    name_map = utils.id_to_name_map()
    pokemon_name = name_map.get(base_id)
    if not egg_sprite:
        egg_sprite = detect_egg_size_early(analysis)    # In case there's no "egg" in the message
    if egg_sprite:
        analysis.issues.add(EggSprite(pokemon_name))
    else:
        analysis.issues.add(CustomBase(pokemon_name))

