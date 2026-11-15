def test_invalid_password_payload_does_not_echo_secret(client):
    secret = "secret-should-not-be-echoed"
    response = client.post("/api/v1/auth/login", json={"email":"bad", "password":secret, "forbidden":secret})
    assert response.status_code == 422
    assert secret not in response.text
    assert isinstance(response.json()["detail"], str)
import pytest




@pytest.mark.parametrize("email", [None, 42])
@pytest.mark.parametrize("endpoint", ["login", "forgot-password"])
def test_wrong_email_types_are_validation_errors(client, email, endpoint):
    body = {"email": email}
    if endpoint == "login":
        body["password"] = "ValidPassword123!"
    assert client.post("/api/v1/auth/"+endpoint, json=body).status_code == 422


def test_numeric_email_on_account_update_is_rejected(client, auth_headers):
    headers = auth_headers()
    user = client.get('/api/v1/auth/me', headers=headers).json()
    assert client.patch(f'/api/v1/users/{user["id"]}', headers=headers, json={"email": 42}).status_code == 422
