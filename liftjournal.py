from datetime import datetime
import typing as t
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Integer,
    func,
    ForeignKey,
    StaticPool,
    select,
    create_engine,
)
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class LJWorkout(db.Model):
    """
    SQLAlchemy model based on 'LJWorkout'
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(
        Date, default=datetime.now().date(), nullable=False
    )
    updated_at: Mapped[float] = mapped_column(
        Float, default=datetime.now().timestamp(), onupdate=datetime.now().timestamp()
    )
    exercises: Mapped[t.List["LJExercise"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJWorkout(id={self.id})>"


EXERCISE_NAMES: list = [
    "Squat",
    "Deadlift",
    "Bench",
]


class LJExercise(db.Model):
    """
    SQLAlchemy model based on 'LJExercise'
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("lj_workout.id"))
    updated_at: Mapped[float] = mapped_column(
        Float, default=datetime.now().timestamp(), onupdate=datetime.now().timestamp()
    )
    name: Mapped[str] = mapped_column(nullable=False)
    sets: Mapped[t.List["LJSet"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJExercise(id={self.id}, workout_id={self.workout_id}, name={self.name})>"


class LJSet(db.Model):
    """
    SQLAlchemy model based on 'LJSet'
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("lj_exercise.id"))
    updated_at: Mapped[float] = mapped_column(
        Float, default=datetime.now().timestamp(), onupdate=datetime.now().timestamp()
    )
    weight: Mapped[int] = mapped_column(nullable=False)
    reps: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<LJSet(id={self.id}, exercise_id={self.exercise_id}, weight={self.weight}, reps={self.reps})>"


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////mnt/c/Users/hooty/liftjournal.db"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/home")
def home():
    return render_template("home.html", workouts=None, workout=None)


@app.route("/mystats")
def mystats():
    return render_template("mystats.html")


@app.route("/myworkouts")
def myworkouts():
    workouts = db.session.execute(db.select(LJWorkout)).scalars()
    return render_template("myworkouts.html", workouts=workouts)


@app.route("/new_workout", methods=["POST"])
def new_workout():
    new_workout = LJWorkout()
    db.session.add(new_workout)
    db.session.commit()
    app.logger.debug(new_workout)
    return render_template(
        "new_exercise.html",
        workout_id=new_workout.id,
        exercise_names=EXERCISE_NAMES,
        exercise_name=None,
    )


@app.route("/new_exercise", methods=["POST"])
def new_exercise():
    # if not exercise select and reload
    workout_id: str = request.args.get("workout_id")
    app.logger.debug(workout_id)
    exercise_name: str = request.form.get("exercise_name")
    if exercise_name:
        app.logger.debug(exercise_name)
        new_exercise = LJExercise(workout_id=workout_id, name=exercise_name)
        db.session.add(new_exercise)
        db.session.commit()
        sets = db.session.execute(
            db.select(LJSet).where(LJSet.exercise_id == new_exercise.id)
        ).scalars()
        return render_template(
            "new_exercise.html",
            workout_id=workout_id,
            exercise=new_exercise,
            sets=sets,
        )

    return render_template(
        "new_exercise.html",
        workout_id=workout_id,
        exercise_name=None,
        exercise=None,
        sets=[],
        exercise_names=EXERCISE_NAMES,
    )


app.route("/select_new_exercise", methods=["POST"])


def select_new_exercise():
    pass


@app.route("/new_set", methods=["POST"])
def new_set():
    workout_id: str = request.args.get("workout_id")
    app.logger.debug("workout_id =", workout_id)

    exercise_id = request.args.get("exercise_id")
    app.logger.debug("exercise_id =", exercise_id)

    reps = request.form.get("reps")
    weight = request.form.get("weight")

    new_set = LJSet(exercise_id=exercise_id, reps=reps, weight=weight)
    db.session.add(new_set)
    db.session.commit()

    exercise = db.session.execute(
        db.select(LJExercise).where(LJExercise.id == exercise_id)
    ).scalar()

    sets = db.session.execute(
        db.select(LJSet).where(LJSet.exercise_id == exercise_id)
    ).scalars()

    return render_template(
        "new_exercise.html", workout_id=workout_id, exercise=exercise, sets=sets
    )


@app.route("/workout", methods=["POST"])
def workout():
    workout_id: str = request.args.get("workout_id")
    app.logger.debug(workout_id)
    workout = db.session.execute(
        db.select(LJWorkout).where(LJWorkout.id == workout_id)
    ).scalar()
    return render_template("workout.html", workout=workout)


@app.route("/load_workouts", methods=["POST"])
def get_workouts():
    workouts = db.session.execute(db.select(LJWorkout)).scalars()
    return render_template("home.html", workouts=workouts)


@app.route("/load_workout", methods=["POST"])
def get_workout():
    workout_id: str = request.form["workout_id"]
    app.logger.debug(workout_id)
    workouts = db.session.execute(db.select(LJWorkout)).scalars()
    workout = db.session.execute(
        db.select(LJWorkout).where(LJWorkout.id == workout_id)
    ).scalar()
    return render_template("home.html", workouts=workouts, workout=workout)


@app.route("/workouts/create", methods=["GET", "POST"])
def workout_create():
    if request.method == "POST":
        workout = LJWorkout()
        db.session.add(workout)
        db.session.commit()
        return redirect(url_for("workout_detail", id=workout.id))
    return render_template("workout/create.html")


@app.route("/workout/<int:id>")
def workout_detail(id):
    workout: LJWorkout = db.get_or_404(LJWorkout, id)
    return render_template("workout/detail.html", workout=workout)


@app.route("/workout/<int:id>/delete")
def workout_delete(id):
    workout = db.get_or_404(LJWorkout, id)
    if request.method == "POST":
        db.session.delete(workout)
        db.session.commit()
        return redirect(url_for("workout_list"))

    return render_template("workout/delete.html", workout=workout)
