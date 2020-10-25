"""
A handler for slack webhooks.

Slacky is a simple slack bot that demonstrates the ability for ledge
to handle blocking code (the POSTs to to the slack endpoints).

It is meant to be configured as a slack bot that responds to mentions.

It requires ledge, requests, and glom in order to be run.
"""
import json

import environ
import requests
from glom import glom

from ledge import HandlerImplementation
from ledge.helpers import content_to_json
from ledge.helpers.slack import verify_slack_request


class SlackAPIError(RuntimeError):
    """Errors provided by the slack API."""


def parse_api_response(resp):
    """
    Parse the response from calling the Slack API.

    Raise if there were any issues.

    :param requests.Response resp: A response from the slack API
    :rtype: None
    """
    # If this goes off something went really wrong - the Slack API should respond
    # with 200's even if there an error (which is in the JSON)
    resp.raise_for_status()
    reply_json = resp.json()
    if not reply_json["ok"]:
        # Something went wront - Slack gave us back an error
        raise SlackAPIError(str(reply_json))


def say_something(channel, msg, oauth_token):
    """
    Respond in a specific channel as the bot.

    :param str channel: The channel identifier
    :param str msg: The message to the send to the channel
    :rtype: None
    """
    # Slack is picky about including the encoding on the Content-Type header
    resp = requests.post(
        "https://slack.com/api/chat.postMessage?charset=utf8",
        json={"channel": channel, "text": msg},
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(oauth_token),
        },
        timeout=10,
    )
    parse_api_response(resp)



class SlackySubConfig:  # pylint: disable=too-few-public-methods
    """Slack Responder subconfig."""

    oauth_token = environ.var(help="Your slack oauth token")


class Slacky(HandlerImplementation):
    """A slack bot implemented as a ledge handler."""

    name = "slacky"
    subconfig = SlackySubConfig

    def handles(self, request, content):
        """
        Handle requests if they...

        - Are verifiably from slack
        - Deserialize from JSON
        - Contain the required json keys
        """
        if not verify_slack_request(
            request,
            content,
            self.config.slack_url_verification_responder.signing_secret,
        ):
            return False

        try:
            request_json = content_to_json(content)
        except json.JSONDecodeError:
            return False

        if not request_json.get("event"):
            return False
        if not request_json["event"].get("channel"):
            return False
        return True

    def handle(self, request, content):
        request_json = content_to_json(content)
        channel = glom(request_json, "event.channel")
        msg = "Hello World!"
        say_something(
            channel, msg, self.config.slacky.oauth_token,
        )
