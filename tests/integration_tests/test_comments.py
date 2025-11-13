import uuid

import pytest

from app.models.model_comments import CommentTypes, Comments


@pytest.fixture
async def comment_type_id(async_session):
    comment_type = CommentTypes(  # создаем тип комментария, чтобы можно было валидно привязать комментарии
        id=uuid.uuid4(),
        short_name="fb",
        name="Feedback",
    )
    async_session.add(comment_type)
    await async_session.commit()
    return comment_type.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,expected_status,expected_detail",
    [
        ("session_token_teacher", 201, None),
        ("session_token_student", 403, "Access denied: required role 'RoleUser.teacher', got 'RoleUser.student'"),
    ],
)
async def test_create_comment(
    request,
    client,
    async_session,
    comment_type_id,
    token_fixture,
    expected_status,
    expected_detail,
):
    setup_ids = request.getfixturevalue("setup_db")  # получаем идентификаторы сущностей, созданных в фикстурах
    comment_id = uuid.uuid4()
    payload = {
        "id": str(comment_id),
        "answer_id": str(setup_ids["answer_id"]),
        "type_id": str(comment_type_id),
    }

    token = request.getfixturevalue(token_fixture)
    response = await client.post(
        f"/worsk/{setup_ids['work_id']}/answers/{setup_ids['answer_id']}/comments",
        headers={"Authorization": token},
        json=payload,
    )

    assert response.status_code == expected_status  # проверяем код ответа

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
        comment_db = await async_session.get(Comments, comment_id)
        assert comment_db is not None  # убеждаемся, что комментарий действительно создан
        await async_session.refresh(comment_db)
    else:
        assert response.json() == {"detail": expected_detail}


async def _create_comment(async_session, answer_id: uuid.UUID, comment_type_id: uuid.UUID) -> uuid.UUID:
    comment_id = uuid.uuid4()
    comment = Comments(
        id=comment_id,
        answer_id=answer_id,
        type_id=comment_type_id,
        description="Initial text",
    )
    async_session.add(comment)
    await async_session.commit()
    await async_session.refresh(comment)
    return comment_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,comment_exists,expected_status,expected_detail",
    [
        ("session_token_teacher", True, 200, None),
        ("session_token_student", True, 403, "Access denied: required role 'RoleUser.teacher', got 'RoleUser.student'"),
        ("session_token_teacher", False, 404, "This Comment, not exists"),
    ],
)
async def test_update_comment(
    request,
    client,
    async_session,
    comment_type_id,
    token_fixture,
    comment_exists,
    expected_status,
    expected_detail,
):
    setup_ids = request.getfixturevalue("setup_db")
    new_comment_type = CommentTypes(
        id=uuid.uuid4(),
        short_name="fb2",
        name="Feedback new",
    )
    async_session.add(new_comment_type)
    await async_session.commit()

    if comment_exists:
        comment_id = await _create_comment(async_session, setup_ids["answer_id"], comment_type_id)
    else:
        comment_id = uuid.uuid4()

    token = request.getfixturevalue(token_fixture)
    response = await client.put(
        f"/worsk/{setup_ids['work_id']}/answers/{setup_ids['answer_id']}/comments/{comment_id}",
        headers={"Authorization": token},
        json={
            "type_id": str(new_comment_type.id),
            "description": "Updated text",
        },
    )

    assert response.status_code == expected_status  # убеждаемся, что API корректно сообщает об ошибке/успехе

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
        updated_comment = await async_session.get(Comments, comment_id)
        await async_session.refresh(updated_comment)
        assert updated_comment.type_id == new_comment_type.id  # проверяем, что изменился тип
        assert updated_comment.description == "Updated text"
    else:
        assert response.json() == {"detail": expected_detail}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,comment_exists,expected_status,expected_detail",
    [
        ("session_token_teacher", True, 200, None),
        ("session_token_student", True, 403, "Access denied: required role 'RoleUser.teacher', got 'RoleUser.student'"),
        ("session_token_teacher", False, 404, "This Comment, not exists"),
    ],
)
async def test_delete_comment(
    request,
    client,
    async_session,
    comment_type_id,
    token_fixture,
    comment_exists,
    expected_status,
    expected_detail,
):
    setup_ids = request.getfixturevalue("setup_db")

    if comment_exists:
        comment_id = await _create_comment(async_session, setup_ids["answer_id"], comment_type_id)
    else:
        comment_id = uuid.uuid4()

    token = request.getfixturevalue(token_fixture)
    response = await client.delete(
        f"/worsk/{setup_ids['work_id']}/answers/{setup_ids['answer_id']}/comments/{comment_id}",
        headers={"Authorization": token},
    )

    assert response.status_code == expected_status

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
        removed_comment = await async_session.get(Comments, comment_id)
        assert removed_comment is None  # комментарий должен быть удален из базы
    else:
        assert response.json() == {"detail": expected_detail}

