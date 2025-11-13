import uuid

import pytest
from sqlalchemy import select

from app.models.model_subjects import Subjects


async def _create_subject(async_session, name: str) -> uuid.UUID:
    subject = Subjects(id=uuid.uuid4(), name=name)
    async_session.add(subject)
    await async_session.commit()
    await async_session.refresh(subject)
    return subject.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,expected_status,expected_detail",
    [
        ("session_token_admin", 200, None),
        ("session_token_teacher", 403, "This user can't create new subjects"),
        ("session_token_student", 403, "This user can't create new subjects"),
    ],
)
async def test_subjects_create(
    client,
    async_session,
    request,
    token_fixture,
    expected_status,
    expected_detail,
):
    subject_name = f"Subject-{uuid.uuid4()}"
    token = request.getfixturevalue(token_fixture)

    response = await client.post(
        "/subjects",
        headers={"Authorization": token},
        params={"name": subject_name},
    )

    assert response.status_code == expected_status  # проверяем код ответа от API

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
        created_subject = await async_session.execute(
            select(Subjects).where(Subjects.name == subject_name)
        )
        assert created_subject.fetchone() is not None  # удостоверяемся, что предмет записан в базу
    else:
        assert response.json() == {"detail": expected_detail}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,subject_exists,expected_status,expected_detail",
    [
        ("session_token_admin", True, 200, None),
        ("session_token_admin", False, 404, "This subject not exists"),
        ("session_token_teacher", True, 403, "This user can't create new subjects"),
    ],
)
async def test_subjects_patch(
    client,
    async_session,
    request,
    token_fixture,
    subject_exists,
    expected_status,
    expected_detail,
):
    if subject_exists:
        subject_id = await _create_subject(async_session, f"Patch-{uuid.uuid4()}")
    else:
        subject_id = uuid.uuid4()

    token = request.getfixturevalue(token_fixture)
    response = await client.patch(
        f"/subjects/{subject_id}",
        headers={"Authorization": token},
    )

    assert response.status_code == expected_status

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
    else:
        assert response.json() == {"detail": expected_detail}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture,subject_exists,expected_status,expected_detail",
    [
        ("session_token_admin", True, 200, None),
        ("session_token_teacher", True, 403, "This user can't create new subjects"),
        ("session_token_admin", False, 404, "This subject not exists"),
    ],
)
async def test_subjects_delete(
    client,
    async_session,
    request,
    token_fixture,
    subject_exists,
    expected_status,
    expected_detail,
):
    if subject_exists:
        subject_id = await _create_subject(async_session, f"Delete-{uuid.uuid4()}")
    else:
        subject_id = uuid.uuid4()

    token = request.getfixturevalue(token_fixture)
    response = await client.delete(
        f"/subjects/{subject_id}",
        headers={"Authorization": token},
    )

    assert response.status_code == expected_status  # проверяем, что статус соответствует ожидаемому сценарию

    if expected_detail is None:
        assert response.json() == {"status": "ok"}
        removed_subject = await async_session.get(Subjects, subject_id)
        assert removed_subject is None  # убеждаемся, что предмет удален
    else:
        assert response.json() == {"detail": expected_detail}

