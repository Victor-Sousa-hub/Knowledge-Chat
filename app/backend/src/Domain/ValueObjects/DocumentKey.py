from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentKey:
    session_id: str
    file_name: str

    @property
    def s3_key(self) -> str:
        return f"sessions/{self.session_id}/{self.file_name}"
