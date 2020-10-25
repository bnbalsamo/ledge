"""
A responder that handles Slack events API url verification requests.

See https://api.slack.com/events/url_verification for more information.
"""
import json

import environ

from ledge import ResponderImplementation
from ledge.helpers import content_to_json, text_response
from ledge.helpers.slack import verify_slack_request


class SubConfig:  # pylint: disable=too-few-public-methods
    """Slack Responder subconfig."""

    signing_secret = environ.var(help="Your slack app signing secret.")


class SlackURLVerificationResponder(ResponderImplementation):
    """A simple demo responder implementation."""

    name = "slack_url_verification_responder"
    subconfig = SubConfig

    def handles(self, request, content):
        """Handle slack url verificatio requests."""
        # Request is verified
        if not verify_slack_request(
            request,
            content,
            self.config.slack_url_verification_responder.signing_secret,
        ):
            return False

        # Request is JSON
        try:
            request_json = content_to_json(content)
        except json.JSONDecodeError:
            return False

        # Request has proper keys
        for key in ["token", "challenge", "type"]:
            if key not in request_json:
                return False

        # Request is proper type
        if request_json["type"] != "url_verification":
            return False

        return True

    def respond(self, request, content):
        """Return the url verification response."""
        rjson = content_to_json(content)
        text_response(request, rjson["challenge"])
        request.logger.msg("Slack url verification response sent!")
