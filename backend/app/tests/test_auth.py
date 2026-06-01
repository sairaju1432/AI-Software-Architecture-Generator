from app.core.security import create_access_token, decode_token, hash_password, verify_password

def test_password_hash_and_verify():
    hashed = hash_password("ChangeMe123!")
    assert verify_password("ChangeMe123!", hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_roundtrip():
    token = create_access_token("user-1")
    assert decode_token(token) == "user-1"
