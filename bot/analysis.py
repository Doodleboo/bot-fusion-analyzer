from io import BytesIO

import utils
from discord.colour import Colour
from discord.embeds import Embed
from discord.file import File
from discord.message import Attachment, Message
from PIL.Image import Image

from enums import DiscordColour, Severity, AnalysisType, IdType
from issues import Issues


DICT_SEVERITY_COLOUR = {
    Severity.accepted : DiscordColour.green,
    Severity.ignored : DiscordColour.orange,
    Severity.controversial : DiscordColour.pink,
    Severity.refused : DiscordColour.red
}
IMAGE_PNG = "image.png"
PNG = "PNG"


class Analysis:
    message: Message
    issues: Issues
    severity: Severity
    embed: Embed
    fusion_id: str = "DEFAULT_VALUE"

    autogen_url: str|None = None
    attachment_url: str|None = None
    specific_attachment: Attachment|None = None

    size_issue: bool = False

    transparency_issue: bool = False
    transparency_image: Image
    transparency_embed: Embed

    half_pixels_issue: bool = False
    half_pixels_image: Image
    half_pixels_embed: Embed

    def __init__(self,
                 message:Message,
                 specific_attachment:Attachment|None,
                 analysis_type:AnalysisType|None) -> None:
        self.message = message
        self.specific_attachment = specific_attachment
        self.issues = Issues()
        self.severity = Severity.accepted
        self.type = analysis_type

    def generate_embed(self):
        self.embed = Embed()
        self.apply_description()
        self.apply_title()
        self.apply_colour()
        self.apply_author()
        self.apply_footer()
        self.apply_image()
        self.apply_thumbnail()
        self.handle_bonus_embed()

    def generate_transparency_file(self):
        if self.transparency_image is None:
            raise RuntimeError()
        bytes_buffer = BytesIO()
        self.transparency_image.save(bytes_buffer, format=PNG)
        bytes_buffer.seek(0)
        return File(bytes_buffer, filename=IMAGE_PNG)

    def generate_half_pixels_file(self):
        if self.half_pixels_image is None:
            raise RuntimeError()
        bytes_buffer = BytesIO()
        self.half_pixels_image.save(bytes_buffer, format=PNG)
        bytes_buffer.seek(0)
        return File(bytes_buffer, filename=IMAGE_PNG)

    def handle_bonus_embed(self):
        if self.transparency_issue is True:
            self.transparency_embed = get_bonus_embed(DiscordColour.pink.value)
        if self.half_pixels_issue is True:
            self.half_pixels_embed = get_bonus_embed(DiscordColour.red.value)

    def apply_title(self):
        if self.fusion_id and (self.fusion_id != "DEFAULT_VALUE"):
            title_text = f"__{self.severity.value}: {self.fusion_id}__\n{str(self.issues)}"
        else:
            title_text = f"__{self.severity.value}:__\n{str(self.issues)}"
        if len(title_text) >= 256:   # In case it's too long for the title
            self.embed.description = title_text
        else:
            self.embed.title = title_text

    def apply_colour(self):
        self.embed.colour = DICT_SEVERITY_COLOUR.get(self.severity, DiscordColour.gray).value

    def apply_description(self):
        self.embed.description = f"[Link to message]({self.message.jump_url})"

    def apply_author(self):
        author_avatar = utils.get_display_avatar(self.message.author)
        self.embed.set_author(name=self.message.author.name, icon_url=author_avatar.url)

    def apply_footer(self):
        message_lines = self.message.content.splitlines()

        if len(message_lines) == 0:
            return

        first_line = message_lines[0]
        if first_line:
            self.embed.set_footer(text=first_line)

    def apply_image(self):
        # Uncomment this when "get_autogen_url" works
        # if self.autogen_url is not None:
        #     self.embed.set_image(url=self.autogen_url)
        pass

    def apply_thumbnail(self):
        if self.attachment_url is not None:
            self.embed.set_thumbnail(url=self.attachment_url)

    # Non-embed methods

    def have_attachment(self) -> bool:
        return len(self.message.attachments) >= 1

    def have_zigzag_embed(self) -> bool:
        if not self.type.is_zigzag_galpost():
            return False
        embeds = self.message.embeds
        return embeds is not None

    def get_filename(self):
        if self.type.is_zigzag_galpost():
            image_url = self.get_attachment_url_from_embed()
            return utils.get_filename_from_image_url(image_url)
        if self.specific_attachment is None:
            return self.message.attachments[0].filename
        return self.specific_attachment.filename

    def get_attachment_url(self):
        if self.type.is_zigzag_galpost():
            return self.get_attachment_url_from_embed()
        else:
            return self.get_attachment_url_from_message()

    def get_attachment_url_from_message(self):
        if self.specific_attachment is None:
            return self.message.attachments[0].url
        return self.specific_attachment.url

    def get_attachment_url_from_embed(self):
        if not self.message.embeds:
            return None
        embed = self.message.embeds[0]
        if embed.image is None:
            return None
        return embed.image.url

    def extract_fusion_id_from_filename(self) -> (str, IdType):
        fusion_id = None
        id_type = None
        if self.have_attachment() or self.type.is_zigzag_galpost():
            filename = self.get_filename()
            fusion_id, id_type = utils.get_fusion_id_from_filename(filename)
        return fusion_id, id_type


def get_bonus_embed(discord_colour:Colour):
    bonus_embed = Embed()
    bonus_embed.colour = discord_colour
    bonus_embed.set_image(url="attachment://image.png")
    return bonus_embed


def generate_bonus_file(image:Image):
    if image is None:
        raise RuntimeError()
    io_bytes = BytesIO()
    image.save(io_bytes, format=PNG)
    io_bytes.seek(0)
    return File(io_bytes, filename=IMAGE_PNG)
