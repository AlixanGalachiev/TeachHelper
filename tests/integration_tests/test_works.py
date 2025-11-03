
from typing import Literal
import uuid
import pytest

from app.models.model_tasks import StatusWork
from app.services.service_work import WorkUpdate

@pytest.fixture
def update_data():
    return WorkUpdate.model_validate(
        {
            "task_id": "7bd1af64-ccb7-448b-bb9e-943b6aaa590b",
            "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
            "finish_date": None,
            "status": "draft",
            "id": "48fd40b4-3d01-4ad3-998e-2338dbacd376",
            "answers": [
                {
                    "work_id": "48fd40b4-3d01-4ad3-998e-2338dbacd376",
                    "exercise_id": "c98ac0ab-69df-4c28-bd81-d255977e7097",
                    "file_url": None,
                    "id": "d5c8edc9-c427-4bb3-af6a-367f0bf49e16",
                    "criterions": [
                        {
                            "id": "d1a6db6f-2b6a-4cfe-95c0-6c512a9ab953",
                            "completed": False
                        }
                    ]
                }
            ]
        }
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id,expected_status",
    [
        (uuid.UUID("48fd40b4-3d01-4ad3-998e-2338dbacd371"), 404),
        (uuid.UUID("48fd40b4-3d01-4ad3-998e-2338dbacd376"), 200),
    ]
)
async def test_get(client, session_token_student: str, id: uuid.UUID, expected_status: Literal[404] | Literal[200]):
    response = await client.get(
        f"/works/{id}",
        headers={"Authorization": session_token_student}
    )

    assert response.status_code == expected_status

    if response.status_code == 200:
        print(response.json())
        work = response.json()['work']
        assert work['id'] == "48fd40b4-3d01-4ad3-998e-2338dbacd376"
        assert work['status'] == StatusWork.draft

    if response.status_code == 400:
        assert response.json() == {"detail": "Work not exists"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filters,expected_status,count",
    [
        # ({uuid.UUID("48fd40b4-3d01-4ad3-998e-2338dbacd371")}, 404),
        
        (
            {"student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca"}, 200, 1
        ),
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca"
            }, 200, 1
        ),
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f1ba"
            }, 200, 1
        ),
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f1ba",
                "status_work": StatusWork.draft.value
            }, 200, 1
        ),
        # не существующий status_work
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f1ba",
                "status_work": StatusWork.canceled.value
            }, 200, 0
        ),
        # не существующий subject_id
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6361",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f1ba",
                "status_work": StatusWork.draft.value
            }, 200, 0
        ),
          # не существующий student_id
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de1eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f1ba",
                "status_work": StatusWork.draft.value
            }, 200, 0
        ),
        # не существующий classroom_id
        (
            {
                "subject_id": "6ded87e5-323d-4994-9c9e-38125e5d6362",
                "student_id": "338464b9-b1c8-4f8a-b840-d42597de0eca",
                "classroom_id": "345a10c2-78a4-418c-85ac-b230e9f1f2ba",
                "status_work": StatusWork.draft.value
            }, 200, 0
        ),
        
    ]
)
async def test_get_all(client, session_token_student: str, filters: dict, expected_status, count):
    response = await client.get(
        "/works",
        headers={"Authorization": session_token_student},
        params = {
            **filters
        }
        
    )
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == count



@pytest.mark.asyncio
async def test_update_success(client, session_token_student, work_id, update_data):
    update_data.answers[0].file_url = 'fileeeeeeeeeeeeeee'
    response = await client.put(
        f"/works/{work_id}",
        headers={"Authorization": session_token_student},
        json=update_data.model_dump(mode="json")
    )
    assert response.status_code == 200
    assert response.json()['id'] == str(work_id)
    assert response.json()['answers'][0]["file_url"] == "fileeeeeeeeeeeeeee"


@pytest.mark.asyncio
async def test_update_user_is_teacher(client, session_token_teacher, work_id, update_data):
    update_data.answers[0].file_url = 'fileeeeeeeeeeeeeee'
    response = await client.put(
        f"/works/{work_id}",
        headers={"Authorization": session_token_teacher},
        json=update_data.model_dump(mode="json")
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "User don't have permission to delete this work"}


@pytest.mark.asyncio
async def test_update_id_not_match(client, session_token_student, update_data):
    update_data.answers[0].file_url = 'fileeeeeeeeeeeeeee'
    response = await client.put(
        "/works/{345a10c2-78a4-418c-85ac-b230e9f1f2ba}",
        headers={"Authorization": session_token_student},
        json=update_data.model_dump(mode="json")

    )
    assert response.status_code == 409
    assert response.json() == {'detail': 'Work data id must match with work_id'}

@pytest.mark.asyncio
async def test_update_not_exists(client, session_token_student, update_data):
    update_data.answers[0].file_url = 'fileeeeeeeeeeeeeee'
    work_id = "345a10c2-78a4-418c-85ac-b230e9f1f2ba"
    update_data.id = work_id
    response = await client.put(
        f"/works/{work_id}",
        headers={"Authorization": session_token_student},
        json=update_data.model_dump(mode="json")

    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Work not exists'}


# @pytest.mark.asyncio
# async def test_delete_success(client, work_id, session_token_student):
#     response = await client.delete(
#         f"/works/{work_id}",
#         headers={"Authorization": session_token_student}
#     )
#     print(response.json())
#     assert response.status_code == 200
#     assert response.json() == {"status": "ok"}


# @pytest.mark.asyncio
# async def test_delete_user_is_teacher(client,  session_token_teacher):
#     response = await client.delete(
#         "/works/{id}",
#         headers={"Authorization": session_token_teacher}
#     )

#     assert response.status_code == 403
#     assert response.json() == {"detail": "User don't have permission to delete this work"}


# @pytest.mark.asyncio
# async def test_delete_not_exists(client, session_token_student):
#     work_id = uuid.UUID("345a10c2-78a4-418c-85ac-b230e9f1f2ba")
#     response = await client.delete(
#         f"/works/{work_id}",
#         headers={"Authorization": session_token_student}
#     )

#     assert response.status_code == 404
#     assert response.json() == {"detail": "Work not exists"}
