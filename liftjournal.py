from datetime import datetime
import typing as t
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)
from sqlalchemy import Date, ForeignKey, StaticPool, select, create_engine
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
    date: Mapped[datetime.date] = mapped_column(Date, default=(datetime.now()).date())
    exercises: Mapped[t.List["LJExercise"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJWorkout(id={self.id})>"


EXERCISE_NAMES: list = [
    "squat",
    "deadlift",
    "bench",
]


class LJExercise(db.Model):
    """
    SQLAlchemy model based on 'LJExercise'
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey("lj_workout.id"))
    name: Mapped[str] = mapped_column()
    sets: Mapped[t.List["LJSet"]] = relationship()

    def __repr__(self) -> str:
        return f"<LJExercise(id={self.id}, workout_id={self.workout_id}, name={self.name})>"


class LJSet(db.Model):
    """
    SQLAlchemy model based on 'LJSet'
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("lj_exercise.id"))
    weight: Mapped[int]
    reps: Mapped[int]

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


@app.route("/new_exercise")
def new_exercise():
    return render_template("new_exercise.html")


@app.route("/new_workout", methods=["POST"])
def new_workout():
    return render_template("new_workout.html")


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
