import analysis_content as analysis_content
import analysis_sprite as analysis_sprite
from analysis import Analysis, generate_bonus_file
from discord.message import Message, Attachment
from models import GlobalContext
from enums import AnalysisType, Severity

MAX_SEVERITY = [Severity.refused, Severity.controversial]


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


# Methods to send messages in #fusion-bot

async def send_bot_logs(analysis: Analysis, ctx: GlobalContext, author_id: int):
    if analysis.severity in MAX_SEVERITY:
        await send_with_content(analysis, ctx, author_id)
    else:
        await send_without_content(analysis, ctx)
    await send_bonus_content(analysis, ctx)


async def send_bonus_content(analysis: Analysis, ctx: GlobalContext):
    if analysis.transparency_issue:
        await ctx.pif.logs.send(
            embed=analysis.transparency_embed,
            file=generate_bonus_file(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await ctx.pif.logs.send(
            embed=analysis.half_pixels_embed,
            file=generate_bonus_file(analysis.half_pixels_image)
        )


async def send_with_content(analysis: Analysis, ctx: GlobalContext, author_id: int):
    ping_owner = f"<@!{author_id}>"
    await ctx.pif.logs.send(embed=analysis.embed, content=ping_owner)


async def send_without_content(analysis: Analysis, ctx: GlobalContext):
    await ctx.pif.logs.send(embed=analysis.embed)