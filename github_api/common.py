from functools import cache


@cache
def get_base_request_headers():
    return {"X-GitHub-Api-Version": "2022-11-28"}
