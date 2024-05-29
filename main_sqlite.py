import datetime
import sqlite3
import time

import matplotlib.pyplot as plt
import pandas as pd

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('timeline.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    task TEXT NOT NULL,
    task_description TEXT,
    subtask TEXT,
    subtask_description TEXT,
    priority TEXT,
    weight INTEGER
)
''')
conn.commit()

# Function to add date
def add_date():
    date = input("Enter date (YYYY-MM-DD): ")
    if len(date) > 10:
        # String has time information
        datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    else:
        # String has no time information
        datetime.datetime.strptime(date, "%Y-%m-%d")
    date = date[:10]
    date = date.replace("-0", "-")  # Remove leading zeros from single-digit dates
    return date

def add_tasks_subtasks_weights_descriptions():
    task = input("Enter task: ")
    task_description = input("Enter task description (optional): ")

    subtasks = input("Enter subtasks (if any, separated by comma): ").split(',')
    subtask_descriptions = []
    subtask_dates = []
    subtask_priorities = []
    subtask_weights = []

    for subtask in subtasks:
        subtask_description = input(f"Enter description for '{subtask}' (optional): ")
        subtask_date = add_date()
        
        while True:  # Loop until valid priority is entered
            subtask_priority = input(f"Enter priority for '{subtask}' (High, Medium, Low): ")
            if subtask_priority in ["High", "Medium", "Low"]:
                break
            print("Invalid priority. Please enter High, Medium, or Low.")

        while True:  # Loop until valid weight is entered
            try:
                subtask_weight = int(input(f"Enter weight for '{subtask}' (1-10): "))
                if not 1 <= subtask_weight <= 10:
                    raise ValueError
                break
            except ValueError:
                print("Invalid weight. Please enter an integer between 1 and 10.")

        subtask_descriptions.append(subtask_description)
        subtask_dates.append(subtask_date)
        subtask_priorities.append(subtask_priority)
        subtask_weights.append(subtask_weight)

    return task, task_description, subtasks, subtask_descriptions, subtask_dates, subtask_priorities, subtask_weights

# Function to add task
def add_task():
    print("\n")
    print("-" * 20)
    print("Adding Task:")

    while True:  # Enclosing loop for retrying all inputs if needed
        try:
            task, task_description, subtasks, subtask_descriptions, subtask_dates, subtask_priorities, subtask_weights = add_tasks_subtasks_weights_descriptions()
            break  # Exit the enclosing while loop if all inputs are valid

        except ValueError:
            print("Invalid input. Please try again.")

    new_rows = []
    for i, subtask in enumerate(subtasks):
        new_row = (subtask_dates[i], task, task_description, subtask, subtask_descriptions[i], subtask_priorities[i], subtask_weights[i])
        new_rows.append(new_row)

    c.executemany('INSERT INTO tasks (date, task, task_description, subtask, subtask_description, priority, weight) VALUES (?, ?, ?, ?, ?, ?, ?)', new_rows)
    conn.commit()
    print("\n")
    print("-" * 20)
    print("Task added successfully.")
    print("-" * 20)
    print("\n")

# Function to view existing timeline
def view_timeline():
    df = pd.read_sql_query('SELECT * FROM tasks', conn)
    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no tasks currently in the timeline.")
        print("-" * 20)
        print("\n")
        
    else:
        print("\nExisting Timeline:")
        print(df)

def remove_task():
    print("\nRemoving task:")
    df = pd.read_sql_query('SELECT * FROM tasks', conn)

    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no tasks currently in the timeline.")
        print("-" * 20)
        print("\n")
        
        return  # Exit the function if empty

    # Print the list of tasks with indices (same as before)
    print("Index\tTask")
    print("-------\t-------")
    for index, row in df.iterrows():
        print(f"{index}\t{row['task']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the task you want to remove (put -1 to go back to menu): "))
            if index in df.index:  # Check if index is valid
                break
            elif index == -1:
                print("Exiting to the main menu...")
                return                
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Remove task and save data (same as before)
    task_id = df.loc[index, 'id']
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    print("Task removed successfully.")
    print("-" * 20)
    print("\n")

# Function to change task priority
def change_task_priority():
    print("\nChanging task Priority:")
    df = pd.read_sql_query('SELECT * FROM tasks', conn)

    if df.empty:  # Check if dataframe is empty
        print("There are no tasks currently in the timeline.")
        return  # Exit the function if empty
    else:
        # Print the list of tasks with indices (same as previous)
        print("Index\tTask\tPriority\tWeights")
        print("-------\t-------")
        for index, row in df.iterrows():
            print(f"{index}\t{row['task']}\t{row['priority']}\t{row['weight']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the task you want to change weight for: "))
            if index in df.index:  # Check if index is valid
                break
            elif index == -1:
                return 
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Get user input for priority
    while True:
        try:
            priority = input("Enter the new priority of the task (High, Medium, Low): ")
            if priority in ["High", "Medium", "Low"]:
                break
            elif priority == -1:
                print("Exiting to the main menu...")
                return 
            else:
                print("Invalid priority. Please enter from High, Medium or Low.")
        except ValueError:
            print("Invalid input. Please enter from High, Medium or Low.")

    # Get user input for weight
    while True:
        try:
            weight = int(input("Enter the new weight of the task (1-10): "))
            if 1 <= weight <= 10:
                break
            elif index == -1:
                print("Exiting to the main menu...")
                return 
            else:
                print("Invalid weight. Please enter a value between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Change weight and save data
    task_id = df.loc[index, 'id']
    c.execute('UPDATE tasks SET priority = ?, weight = ? WHERE id = ?', (priority, weight, task_id))
    conn.commit()
    print("Task priority changed successfully.")

# Function to check for immediate deadlines or show the nearest deadline
def check_deadlines(threshold_days=1):
    df = pd.read_sql_query('SELECT * FROM tasks', conn)
    current_date = datetime.datetime.now().date()
    nearest_deadline = None
    nearest_deadline_days = float('inf')
    immediate_deadlines = False
    
    for index, row in df.iterrows():
        task_date = datetime.datetime.strptime(row['date'], "%Y-%m-%d").date()
        time_difference = (task_date - current_date).days
        if 0 <= time_difference <= threshold_days:
            immediate_deadlines = True
            print("\n")
            print("-" * 20)            
            print_colored_output(row['priority'], f"Task '{row['task']}' is due within {threshold_days} days: {row['date']}")
            print("-" * 20)
            print("\n")
        elif time_difference < nearest_deadline_days:
            nearest_deadline = row
            nearest_deadline_days = time_difference
    
    if not immediate_deadlines:
        if nearest_deadline is not None:
            print("\n")
            print("-" * 20)            
            print_colored_output(nearest_deadline['priority'], f"Task '{nearest_deadline['task']}' has the nearest deadline: {nearest_deadline['date']}")
            print("-" * 20)
            print("\n")
        else:
            print("No upcoming deadlines found.")

# Function to generate a timeline and display it as a plot
def generate_timeline():
    df = pd.read_sql_query('SELECT * FROM tasks', conn)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date', inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        color = 'green' if row['priority'] == 'Low' else 'yellow' if row['priority'] == 'Medium' else 'red'
        ax.plot([row['date'], row['date']], [0, 1], color=color, lw=row['weight'], label=row['task'] if i == 0 else "")

    ax.set_xlim([df['date'].min() - pd.Timedelta(days=1), df['date'].max() + pd.Timedelta(days=1)])
    ax.set_ylim([0, 1])
    ax.set_yticks([])
    ax.set_xlabel('Date')
    ax.set_title('Task Timeline')

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    plt.grid(True)
    plt.show()

# Function to search for tasks by keyword
def search_tasks():
    keyword = input("Enter keyword to search for: ")
    df = pd.read_sql_query('SELECT * FROM tasks WHERE task LIKE ? OR task_description LIKE ? OR subtask LIKE ? OR subtask_description LIKE ?', conn, params=('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
    if df.empty:
        print(f"No tasks found containing keyword: {keyword}")
    else:
        print(f"Tasks containing keyword '{keyword}':")
        print(df)

# Utility function to print colored output based on priority
def print_colored_output(priority, text):
    if priority == 'High':
        print(f"\033[91m{text}\033[0m")  # Red
    elif priority == 'Medium':
        print(f"\033[93m{text}\033[0m")  # Yellow
    else:
        print(f"\033[92m{text}\033[0m")  # Green

# Main loop
while True:
    print("Select an option:")
    print("1. Add task")
    print("2. View timeline")
    print("3. Remove task")
    print("4. Change task priority")
    print("5. Check deadlines")
    print("6. Generate timeline")
    print("7. Search tasks")
    print("8. Exit")

    choice = input("Enter your choice (1-8): ")

    if choice == "1":
        add_task()
    elif choice == "2":
        view_timeline()
    elif choice == "3":
        remove_task()
    elif choice == "4":
        change_task_priority()
    elif choice == "5":
        check_deadlines()
    elif choice == "6":
        generate_timeline()
    elif choice == "7":
        search_tasks()
    elif choice == "8":
        break
    else:
        print("Invalid choice. Please try again.")

conn.close()
