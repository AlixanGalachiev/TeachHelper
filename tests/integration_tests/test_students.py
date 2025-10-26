import pytest

from app.config.config_app import settings



@pytest.mark.asyncio(loop_scope="session")
async def test_get_link(client, session_token_teacher):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": session_token_teacher}
        )
    user_db = response.json()

    response = await client.get(
        "/teachers/invite_link",
        headers={"Authorization": session_token_teacher}
    )

    assert response.status_code == 200
    assert response.json() == {"link": f"{settings.FRONT_URL}/t/{user_db["id"]}"}

@pytest.mark.asyncio(loop_scope="session")
async def test_get_all(client, session_token_teacher):
    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "students" in data
    assert "classrooms" in data



@pytest.mark.asyncio(loop_scope="session")
async def test_get_performans_data(client, session_token_teacher):
    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )
    student = response.json()['students'][0]

    response = await client.get(
        f"/students/{student['id']}",
        headers={"Authorization": session_token_teacher}
    )
    data = response.json()

    assert "student_id" in data
    assert "student_name" in data
    assert "verificated_works_count" in data
    assert "avg_score" in data
    assert "works" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_move_to_class(client, session_token_teacher):
    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )    
    student = response.json()['students'][0]
    classroom = response.json()['classrooms'][0]

    response = await client.patch(
        f"/students/{student['id']}/move_to_class",
        headers={"Authorization": session_token_teacher},
        params={
            "classroom_id": classroom['id']
        }
    )

    assert response.status_code == 200

    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )    
    student_new = response.json()['students'][0]

    assert student_new["id"] == student["id"]
    assert student_new["classroom_id"] == classroom["id"]

    

@pytest.mark.asyncio(loop_scope="session")
async def test_remove_from_class(client, session_token_teacher):
    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )
    student = response.json()['students'][0]
    classroom = response.json()['classrooms'][0]
    assert student["classroom_id"] == classroom["id"]
    

    response = await client.patch(
        f"/students/{student['id']}/remove_from_class",
        headers={"Authorization": session_token_teacher},
        params={
            "classroom_id": classroom['id']
        }
    )
    assert response.status_code == 200

    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )    
    student_new = response.json()['students'][0]

    assert student_new["id"] == student["id"]
    assert student_new["classroom_id"] is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete(client, session_token_teacher):
    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )
    students = response.json()['students']
    assert len(students) > 0

    response = await client.delete(
        f"/students/{students[0]['id']}",
        headers={"Authorization": session_token_teacher}
    )
    assert response.status_code == 200

    response = await client.get(
        "/students",
        headers={"Authorization": session_token_teacher}
    )
    students = response.json()['students']
    assert len(students) == 0
    