import typing as t
from datetime import datetime, date, time


class LJSet:
    """
    A 'set' is collection of reps for a given weight
    """

    def __init__(self, weight: int, reps: int) -> None:
        self.weight: int = weight
        self.reps: int = reps


exercise_names: list = [
    "squat",
    "deadlift",
    "bench",
]


class LJExercise:
    """
    An 'set group' is a collection of sets for a given exercise
    """

    def __init__(self, exercise_name: str) -> None:
        if exercise_name in exercise_names:
            self.exercise_type: str = exercise_name
        else:
            raise ValueError(f"Exercise type '{exercise_name}' does not exist.")
        self.sets: list = []

    def add_set(self, set: LJSet) -> None:
        self.sets.append(set)


class LJWorkout:
    """
    A 'session' is a collection of set groups for a given session start and end time
    """

    def __init__(self) -> None:
        self.exercises: list = []

    def start(self, now: datetime) -> None:
        self._date: date = datetime.date(now)
        self._start_time: time = datetime.time(now)
        return self._date, self._start_time

    def end(self, now: datetime) -> None:
        self._end_time: time = datetime.time(now)

    def add_exercise(self, exercise: LJExercise) -> None:
        self.exercises.append(exercise)


class App:
    def add_workout() -> LJWorkout:
        return LJWorkout()

    def add_exercise(workout: LJWorkout, exercise_name: str) -> None:
        exercise: LJExercise = LJExercise(exercise_name)
        workout.add_exercise(exercise)
        return exercise

    def add_set(exercise: LJExercise, weight: int, reps: int) -> None:
        exercise.add_set(LJSet(weight, reps))


def main() -> None:
    app = App()
    workout: LJWorkout = app.add_workout()
    exercise: LJExercise = app.add_exercise(workout, "squat")
    app.add_set(exercise, 100, 10)


if __name__ == "__main__":
    main()
