from attr import dataclass


@dataclass
class Description:
    text: str
    actions: list[str]

    def __str__(self) -> str:
        return f"{self.text}\n{self.actions}"
