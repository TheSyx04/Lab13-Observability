from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_credit_card_and_passport() -> None:
    out = scrub_text("card 4111 1111 1111 1111 passport B1234567")
    assert "4111" not in out
    assert "B1234567" not in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_vietnamese_address_keyword() -> None:
    out = scrub_text("Ship to Quan 1 Nguyen Hue")
    assert "Quan 1 Nguyen Hue" not in out
    assert "REDACTED_VN_ADDRESS" in out
