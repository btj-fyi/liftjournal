import unittest
from liftjournal import LJWorkout, LJSetGroup, Excercise
from datetime import datetime, timedelta


class TestLJWorkout(unittest.TestCase):
    def setUp(self) -> None:
        self.now: datetime = datetime.now()
        self.workout: LJWorkout = LJWorkout()

    def test_start_workout(self) -> None:
        self.workout.start(self.now)
        self.assertEqual(self.workout._date, datetime.date(self.now))
        self.assertEqual(self.workout._start_time, datetime.time(self.now))

    def test_end_workout(self) -> None:
        later: datetime = self.now + timedelta(hours=1)
        self.workout.end(later)
        self.assertEqual(self.workout._end_time, datetime.time(later))

    def test_add_set_group(self) -> None:
        set_group: LJSetGroup = LJSetGroup(Excercise("squat"))
        self.workout.add_set_group(set_group)
        self.assertEqual(self.workout.set_groups, [set_group])


if __name__ == "main":
    unittest.main()
