import pytest

from ....errors import ErrorsList
from ....threads.get import get_post_by_id
from ..editpost import resolve_edit_post


@pytest.mark.asyncio
async def test_edit_post_mutation_updates_post(user_graphql_info, user, user_post):
    data = await resolve_edit_post(
        None,
        user_graphql_info,
        input={"post": str(user_post.id), "body": "Edited post"},
    )

    assert not data.get("errors")
    assert data.get("post")
    assert data["post"] == await get_post_by_id(data["post"].id)
    assert data["post"].body == {"text": "Edited post"}


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_user_is_not_authorized(
    graphql_info, user_post
):
    data = await resolve_edit_post(
        None, graphql_info, input={"post": str(user_post.id), "body": "Edited post"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post", ErrorsList.ROOT_LOCATION]
    assert data["errors"].get_errors_types() == [
        "auth_error.not_post_author_error",
        "auth_error.not_authorized",
    ]


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_post_id_is_invalid(user_graphql_info):
    data = await resolve_edit_post(
        None,
        user_graphql_info,
        input={"post": "invalid", "body": "This is test post!"},
    )

    assert not data.get("thread")
    assert not data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post"]
    assert data["errors"].get_errors_types() == ["type_error.integer"]


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_post_doesnt_exist(user_graphql_info):
    data = await resolve_edit_post(
        None, user_graphql_info, input={"post": "4000", "body": "This is test post!"},
    )

    assert not data.get("thread")
    assert not data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post"]
    assert data["errors"].get_errors_types() == ["value_error.post_does_not_exist"]


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_post_author_is_other_user(
    user_graphql_info, other_user_post
):
    data = await resolve_edit_post(
        None,
        user_graphql_info,
        input={"post": str(other_user_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post"]
    assert data["errors"].get_errors_types() == ["auth_error.not_post_author_error"]


@pytest.mark.asyncio
async def test_edit_post_mutation_allowss_moderator_to_edit_other_user_post(
    moderator_graphql_info, other_user_post
):
    data = await resolve_edit_post(
        None,
        moderator_graphql_info,
        input={"post": str(other_user_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert not data.get("errors")


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_thread_is_closed(
    user_graphql_info, closed_user_thread_post
):
    data = await resolve_edit_post(
        None,
        user_graphql_info,
        input={"post": str(closed_user_thread_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post"]
    assert data["errors"].get_errors_types() == ["auth_error.thread_is_closed"]


@pytest.mark.asyncio
async def test_edit_post_mutation_allows_moderator_to_edit_post_in_closed_thread(
    moderator_graphql_info, closed_user_thread_post
):
    data = await resolve_edit_post(
        None,
        moderator_graphql_info,
        input={"post": str(closed_user_thread_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert not data.get("errors")


@pytest.mark.asyncio
async def test_edit_post_mutation_fails_if_category_is_closed(
    user_graphql_info, closed_category_user_post
):
    data = await resolve_edit_post(
        None,
        user_graphql_info,
        input={"post": str(closed_category_user_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert data.get("errors")
    assert data["errors"].get_errors_locations() == ["post"]
    assert data["errors"].get_errors_types() == ["auth_error.category_is_closed"]


@pytest.mark.asyncio
async def test_edit_post_mutation_allows_moderator_to_edit_post_in_closed_category(
    moderator_graphql_info, closed_category_user_post
):
    data = await resolve_edit_post(
        None,
        moderator_graphql_info,
        input={"post": str(closed_category_user_post.id), "body": "This is test post!"},
    )

    assert data.get("thread")
    assert data.get("post")
    assert not data.get("errors")
