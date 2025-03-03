import asyncio
import re
from urllib.parse import urlparse

import aiohttp
import pydantic
from multidict import CIMultiDictProxy

from .common import get_base_request_headers
from .consts import BASE_URL, USER_EVENTS
from .exceptions import GithubAPIError
from .models import Events

PAGE_SIZE = 100


async def get_user_events(
    username: str, auth_token: str | None = None
) -> Events:
    url = f"{BASE_URL}{USER_EVENTS.format(username)}"
    headers = get_base_request_headers()
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with aiohttp.ClientSession() as session:
            n_pages = await _get_total_pages(session, url, headers)
            coros = [
                _get_page(n + 1, session, url, headers) for n in range(n_pages)
            ]
            contents = await asyncio.gather(*coros)
            events = []
            for content in contents:
                events += Events.model_validate_json(content).root
            return Events(root=events)
    except pydantic.ValidationError as e:
        raise GithubAPIError(
            "Incoherence between response and expected schemas"
        ) from e
    except aiohttp.ClientError as e:
        raise GithubAPIError("Could not receive data from Github") from e


def _get_pages_from_headers(headers: CIMultiDictProxy) -> int:
    links = headers["link"]
    (last_link_entry,) = [x for x in links.split(",") if 'rel="last"' in x]
    last_link_url, _ = last_link_entry.split(";")
    parse_result = urlparse(last_link_url[1:-1])
    query_params = parse_result.query.split("&")
    (last_page_query_param_str,) = [
        x for x in query_params if re.match("^page=.*", x)
    ]
    _, last_page_str = last_page_query_param_str.split("=")
    return int(last_page_str)


async def _get_total_pages(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
) -> int:
    full_url = f"{url}?per_page={PAGE_SIZE}"
    async with session.get(full_url, headers=headers) as response:
        if 400 <= response.status < 500:
            raise GithubAPIError(
                "Could not get event page count. Make sure username is correct"
            )
        if response.status >= 500:
            raise GithubAPIError("Unknown API-side error. Try again later")
        return _get_pages_from_headers(response.headers)


async def _get_page(
    page_number: int,
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
) -> bytes:
    full_url = f"{url}?page={page_number}&per_page={PAGE_SIZE}"
    async with session.get(full_url, headers=headers) as response:
        if 400 <= response.status < 500:
            raise GithubAPIError(
                "Could not get events. Make sure username is correct"
            )
        if response.status >= 500:
            raise GithubAPIError("Unknown API-side error. Try again later")
        return await response.content.read()
