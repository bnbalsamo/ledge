"""Helpers for working with the slack events API."""

import hashlib
import hmac

from ledge.helpers import get_headers


def verify_slack_request(request, content, secret):
    """
    Use Slacks hmac impl. to verify a request.

    :param twisted.web.http.Request request: The request
    :param bytes content: The request content
    :param str secret: Slack signing secret

    :rtype: bool
    :returns: Whether or not the request is from Slack
    """
    headers = get_headers(request)
    timestamp = headers.get("x-slack-request-timestamp")
    sig = headers.get("x-slack-signature")
    if timestamp is None or sig is None:
        return False
    # From the slack python sdk, slight alterations
    req = str.encode("v0:" + str(timestamp) + ":") + content
    request_hash = "v0=" + hmac.new(str.encode(secret), req, hashlib.sha256).hexdigest()
    if hmac.compare_digest(request_hash, sig):
        request.logger.msg("Received request with correct slack signature")
        return True
    request.logger.msg("Received request with bad slack signature")
    return False
