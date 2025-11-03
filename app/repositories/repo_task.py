from time import time
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.model_tasks import ACriterions, Answers, Exercises, Works, Tasks
from app.schemas.schema_tasks import SchemaTask

class RepoTasks():
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get(self, id: uuid.UUID):
        stmt = (
            select(Tasks)
            .where(Tasks.id == id)
            .options(
                selectinload(Tasks.exercises)
                .selectinload(Exercises.criterions)
            )
        )
        response = await self.session.execute(stmt)
        return response.scalars().first()

    async def create_works(
        self,
        task: SchemaTask,
        students_ids: list[uuid.UUID]
    ):
        submissions = [
            Works(task_id=task.id, student_id=student_id) 
            for student_id in students_ids
        ]
        self.session.add_all(submissions)
        await self.session.flush()


        all_answers = []
        all_a_criterions = []

        for submission in submissions:
            # Проверяем, что task.exercises существует и является списком (из-за relationship)
            if hasattr(task, 'exercises') and task.exercises: 
                for exercise in task.exercises:
                    # Создаем Answer
                    answer = Answers(submission_id=submission.id, exercise_id=exercise.id)
                    all_answers.append(answer)

                    # Создаем ACriterions для этого Answer
                    if hasattr(exercise, 'criterions') and exercise.criterions:
                        a_criterions = [
                            ACriterions(
                                answer_id=answer.id, 
                                exercise_criterion_id=e_criterion.id
                            ) 
                            for e_criterion in exercise.criterions
                        ]
                        all_a_criterions.extend(a_criterions)

        self.session.add_all(all_answers)
        self.session.add_all(all_a_criterions)
