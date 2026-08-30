"""IN06, IN07: Client setup, error handling, authentication, request options."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import anthropic
from _lib import client, test, finish, DEFAULT_MODEL

def test_not_found_error():
  try:
    client.messages.create(model="nonexistent-model", max_tokens=10, messages=[{"role": "user", "content": "Hi"}])
    return {"error": "Expected exception"}
  except anthropic.NotFoundError as e:
    return {"class": type(e).__name__, "status": e.status_code}
  except anthropic.APIError as e:
    return {"class": type(e).__name__, "status": e.status_code}

test("NotFoundError (bad model)", test_not_found_error)

def test_auth_error():
  bad_client = anthropic.Anthropic(api_key="sk-ant-invalid-key")
  try:
    bad_client.messages.create(model=DEFAULT_MODEL, max_tokens=10, messages=[{"role": "user", "content": "Hi"}])
    return {"error": "Expected AuthenticationError"}
  except anthropic.AuthenticationError as e:
    return {"class": type(e).__name__, "status": e.status_code}

test("AuthenticationError (bad key)", test_auth_error)

def test_error_classes_exist():
  return {
    "RateLimitError": hasattr(anthropic, "RateLimitError"),
    "BadRequestError": hasattr(anthropic, "BadRequestError"),
    "PermissionDeniedError": hasattr(anthropic, "PermissionDeniedError"),
    "InternalServerError": hasattr(anthropic, "InternalServerError"),
    "APIConnectionError": hasattr(anthropic, "APIConnectionError"),
  }

test("Error classes exist", test_error_classes_exist)

def test_basic_client():
  msg = client.messages.create(model=DEFAULT_MODEL, max_tokens=64, messages=[{"role": "user", "content": "Reply: OK"}])
  return {"text": msg.content[0].text, "model": msg.model}

test("Basic client + message", test_basic_client)

def test_request_options():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=64,
    messages=[{"role": "user", "content": "Reply: OK"}],
    timeout=30.0,
    extra_headers={"x-custom": "test"},
  )
  return {"text": msg.content[0].text}

test("RequestOptions (timeout, extra_headers)", test_request_options)

finish(__file__)
