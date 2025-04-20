from enums import Description, Severity


class Issue():
    description: Description
    severity: Severity

    def __str__(self) -> str:
        return self.description.value


class Issues():
    issue_list: list[Issue]

    def __init__(self):
        self.issue_list = []

    def __str__(self) -> str:
        if len(self.issue_list) == 1:
            return str(self.issue_list[0])

        result = ""
        for issue in self.issue_list:
            result += f"- {issue}\n"
        return result

    def add(self, issue: Issue):
        self.issue_list.append(issue)

    def has_issue(self, issue_type) -> bool:
        return any(isinstance(issue, issue_type) for issue in self.issue_list)


class DifferentSprite(Issue):
    description = Description.different_fusion_id
    severity = Severity.refused

    def __init__(self, filename_fusion_id: str, content_fusion_id: str) -> None:
        self.filename_fusion_id = filename_fusion_id
        self.content_fusion_id = content_fusion_id

    def __str__(self) -> str:
        return f"{self.description.value} ({self.filename_fusion_id}) ({self.content_fusion_id})"


class EggSprite(Issue):
    description = Description.egg
    severity = Severity.ignored


class MissingFilename(Issue):
    description = Description.missing_file_name
    severity = Severity.refused


class MissingSprite(Issue):
    description = Description.missing_file
    severity = Severity.ignored


class IconSprite(Issue):
    description = Description.icon
    severity = Severity.ignored


class CustomBase(Issue):
    description = Description.custom
    severity = Severity.accepted

    def __init__(self, base_name: str = "Unknown") -> None:
        self.base_name = base_name

    def __str__(self) -> str:
        return f"{self.base_name} {self.description.value}"


class IncomprehensibleSprite(Issue):
    description = Description.incomprehensible
    severity = Severity.ignored


class OutOfDex(Issue):
    description = Description.invalid_fusion_id
    severity = Severity.refused

    def __init__(self, fusion_id: str) -> None:
        self.fusion_id = fusion_id

    def __str__(self) -> str:
        return f"{self.description.value} ({self.fusion_id})"


class InvalidSize(Issue):
    description = Description.invalid_size
    severity = Severity.refused

    def __init__(self, size: tuple) -> None:
        self.size = size

    def __str__(self) -> str:
        return f"{self.description.value} {self.size}"


class FileName(Issue):
    description = Description.file_name
    severity = Severity.accepted

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.description.value}: {self.filename}"


class ColorAmount(Issue):
    description = Description.colour_amount
    severity = Severity.accepted

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class ColorExcessRefused(Issue):
    description = Description.colour_excess
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (max: {self.maximum})"


class ColorExcessControversial(Issue):
    description = Description.colour_excess
    severity = Severity.controversial

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (over {self.maximum})"


class ColorOverExcess(Issue):
    description = Description.colour_excess
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (+{self.maximum})"


class SimilarityExcessControversial(Issue):
    description = Description.high_similarity
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (over {self.maximum})"


class SimilarityExcessRefused(Issue):
    description = Description.refused_similarity
    severity = Severity.controversial

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (limit: {self.maximum})"


class MissingTransparency(Issue):
    description = Description.no_transparency
    severity = Severity.refused


class AsepriteUser(Issue):
    description = Description.aseprite_user
    severity = Severity.accepted

    def __init__(self, ratio: float) -> None:
        self.ratio = int(ratio)

    def __str__(self) -> str:
        return f"{self.description.value} (r{self.ratio})"


class GraphicsGaleUser(Issue):
    description = Description.graphics_gale_user
    severity = Severity.accepted


class TransparencyAmount(Issue):
    description = Description.transparency_amount
    severity = Severity.controversial

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class SimilarityAmount(Issue):
    description = Description.similarity_amount
    severity = Severity.controversial

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class HalfPixelsAmount(Issue):
    description = Description.half_pixels_amount
    severity = Severity.refused

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class PokemonNames(Issue):
    severity = Severity.accepted

    def __init__(self, head_id: str, body_id: str) -> None:
        self.head_name = head_id
        self.body_name = body_id

    def __str__(self) -> str:
        return f"{self.head_name}/{self.body_name}"
