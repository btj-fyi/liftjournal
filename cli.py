import click
import os
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session
from liftjournal import LJWorkout, Base
import logging

logger = logging.getLogger("test")

engine: Engine = create_engine("sqlite:////mnt/c/Users/hooty/liftjournal.db", echo=True)


@click.group()
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True)
def cli(verbose: bool) -> None:
    logger.setLevel(logging.INFO)
    if verbose:
        logger.setLevel(logging.DEBUG)
    logger.info(f"[DEBUG MODE]: {verbose}")


@cli.command()
def reinitialize_db() -> None:
    if os.path.exists("/mnt/c/Users/hooty/liftjournal.db"):
        os.remove("/mnt/c/Users/hooty/liftjournal.db")

    Base.metadata.create_all(engine)


@cli.command()
def add_workout() -> None:
    with Session(engine) as session:
        workout = LJWorkout()
        click.echo("Adding workout...")
        session.add(workout)
        session.commit()
        logger.debug("test")
        click.echo(f"Added workout: {workout}")


@cli.command()
def get_workouts() -> None:
    with Session(engine) as session:
        workouts = session.execute(select(LJWorkout)).all()
        click.echo("Fidning workouts...")
        click.echo("Found workouts:")
        for workout in workouts:
            click.echo(workout)


@cli.command()
def add_exercise() -> None:
    pass


@cli.command()
def add_set() -> None:
    pass


if __name__ == "__main__":
    cli()
