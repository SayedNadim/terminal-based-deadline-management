import datetime
from typing import List, Optional

import typer
import questionary
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

app = typer.Typer()
Base = declarative_base()


# --- Database Models ---
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    subtasks = relationship(
        "Subtask", back_populates="task", cascade="all, delete-orphan"
    )


class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    date = Column(Date, nullable=False)
    priority = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    task = relationship("Task", back_populates="subtasks")


# --- Database Setup ---
DB_URL = "sqlite:///timeline.db"
engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- Deadline Warning Helper ---
def warn_immediate_deadlines(within_days: int = 1):
    session = SessionLocal()
    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=within_days)
    immediates = (
        session.execute(select(Subtask).where(Subtask.date.between(today, cutoff)))
        .scalars()
        .all()
    )
    if immediates:
        typer.secho(
            f"\n⚠️  You have {len(immediates)} task(s) due within {within_days} day(s):",
            fg=typer.colors.RED,
        )
        for st in immediates:
            typer.secho(
                f"  [{st.id}] {st.task.name}->{st.name} on {st.date}",
                fg=typer.colors.RED,
            )
        typer.echo("")


# --- Interactive Mode ---
@app.callback(invoke_without_command=True)
def interactive(ctx: typer.Context):
    """Launch interactive menu, showing deadline warnings."""
    if ctx.invoked_subcommand is None:
        init_db()  # ensure DB exists
        warn_immediate_deadlines(1)
        while True:
            warn_immediate_deadlines(1)
            action = questionary.select(
                "Select an action:",
                choices=[
                    "Add Task",
                    "List Subtasks",
                    "Remove Subtask",
                    "Update Subtask",
                    "Check Deadlines",
                    "Quit",
                ],
            ).ask()
            if action in (None, "Quit"):
                typer.echo("Exiting.")
                raise typer.Exit()

            if action == "Add Task":
                task = questionary.text("Task name:").ask()
                desc = questionary.text("Task description (optional):").ask() or ""
                count = int(questionary.text("How many subtasks? ").ask() or 0)
                subs, subdescs, dates, prios, weights = [], [], [], [], []
                for i in range(count):
                    subs.append(questionary.text(f"Subtask {i+1} name:").ask())
                    subdescs.append(
                        questionary.text(f"Subtask {i+1} desc:").ask() or ""
                    )
                    dates.append(
                        questionary.text(f"Subtask {i+1} date (YYYY-MM-DD):").ask()
                    )
                    prios.append(
                        questionary.select(
                            f"Subtask {i+1} priority:",
                            choices=["High", "Medium", "Low"],
                        ).ask()
                    )
                    weights.append(
                        int(questionary.text(f"Subtask {i+1} weight (1-10):").ask())
                    )
                ctx.invoke(
                    add,
                    task=task,
                    description=desc,
                    subtask=subs,
                    subdesc=subdescs,
                    date=dates,
                    priority=prios,
                    weight=weights,
                )

            elif action == "List Subtasks":
                days = questionary.text(
                    "Show upcoming in N days (blank for all):"
                ).ask()
                upcoming = int(days) if days else None
                ctx.invoke(list, upcoming=upcoming)

            elif action == "Remove Subtask":
                sid = int(questionary.text("Subtask ID to remove: ").ask())
                ctx.invoke(remove, subtask_id=sid)

            elif action == "Update Subtask":
                sid = int(questionary.text("Subtask ID to update: ").ask())
                prio = questionary.select(
                    "New priority:", choices=["(None)", "High", "Medium", "Low"]
                ).ask()
                prio = None if prio == "(None)" else prio
                w = questionary.text("New weight (1-10, blank for none):").ask()
                weight = int(w) if w else None
                ctx.invoke(update, subtask_id=sid, priority=prio, weight=weight)

            elif action == "Check Deadlines":
                w = int(questionary.text("Within days (default 1):").ask() or 1)
                ctx.invoke(deadlines, within=w)


# --- CLI Commands ---
@app.command()
def init():
    """Initialize the database explicitly."""
    init_db()
    typer.secho("Database initialized at timeline.db", fg=typer.colors.GREEN)


@app.command()
def add(
    task: str = typer.Option(..., prompt=True),
    description: str = typer.Option("", prompt=False),
    subtask: List[str] = typer.Option([], "--subtask", "-s"),
    subdesc: List[str] = typer.Option([], "--subdesc", "-d"),
    date: List[str] = typer.Option([], "--date"),
    priority: List[str] = typer.Option([], "--priority"),
    weight: List[int] = typer.Option([], "--weight"),
):
    """Add a task and its subtasks."""
    session = SessionLocal()
    t = Task(name=task, description=description)
    session.add(t)
    session.flush()
    n = len(subtask)
    if any(len(lst) != n for lst in (subdesc, date, priority, weight)):
        typer.secho("Subtask argument lists must be equal length.", fg=typer.colors.RED)
        raise typer.Exit(1)
    for i in range(n):
        try:
            d = datetime.datetime.strptime(date[i], "%Y-%m-%d").date()
        except ValueError:
            typer.secho(f"Bad date: {date[i]}", fg=typer.colors.RED)
            session.rollback()
            raise typer.Exit(1)
        st = Subtask(
            task_id=t.id,
            name=subtask[i],
            description=subdesc[i],
            date=d,
            priority=priority[i],
            weight=weight[i],
        )
        session.add(st)
    session.commit()
    typer.secho(f"Added '{task}' with {n} subtasks.", fg=typer.colors.GREEN)


@app.command(name="list")
def list(
    upcoming: Optional[int] = typer.Option(None, "--upcoming", "-u"),
):
    """List all (or upcoming) subtasks."""
    session = SessionLocal()
    stmt = select(Subtask).join(Task)
    if upcoming is not None:
        today = datetime.date.today()
        limit = today + datetime.timedelta(days=upcoming)
        stmt = stmt.where(Subtask.date.between(today, limit))
    rows = session.execute(stmt).scalars().all()
    if not rows:
        typer.secho("No subtasks found.", fg=typer.colors.YELLOW)
        raise typer.Exit()
    for st in rows:
        typer.echo(
            f"[{st.id}] {st.task.name} -> {st.name} | {st.date} | {st.priority} | w={st.weight}"
        )


@app.command()
def remove(subtask_id: int):
    """Remove a subtask by its ID."""
    session = SessionLocal()
    st = session.get(Subtask, subtask_id)
    if not st:
        typer.secho(f"ID {subtask_id} not found.", fg=typer.colors.RED)
        raise typer.Exit(1)
    session.delete(st)
    session.commit()
    typer.secho(f"Removed subtask {subtask_id}.", fg=typer.colors.GREEN)


@app.command()
def update(
    subtask_id: int,
    priority: Optional[str] = typer.Option(None, "--priority"),
    weight: Optional[int] = typer.Option(None, "--weight"),
):
    """Update priority/weight of a subtask."""
    session = SessionLocal()
    st = session.get(Subtask, subtask_id)
    if not st:
        typer.secho(f"ID {subtask_id} not found.", fg=typer.colors.RED)
        raise typer.Exit(1)
    if priority:
        st.priority = priority
    if weight:
        st.weight = weight
    session.commit()
    typer.secho(f"Updated subtask {subtask_id}.", fg=typer.colors.GREEN)


@app.command()
def deadlines(within: int = typer.Option(1, "--within", "-w")):
    """Show immediate and nearest deadlines."""
    session = SessionLocal()
    today = datetime.date.today()
    im_end = today + datetime.timedelta(days=within)
    immediate = (
        session.execute(select(Subtask).where(Subtask.date.between(today, im_end)))
        .scalars()
        .all()
    )
    if immediate:
        typer.secho("Immediate deadlines:", fg=typer.colors.RED)
        for st in immediate:
            typer.echo(f"  {st.task.name}->{st.name} due {st.date}")
    else:
        next_one = (
            session.execute(
                select(Subtask)
                .where(Subtask.date > today)
                .order_by(Subtask.date)
                .limit(1)
            )
            .scalars()
            .first()
        )
        if next_one:
            typer.secho("Nearest deadline:", fg=typer.colors.BLUE)
            typer.echo(f"  {next_one.task.name}->{next_one.name} due {next_one.date}")
        else:
            typer.secho("No upcoming deadlines.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
