import uuid
from sqlalchemy import case, func, select

from app.models.model_classroom import Classrooms
from app.models.model_tasks import ECriterions, Tasks, Subjects, Exercises
from app.models.model_users import RoleUser, Users, teachers_students
from app.models.model_works import ACriterions, StatusWork, Works, Answers
from app.schemas.schema_work import WorkAllFilters
from app.utils.logger import logger

class RepoWorks():
    def __init__(self, session):
        self.session = session

    async def get_all(self, filters: WorkAllFilters, user: Users):
        # 1. Определяем алиасы для удобства
        # Используем алиас для связей, которые будут использоваться в агрегации
        
        # Набранный балл: сумма баллов тех критериев ECriterions, где ACriterions.completed == True
        # Используем CASE для условного суммирования
        current_score_expr = func.sum(
            case(
                (ACriterions.completed == True, ECriterions.score),
                else_=0
            )
        )
        
        # 3. Базовый запрос с JOINs
        stmt = (
            select(
                Works.id.label("id"),
                func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
                Tasks.name.label("task_name"),
                current_score_expr.label("score"),
                func.sum(ECriterions.score).label("max_score"),
                Works.status.label("status_work")
            )
            .select_from(Works)
            .join(Users, Works.student_id == Users.id) 
            .join(Tasks, Works.task_id == Tasks.id)
            .join(Answers, Works.id == Answers.work_id) 
            .join(Exercises, Answers.exercise_id == Exercises.id)
            .join(ECriterions, Exercises.id == ECriterions.exercise_id)
            .join(ACriterions, (Answers.id == ACriterions.answer_id) & (ECriterions.id == ACriterions.e_criterion_id))
            .join(Subjects, Tasks.subject_id == Subjects.id, isouter=True)
        )

        # 4. Группировка
        # Группируем по уникальным полям работы, чтобы агрегировать баллы (SUM)
        stmt = stmt.group_by(
            Works.id,
            Users.first_name,
            Users.last_name,
            Tasks.name,
            Works.status
        )

        # 5. Фильтрация по роли пользователя
        if user.role == RoleUser.student:
            stmt = stmt.where(Works.student_id == user.id)
        elif user.role == RoleUser.teacher:
            stmt = stmt.where(Tasks.teacher_id == user.id)
            stmt = stmt.join(teachers_students, user.id == teachers_students.c.teacher_id )

            if filters.classroom_id:
                stmt = stmt.join(Classrooms, teachers_students.c.classroom_id == Classrooms.id)
                stmt = stmt.where(Classrooms.id == filters.classroom_id)

            if filters.student_id:
                stmt = stmt.where(Works.student_id == filters.student_id)

        # 6. Фильтрация по параметрам WorkAllFilters
        if filters.subject_id:
            stmt = stmt.where(Tasks.subject_id == filters.subject_id)


        if filters.status_work:
            stmt = stmt.where(Works.status == filters.status_work)


        # 7. Выполнение запроса и расчет процента
        result = await self.session.execute(stmt)
        # Получаем список кортежей (id, student_name, task_name, score, max_score, status_work)
        return result.all()


    async def get_all_student(
        self,
        user: Users,
        subject_id: uuid.UUID|None = None,
        status_work: StatusWork| None = None,
    ):
        current_score_expr = func.sum(
            case(
                (ACriterions.completed == True, ECriterions.score),
                else_=0
            )
        )

        stmt = (
            select(
                Works.id.label("id"),
                func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
                Tasks.name.label("task_name"),
                current_score_expr.label("score"),
                func.sum(ECriterions.score).label("max_score"),
                Works.status.label("status_work")
            )
            .select_from(Works)
            .join(Users, Works.student_id == Users.id) 
            .join(Tasks, Works.task_id == Tasks.id)
            .join(Answers, Works.id == Answers.work_id) 
            .join(Exercises, Answers.exercise_id == Exercises.id)
            .join(ECriterions, Exercises.id == ECriterions.exercise_id)
            .join(ACriterions, (Answers.id == ACriterions.answer_id) & (ECriterions.id == ACriterions.e_criterion_id))
            .join(Subjects, Tasks.subject_id == Subjects.id, isouter=True)
        )

        stmt = stmt.group_by(
            Works.id,
            Users.first_name,
            Users.last_name,
            Tasks.name,
            Works.status
        )

        # 5. Фильтрация по роли пользователя

        stmt = stmt.where(Works.student_id == user.id)

        # 6. Фильтрация по параметрам WorkAllFilters
        if subject_id:
            stmt = stmt.where(Tasks.subject_id == subject_id)


        if status_work:
            stmt = stmt.where(Works.status == status_work)


        # 7. Выполнение запроса и расчет процента
        result = await self.session.execute(stmt)
        # Получаем список кортежей (id, student_name, task_name, score, max_score, status_work)
        return result.all()

    async def get_all_teacher(
        self,
        user: Users,
        students_ids: list[uuid.UUID]|None = None,
        subject_id: uuid.UUID|None = None,
        status_work: StatusWork| None = None,
    ):
        current_score_expr = func.sum(
            case(
                (ACriterions.completed == True, ECriterions.score),
                else_=0
            )
        )


        stmt = (
            select(
                Works.id.label("id"),
                func.concat(Users.first_name, " ", Users.last_name).label("student_name"),
                Tasks.name.label("task_name"),
                current_score_expr.label("score"),
                func.sum(ECriterions.score).label("max_score"),
                Works.status.label("status_work")
            )
            .select_from(Tasks)
            .where(Tasks.teacher_id == user.id)
        )

        if subject_id is not None:
            stmt = stmt.join(Subjects, Tasks.subject_id == Subjects.id)
            stmt = stmt.where(Subjects.id == subject_id)

        stmt = stmt.join(Works, Tasks.id == Works.task_id)
        if status_work is not None :
            stmt = stmt.where(Works.status == status_work)

        if students_ids is not None:
            stmt = stmt.where(Works.student_id.in_(students_ids))
        
        stmt = (
            stmt.join(Users, Works.student_id == Users.id) 
            .join(Answers, Works.id == Answers.work_id) 
            .join(Exercises, Answers.exercise_id == Exercises.id)
            .join(ECriterions, Exercises.id == ECriterions.exercise_id)
            .join(ACriterions, (Answers.id == ACriterions.answer_id) & (ECriterions.id == ACriterions.e_criterion_id))
        )


        stmt = stmt.group_by(
            Works.id,
            Users.first_name,
            Users.last_name,
            Tasks.name,
            Works.status
        )

        result = await self.session.execute(stmt)
        # Получаем список кортежей (id, student_name, task_name, score, max_score, status_work)
        return result.all()