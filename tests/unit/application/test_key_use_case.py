from auth.application_layer.dto.key import PublicKey, PublicKeyResponse
from auth.application_layer.use_cases.key import KeyService
from tests.unit.application.fakes import FakeKeyProvider


def test_get_public_keys_returns_public_keys():
    response = PublicKeyResponse(
        keys=(
            PublicKey(
                kid="auth-key-01",
                paserk="k4.public.test-key"
            ),
        )
    )

    key_provider = FakeKeyProvider(response)
    key_service = KeyService(key_provider)

    result = key_service.get_public_keys()

    assert result is response
    assert result.keys == response.keys
    assert key_provider.counter == 1
