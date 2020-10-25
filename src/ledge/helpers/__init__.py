"""
Ledge supplied helper functions.

These functions are meant to be used in plugin implementations
to facilitate common workflows.
"""

import json


def content_to_json(
    content, json_loads_args=None, json_loads_kwargs=None, encoding="utf-8"
):
    """
    Convert request content into JSON.

    :param bytes content: The request content
    :param tuple json_loads_args: Arguments to pass through to the call
        to json.loads.
    :param dict json_loads_kwargs: Keyword argumetns to pass through to
        the call to json.loads.
    :param str encoding: The encoding to use to decode the request content.
    :rtype: dict
    :returns: The JSON content of the request.
    """
    if json_loads_args is None:
        json_loads_args = ()
    if json_loads_kwargs is None:
        json_loads_kwargs = {}
    return json.loads(content.decode(encoding), *json_loads_args, **json_loads_kwargs)


def json_response(  # pylint: disable=too-many-arguments
    request,
    dictionary,
    json_dumps_args=None,
    json_dumps_kwargs=None,
    encoding="utf-8",
    finish=True,
):
    """
    Reply to the given request with a JSON object.

    :param twisted.web.http.Request request: The request to respond to.
    :param dict dictionary: A JSON serializable dictionary to use as the response.
    :param tuple json_dumps_args: Arguments to pass through to the call
        to `json.dumps`
    :param dict json_dumps_kwargs: Keyword arguments to pass through to
        the call to `json.dumps`
    :param str encoding: The encoding to use to encode the JSON obj to bytes.
    :param bool finish: If true, finish the request after writing the JSON.
    """
    if json_dumps_args is None:
        json_dumps_args = ()
    if json_dumps_kwargs is None:
        json_dumps_kwargs = {}
    data = json.dumps(dictionary, *json_dumps_args, **json_dumps_kwargs).encode(
        encoding
    )
    request.write(data)
    if finish:
        request.finish()


def text_response(request, text, encoding="utf-8", finish=True):
    """
    Reply to the given request with text.

    :param twisted.web.http.Request request: The request to respond to.
    :param str text: The text to reply with.
    :param str encoding: The encoding to use to encode the text to bytes.
    :param bool finish: If true, finish the request after writing the text.
    """
    data = text.encode(encoding)
    request.write(data)
    if finish:
        request.finish()


def get_headers(request, encoding="utf-8"):
    """
    Wrap `twisted.web.http.Request.getAllHeaders` so it returns strs.

    :param twisted.web.http.Request request: The request to get the headers from.
    :param str encoding: The encoding to use to decode the header bytes to text.

    :rtype: dict
    :return: A dictionary, whose keys and values are strs, representing the
        request headers.
    """
    raw_headers = request.getAllHeaders()
    return {k.decode(encoding): raw_headers[k].decode(encoding) for k in raw_headers}
