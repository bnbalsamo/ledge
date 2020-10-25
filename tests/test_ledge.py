"""Unit tests for ledge."""
import hmac
import json
import os
from uuid import uuid4

import pytest
import pytest_twisted

import ledge


@pytest.fixture
def mock_config():
    """Mock minimally viable config object fixture."""

    class MockConfig:
        """Mock minimally viable config object."""

        handlers = []
        responders = []

    return MockConfig


def test_version_available():
    """Test the module has a version dunder."""
    assert hasattr(ledge, "__version__") and isinstance(ledge.__version__, str)


def test_start(mocker):
    """Confirm the start command runs the reactor."""
    mock_reactor = mocker.MagicMock()
    mocker.patch("ledge._cmds.reactor", mock_reactor)
    ledge._cmds.start()
    mock_reactor.run.assert_called_once()


@pytest_twisted.inlineCallbacks
def test_simple(mocker, mock_config):
    """
    Test requests finish with no handlers or responders specified.
    """
    mock_config = mocker.MagicMock()
    mock_config.handlers = []
    mock_config.responders = []
    app = ledge._app.Ledge(mock_config)
    request = mocker.MagicMock()
    response_d, handler_ds = app.handle_request(request, b"123")
    yield response_d
    for handler_deferred in handler_ds:
        yield handler_deferred
    request.finish.assert_called_once()


@pytest_twisted.inlineCallbacks
def test_process_true(mocker):
    """
    Test the process function when handles is true.

    process stitches together handles and handle
    """
    mock_handler = mocker.MagicMock()
    mock_handler.process = ledge._bases.HandlerImplementation.process
    mock_handler.handles = mocker.MagicMock(return_value=True)
    request = mocker.MagicMock()
    data = mocker.MagicMock()
    yield mock_handler.process(mock_handler, request, data)
    mock_handler.handle.assert_called_once_with(request, data)


@pytest_twisted.inlineCallbacks
def test_process_false(mocker):
    """
    Test the process function when handles is false.

    process stitches together handles and handle
    """
    mock_handler = mocker.MagicMock()
    mock_handler.process = ledge._bases.HandlerImplementation.process
    mock_handler.handles = mocker.MagicMock(return_value=False)
    request = mocker.MagicMock()
    data = mocker.MagicMock()
    yield mock_handler.process(mock_handler, request, data)
    mock_handler.handle.assert_not_called()


@pytest_twisted.inlineCallbacks
def test_handler(mocker):
    """
    Test handlers get the correct args.
    """
    mock_handler = mocker.MagicMock()
    mock_handler.name = "Mock Handler"

    mock_config = mocker.MagicMock()
    mock_config.handlers = []
    mock_config.responders = []

    app = ledge._app.Ledge(mock_config)
    app._handlers = [mock_handler]

    requests = [mocker.MagicMock() for _ in range(2)]
    contents = [uuid4().hex.encode("utf-8") for _ in range(len(requests))]
    for i in range(len(requests)):
        request = requests[i]
        content = contents[i]
        response_d, handler_ds = app.handle_request(request, content)
        yield response_d
        for handler_deferred in handler_ds:
            yield handler_deferred
        mock_handler.process.assert_called_with(request, content)
    assert mock_handler.process.call_count == len(requests)


@pytest_twisted.inlineCallbacks
def test_responder(mocker):
    """
    Test responders get the correct args.
    """
    mock_responder = mocker.MagicMock()
    mock_responder.name = "Mock Responder"
    mock_responder.handles = mocker.MagicMock(return_value=True)

    mock_config = mocker.MagicMock()
    mock_config.handlers = []
    mock_config.responders = []

    app = ledge._app.Ledge(mock_config)
    app._responders = [mock_responder]

    request = mocker.MagicMock()
    content = b"123"
    response_d, handler_ds = app.handle_request(request, content)
    yield response_d
    mock_responder.respond.assert_called_once_with(request, content)


@pytest_twisted.inlineCallbacks
def test_end_to_end(mocker):
    """End to end smoke test of very basic responder + handler."""
    os.environ["LEDGE_RESPONDERS"] = "ledge.responders.DemoResponder"
    os.environ["LEDGE_HANDLERS"] = "ledge.handlers.DemoHandler"
    config = ledge._config.get_config()
    app = ledge._app.Ledge(config)
    request = mocker.MagicMock()
    # For debugging
    request.logger.msg = lambda x: print(x)
    content = b"123"
    response_d, handler_ds = app.handle_request(request, content)
    yield response_d
    for handler_deferred in handler_ds:
        yield handler_deferred
    request.write.assert_called_once_with(b":)")
    request.finish.assert_called_once()
    del os.environ["LEDGE_RESPONDERS"]
    del os.environ["LEDGE_HANDLERS"]


def test_content_to_json():
    """Test request content is correctly converted into a dict."""
    content = b'{"foo": "bar"}'
    assert ledge.helpers.content_to_json(content) == {"foo": "bar"}


def test_json_response(mocker):
    """Test a dict is correctly converted to bytes + written."""
    request = mocker.MagicMock()
    ledge.helpers.json_response(request, {"foo": "bar"})
    request.write.assert_called_once_with(b'{"foo": "bar"}')
    request.finish.assert_called_once()


def test_text_response(mocker):
    """Test a str is correctly converted to bytes + written."""
    request = mocker.MagicMock()
    ledge.helpers.text_response(request, "foo")
    request.write.assert_called_once_with(b"foo")
    request.finish.assert_called_once()


def test_json_response_no_finish(mocker):
    """Test partial JSON response."""
    request = mocker.MagicMock()
    ledge.helpers.json_response(request, {"foo": "bar"}, finish=False)
    request.write.assert_called_once_with(b'{"foo": "bar"}')
    request.finish.assert_not_called()


def test_text_response_no_finish(mocker):
    """Test partial str response."""
    request = mocker.MagicMock()
    ledge.helpers.text_response(request, "foo", finish=False)
    request.write.assert_called_once_with(b"foo")
    request.finish.assert_not_called()


def test_get_headers(mocker):
    """Test headers are properly converted to strs."""
    request = mocker.MagicMock()
    request.getAllHeaders = mocker.MagicMock(return_value={b"foo": b"bar"})
    assert ledge.helpers.get_headers(request) == {"foo": "bar"}


def test_inject_logger(mocker):
    """Test loggers are injected onto each request."""
    request = mocker.MagicMock()
    ledge._utils.inject_logger(request)
    request.logger.msg("Doesn't raise an exception!")


def test_make_name_safe():
    """Test names are made env var safe."""
    cases = {
        "name with spaces": "namexwithxspaces",
        "name_without_spaces": "name_without_spaces",
    }
    for before, after in cases.items():
        assert ledge._utils.make_name_safe(before) == after


@pytest_twisted.inlineCallbacks
def test_echo_handler(mocker):
    """Confirm the echo handler echos things exactly."""
    os.environ["LEDGE_HANDLERS"] = "ledge.handlers.EchoHandler"
    config = ledge._config.get_config()
    app = ledge._app.Ledge(config)
    assert isinstance(app._handlers[0], ledge.handlers.EchoHandler)
    request = mocker.MagicMock()
    content = b"123"
    response_d, handler_ds = app.handle_request(request, content)
    yield response_d
    for handler_deferred in handler_ds:
        yield handler_deferred
    request.logger.msg.assert_any_call(f"Request content: {content.decode('utf-8')}")
    request.finish.assert_called_once()
    del os.environ["LEDGE_HANDLERS"]


@pytest_twisted.inlineCallbacks
def test_two_handlers(mocker):
    """
    Test multiple handlers can be specified via env vars.
    """
    os.environ[
        "LEDGE_HANDLERS"
    ] = "ledge.handlers.EchoHandler,ledge.handlers.DemoHandler"
    config = ledge._config.get_config()
    app = ledge._app.Ledge(config)
    assert len(app._handlers) == 2
    for handler in app._handlers:
        handler.handle = mocker.MagicMock()
    request = mocker.MagicMock()
    content = b"123"
    response_d, handler_ds = app.handle_request(request, content)
    yield response_d
    for handler_deferred in handler_ds:
        yield handler_deferred
    for handler in app._handlers:
        handler.handle.assert_called_once_with(request, content)


def test_slack_verification(mocker):
    """
    Test slack signature verification (positive).
    """
    mock_request = mocker.MagicMock()
    secret = "itsasecret"
    content = "Stuff and Things".encode()
    timestamp = "1234"
    base_string = str.encode("v0:" + timestamp + ":") + content
    signature = hmac.new(
        secret.encode(), msg=base_string, digestmod="sha256"
    ).hexdigest()
    mock_request_headers = {
        "x-slack-request-timestamp": timestamp,
        "x-slack-signature": "v0={}".format(signature),
    }
    mock_request.getAllHeaders = mocker.MagicMock(
        return_value={
            k.encode("utf-8"): mock_request_headers[k].encode("utf-8")
            for k in mock_request_headers
        }
    )
    assert ledge.helpers.slack.verify_slack_request(mock_request, content, secret)


def test_bad_slack_verification(mocker):
    """
    Test slack signature verification (negative).
    """
    mock_request = mocker.MagicMock()
    secret = "itsasecret"
    content = "Stuff and Things".encode()
    timestamp = "1234"

    base_string = str.encode("v0:" + timestamp + ":") + content
    signature = hmac.new(
        secret.encode(), msg=base_string, digestmod="sha256"
    ).hexdigest()
    mock_request_headers = {
        "x-slack-request-timestamp": timestamp,
        "x-slack-signature": "v0={}".format(signature),
    }
    mock_request.getAllHeaders = mocker.MagicMock(
        return_value={
            k.encode("utf-8"): mock_request_headers[k].encode("utf-8")
            for k in mock_request_headers
        }
    )
    assert not ledge.helpers.slack.verify_slack_request(mock_request, content, "wrong")


@pytest_twisted.inlineCallbacks
def test_slack_responder(mocker):
    """
    Test the slack responder verifies signatures + responds properly.
    """
    os.environ["LEDGE_RESPONDERS"] = "ledge.responders.SlackURLVerificationResponder"
    secret = "itsasecret"
    os.environ["LEDGE_SLACK_URL_VERIFICATION_RESPONDER_SIGNING_SECRET"] = secret
    config = ledge._config.get_config()
    app = ledge._app.Ledge(config)

    content_dict = {"token": "foo", "challenge": "abc123", "type": "url_verification"}
    content = json.dumps(content_dict).encode()
    timestamp = "456"
    mock_request = mocker.MagicMock()

    base_string = str.encode("v0:" + timestamp + ":") + content
    signature = hmac.new(
        secret.encode(), msg=base_string, digestmod="sha256"
    ).hexdigest()
    mock_request_headers = {
        "x-slack-request-timestamp": timestamp,
        "x-slack-signature": "v0={}".format(signature),
    }
    mock_request.getAllHeaders = mocker.MagicMock(
        return_value={
            k.encode("utf-8"): mock_request_headers[k].encode("utf-8")
            for k in mock_request_headers
        }
    )

    response_d, handler_ds = app.handle_request(mock_request, content)
    yield response_d
    for handler_deferred in handler_ds:
        yield handler_deferred
    mock_request.write.assert_called_once_with(content_dict["challenge"].encode())
    mock_request.finish.assert_called_once()
    del os.environ["LEDGE_RESPONDERS"]
    del os.environ["LEDGE_SLACK_URL_VERIFICATION_RESPONDER_SIGNING_SECRET"]
