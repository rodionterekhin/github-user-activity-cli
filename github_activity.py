import argparse
import asyncio
import sys

from github_api import (
    Event,
    Events,
    EventType,
    GithubAPIError,
    get_user_events,
)


def get_args_or_fail() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "username",
        help="github username to show activity for",
        type=str,
    )
    return parser.parse_args()


def print_event(event: Event) -> None:
    txt: str = f"{event.created_at:%Y-%m-%d %H:%M:%S}: "
    match event.type:
        case EventType.COMMIT_COMMENT_EVENT:
            txt += "Created a comment on commit"
        case EventType.CREATE_EVENT:
            txt += f"Created a {event.payload.ref_type.value}"
            if event.payload.ref:
                txt += f' "{event.payload.ref}"'
        case EventType.DELETE_EVENT:
            txt += f"Deleted a {event.payload.ref_type.value}"
            if event.payload.ref:
                txt += f' "{event.payload.ref}"'
        case EventType.FORK_EVENT:
            txt += f"Forked a repo {event.payload.forkee.full_name}"
        case EventType.GOLLUM_EVENT:
            txt += "Created or updated a wiki page"
        case EventType.ISSUE_COMMENT_EVENT:
            txt += f"{event.payload.action.capitalize()} an issue/PR comment"
        case EventType.ISSUES_EVENT:
            txt += f"{event.payload.action.capitalize()} an issue"
        case EventType.MEMBER_EVENT:
            txt += f"Added collaborator {event.payload.member.name}"
        case EventType.PUBLIC_EVENT:
            txt += "Made private repo public"
        case EventType.PULL_REQUEST_EVENT:
            txt += f"{event.payload.action.capitalize()} a pull request"
        case EventType.PULL_REQUEST_REVIEW_EVENT:
            txt += f"{event.payload.action.capitalize()} a pull request review"
        case EventType.PULL_REQUEST_REVIEW_COMMENT_EVENT:
            txt += (
                f"{event.payload.action.capitalize()} a pull request review"
                " thread"
            )
        case EventType.PUSH_EVENT:
            if event.payload.size == 0:
                if event.payload.distinct_size == 0:
                    txt += "One commit"
                else:
                    txt += f"{event.payload.distinct_size} commits"
                txt += " swapped in"
            elif event.payload.size == 1:
                txt += "One commit pushed to"
            else:
                txt += f"{event.payload.size} commmits pushed to"
            txt += f' "{event.payload.ref}"'
        case EventType.RELEASE_EVENT:
            txt += f"{event.payload.action} a release"
        case EventType.SPONSORSHIP_EVENT:
            txt += (
                f"{event.payload.action} activity related to sponsorship"
                " listing"
            )
        case EventType.WATCH_EVENT:
            txt += "Starred a repo"
    print(txt)


async def main():
    args = get_args_or_fail()
    username: str = args.username
    try:
        events: Events = await get_user_events(username)
    except GithubAPIError as e:
        print(f"Error! {e}")
        sys.exit(-1)
    event: Event
    for event in events.root:
        print_event(event)


if __name__ == "__main__":
    asyncio.run(main())
