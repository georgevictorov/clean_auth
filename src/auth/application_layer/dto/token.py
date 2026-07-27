from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPairDTO:
    access_token: str
    refresh_token: str
