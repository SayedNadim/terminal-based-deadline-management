from dotenv import load_dotenv
import os
import datetime
from datetime import date, timedelta
from typing import List, Optional

import typer
import questionary
from supabase import create_client

# Load environment
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

# Initialize Supabase client
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

app = typer.Typer()


# --- Deadline Warning Helper ---
def warn_immediate_deadlines(within_days: int = 1):
    today = date.today().isoformat()
    cutoff = (date.today() + timedelta(days=within_days)).isoformat()
    resp = (
        sb.table("subtasks")
        .select("id,name,date,priority,weight,task_id,tasks(name)")
        .gte("date", today)
        .lte("date", cutoff)
        .execute()
    )
    immediates = resp.data or []
    if immediates:
        typer.secho(
            f"\n⚠️  You have {len(immediates)} subtask(s) due within {within_days} day(s):",
            fg=typer.colors.RED,
        )
        for st in immediates:
            task_name = st.get("tasks", {}).get("name", "<unknown>")
            typer.secho(
                f"  [{st['id']}] {task_name}->{st['name']} on {st['date']}",
                fg=typer.colors.RED,
            )
        typer.echo("")


# --- Interactive Mode ---
@app.callback(invoke_without_command=True)
def interactive(ctx: typer.Context):
    """Interactive menu with deadline warnings."""
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
            names, descriptions, dates, priorities, weights = [], [], [], [], []
            for i in range(count):
                names.append(questionary.text(f"Subtask {i+1} name:").ask())
                descriptions.append(
                    questionary.text(f"Subtask {i+1} desc:").ask() or ""
                )
                dates.append(
                    questionary.text(f"Subtask {i+1} date (YYYY-MM-DD):").ask()
                )
                priorities.append(
                    questionary.select(
                        f"Subtask {i+1} priority:", choices=["High", "Medium", "Low"]
                    ).ask()
                )
                weights.append(
                    int(questionary.text(f"Subtask {i+1} weight (1-10):").ask())
                )
            ctx.invoke(
                add,
                task=task,
                description=desc,
                subtask=names,
                subdesc=descriptions,
                date=dates,
                priority=priorities,
                weight=weights,
            )

        elif action == "List Subtasks":
            days = questionary.text("Show upcoming in N days (blank for all):").ask()
            upcoming = int(days) if days else None
            ctx.invoke(list_subtasks, upcoming=upcoming)

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
def add(
    task: str = typer.Option(..., prompt=True),
    description: str = typer.Option("", prompt=False),
    subtask: List[str] = typer.Option([], "--subtask", "-s"),
    subdesc: List[str] = typer.Option([], "--subdesc", "-d"),
    date: List[str] = typer.Option([], "--date"),
    priority: List[str] = typer.Option([], "--priority"),
    weight: List[int] = typer.Option([], "--weight"),
):
    """Add a task and its subtasks via Supabase."""
    # Insert main task
    resp = (
        sb.table("tasks")
        .insert(
            {
                "name": task,
                "description": description,
            }
        )
        .execute()
    )
    task_id = resp.data[0]["id"]
    # Prepare subtasks
    n = len(subtask)
    if any(len(lst) != n for lst in (subdesc, date, priority, weight)):
        typer.secho("Subtask argument lists must match lengths.", fg=typer.colors.RED)
        raise typer.Exit(1)
    records = []
    for i in range(n):
        # Validate date format
        try:
            datetime.datetime.strptime(date[i], "%Y-%m-%d")
        except ValueError:
            typer.secho(f"Invalid date: {date[i]}", fg=typer.colors.RED)
            raise typer.Exit(1)
        records.append(
            {
                "task_id": task_id,
                "name": subtask[i],
                "description": subdesc[i],
                "date": date[i],
                "priority": priority[i],
                "weight": weight[i],
            }
        )
    if records:
        sb.table("subtasks").insert(records).execute()
    typer.secho(f"Added '{task}' with {n} subtasks.", fg=typer.colors.GREEN)


@app.command(name="list")
def list_subtasks(
    upcoming: Optional[int] = typer.Option(None, "--upcoming", "-u"),
):
    """List subtasks (via Supabase)."""
    query = sb.table("subtasks").select("id,name,date,priority,weight,tasks(name)")
    if upcoming is not None:
        today = date.today().isoformat()
        cutoff = (date.today() + timedelta(days=upcoming)).isoformat()
        query = query.gte("date", today).lte("date", cutoff)
    rows = query.execute().data or []
    if not rows:
        typer.secho("No subtasks found.", fg=typer.colors.YELLOW)
        raise typer.Exit()
    for st in rows:
        task_name = st.get("tasks", {}).get("name", "<unknown>")
        typer.echo(
            f"[{st['id']}] {task_name} -> {st['name']} | {st['date']} | {st['priority']} | w={st['weight']}"
        )


@app.command()
def remove(subtask_id: int):
    """Remove a subtask by ID via Supabase."""
    resp = sb.table("subtasks").delete().eq("id", subtask_id).execute()
    if resp.error:
        typer.secho(
            f"Error removing ID {subtask_id}: {resp.error}", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    typer.secho(f"Removed subtask {subtask_id}.", fg=typer.colors.GREEN)


@app.command()
def update(
    subtask_id: int,
    priority: Optional[str] = typer.Option(None, "--priority"),
    weight: Optional[int] = typer.Option(None, "--weight"),
):
    """Update priority/weight of a subtask via Supabase."""
    data = {}
    if priority:
        data["priority"] = priority
    if weight:
        data["weight"] = weight
    if not data:
        typer.echo("Nothing to update.")
        raise typer.Exit()
    resp = sb.table("subtasks").update(data).eq("id", subtask_id).execute()
    if resp.error:
        typer.secho(
            f"Error updating ID {subtask_id}: {resp.error}", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    typer.secho(f"Updated subtask {subtask_id}.", fg=typer.colors.GREEN)


@app.command()
def deadlines(within: int = typer.Option(1, "--within", "-w")):
    """Show immediate and next deadlines via Supabase."""
    today = date.today().isoformat()
    cutoff = (date.today() + timedelta(days=within)).isoformat()
    imm = (
        sb.table("subtasks")
        .select("id,name,date,tasks(name)")
        .gte("date", today)
        .lte("date", cutoff)
        .execute()
        .data
    ) or []
    if imm:
        typer.secho("Immediate deadlines:", fg=typer.colors.RED)
        for st in imm:
            task_name = st.get("tasks", {}).get("name", "<unknown>")
            typer.echo(f"  {task_name}->{st['name']} due {st['date']}")
    else:
        nxt = (
            sb.table("subtasks")
            .select("id,name,date,tasks(name)")
            .gt("date", today)
            .order("date", count="asc")
            .limit(1)
            .execute()
            .data
        )
        if nxt:
            st = nxt[0]
            task_name = st.get("tasks", {}).get("name", "<unknown>")
            typer.secho("Nearest deadline:", fg=typer.colors.BLUE)
            typer.echo(f"  {task_name}->{st['name']} due {st['date']}")
        else:
            typer.secho("No upcoming deadlines.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
