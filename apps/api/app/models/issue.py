from dataclasses import dataclass


@dataclass
class Issue:
    file_path: str
    line_number: int
    tool: str
    severity: str
    message: str