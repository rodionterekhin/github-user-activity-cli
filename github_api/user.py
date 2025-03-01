import aiohttp
import pydantic

from .common import get_base_request_headers
from .consts import BASE_URL, USER_EVENTS
from .exceptions import GithubAPIError
from .models import Events


async def get_user_events(
    username: str, auth_token: str | None = None
) -> Events:
    url = f"{BASE_URL}{USER_EVENTS.format(username)}"
    headers = get_base_request_headers()
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                content = await resp.content.read()
                return Events.model_validate_json(content)
    except pydantic.ValidationError as e:
        raise GithubAPIError(
            "Incoherence between response and expected schemas"
        ) from e
    except aiohttp.ClientError as e:
        raise GithubAPIError("Could not receive data from Github") from e
