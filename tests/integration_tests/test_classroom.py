import uuid
import pytest

from app.schemas.schema_classroom import SchemaClassroom


@pytest.fixture(scope="module")
def classroom():
    return SchemaClassroom(
        id=uuid.uuid4,
        name="lal"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_classrooms_create_classroom(client, session_token_teacher):
    response = await client.post(
        '/classrooms',
        headers={"Authorization": session_token_teacher},
        params={"name":"lal"}
    )

    data = response.json()

    assert response.status_code == 200
    assert "id" in data
    assert data["name"] == "lal"


@pytest.mark.asyncio(loop_scope="session")
async def test_classrooms_get_all(client, session_token_teacher):
    response = await client.get(
        '/classrooms',
        headers={"Authorization": session_token_teacher},
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio(loop_scope="session")
async def test_classrooms_update(client, session_token_teacher, ):
    response = await client.get(
        '/classrooms',
        headers={"Authorization": session_token_teacher},
    )
    classroom = response.json()[0]

    response = await client.patch(
        f"/classrooms/{classroom["id"]}",
        headers={"Authorization": session_token_teacher},
        params={"name": "gegeree"}
        )

    assert response.status_code == 200
    assert response.json() == {'message': 'success'}

@pytest.mark.asyncio(loop_scope="session")
async def test_classrooms_delete(client, session_token_teacher, ):
    response = await client.get(
        '/classrooms',
        headers={"Authorization": session_token_teacher},
    )

    classroom = response.json()[0]
    response = await client.delete(
        f"/classrooms/{classroom["id"]}",
        headers={"Authorization": session_token_teacher},
        )

    assert response.status_code == 200
    assert response.json() == {'message': 'success'}
