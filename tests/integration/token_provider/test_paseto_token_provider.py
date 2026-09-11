from uuid import uuid7

import pytest

from auth.infrastructure.key_provider.file_key_pair_provider import \
    FileKeysPairProvider
from auth.infrastructure.token_provider.paseto_token_provider import \
    PasetoTokenProvider


@pytest.fixture
def file_key_provider():
    return FileKeysPairProvider(
        private_key_path="/run/secrets/private_key",
        public_key_path="/run/secrets/public_key"
    )


@pytest.fixture
def paseto_token_provider(file_key_provider):
    return PasetoTokenProvider(
        private_key_provider=file_key_provider,
        public_key_provider=file_key_provider
    )


def test_issue_and_verify_refresh_token(paseto_token_provider):
    user_id = uuid7()
    session_id = uuid7()

    tokens = paseto_token_provider.issue(user_id, session_id)

    payload = paseto_token_provider.verify_refresh(tokens.refresh_token)

    assert payload.user_id == user_id
    assert payload.session_id == session_id
