from core.security import issue_csrf_token, validate_csrf_token

def test_csrf_round_trip():
    session = {}
    token = issue_csrf_token(session)
    assert validate_csrf_token(session, token)
    assert not validate_csrf_token(session, "wrong")
