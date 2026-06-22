from app.services.system_settings import mask_api_key


def test_mask_api_key_hides_sensitive_middle() -> None:
    assert mask_api_key("sk-1234567890abcdef") == "sk-****cdef"
    assert mask_api_key("short") == "****"
    assert mask_api_key("") == ""
