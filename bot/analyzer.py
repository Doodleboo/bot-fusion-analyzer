import analysis_content as analysis_content
import analysis_sprite as analysis_sprite
from analysis import Analysis
from discord.message import Message, Attachment
from enums import AnalysisType


def generate_analysis(
        message: Message,
        specific_attachment: Attachment|None = None,
        analysis_type: AnalysisType|None = None):
    # TODO: Use is_assets and is_reply to detect
    # custom bases in sprite gallery
    analysis = Analysis(message, specific_attachment, analysis_type)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis)
    analysis.generate_embed()
    return analysis