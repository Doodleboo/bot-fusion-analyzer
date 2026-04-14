class TransparencyException(Exception):
    pass

class MissingBotContext(Exception):
    pass

class DifferentFusionsInSameGalleryMessage(Exception):
    pass

class MisnumberedGalleryID(Exception):
    def __init__(self, filename_fusion_id: str, content_fusion_id: str) -> None:
        self.filename_fusion_id = filename_fusion_id
        self.content_fusion_id = content_fusion_id