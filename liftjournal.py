import typing as t
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey, StaticPool, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    relationship,
    mapped_column,
    Session,
)
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class LJWorkout(Base):
    """
    SQLAlchemy model based on 'LJWorkout'
    """

    __tablename__ = "lj_workout"
    id: Mapped[int] = mapped_column(primary_key=True)
    exercises: Mapped[t.List["LJExercise"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJWorkout(id={self.id})>"


EXERCISE_NAMES: list = [
    "squat",
    "deadlift",
    "bench",
]


class LJExercise(Base):
    """
    SQLAlchemy model based on 'LJExercise'
    """

    __tablename__ = "lj_exercise"
    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("lj_workout.id"))
    name: Mapped[str] = mapped_column()
    sets: Mapped[t.List["LJSet"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJSet(id={self.id}, workout_id={self.workout_id}, name={self.name})>"


class LJSet(Base):
    """
    SQLAlchemy model based on 'LJSet'
    """

    __tablename__ = "lj_set"
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("lj_exercise.id"))
    weight: Mapped[int]
    reps: Mapped[int]

    def __repr__(self) -> str:
        return f"<LJSet(id={self.id}, exercise_id={self.exercise_id}, weight={self.weight}, reps={self.reps})>"


def main() -> None:
    engine = create_engine(
        "sqlite:////mnt/c/Users/hooty/test.db", echo=True, poolclass=StaticPool
    )

    Base.metadata.create_all(engine)

    with Session(engine) as s:
        workout1 = LJWorkout()
        print(workout1.exercises)
        exercise1 = LJExercise(name="squat")
        exercise1.sets.extend(
            [
                LJSet(weight=135, reps=5),
                LJSet(weight=185, reps=5),
                LJSet(weight=225, reps=5),
            ]
        )
        exercise2 = LJExercise(name="bench")
        exercise2.sets.extend([LJSet(weight=135, reps=5), LJSet(weight=185, reps=5)])
        workout1.exercises.extend([exercise1, exercise2])
        print(workout1.exercises)

        s.add(workout1)
        s.commit()

        for row in s.execute(
            select(LJSet)
            .select_from(LJExercise)
            .join(LJSet)
            .where(LJExercise.name == "squat")
        ):
            print(row[0])


if __name__ == "__main__":
    main()
