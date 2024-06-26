import datetime
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd



# # function to add date
# def add_date():
#     date = input("Enter date (YYYY-MM-DD): ")
#     if len(date) > 10:
#         # String has time information
#         datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#     else:
#         # String has no time information
#         datetime.datetime.strptime(date, "%Y-%m-%d")
#     date = date[:10]
#     date = date.replace("-0", "-")  # Remove leading zeros from single-digit dates
#     return date


# def add_tasks_subtasks_weights():
#     task = input("Enter task: ")
#     subtasks = input("Enter subtasks (if any, separated by comma): ").split(',')

#     while True:  # Loop until valid priority is entered
#         priority = input("Enter priority (High, Medium, Low): ")
#         if priority in ["High", "Medium", "Low"]:
#             break
#         print("Invalid priority. Please enter High, Medium, or Low.")

#     while True:  # Loop until valid weight is entered
#         try:
#             weight = int(input("Enter weight of the task (1-10): "))
#             if not 1 <= weight <= 10:
#                 raise ValueError
#             break
#         except ValueError:
#             print("Invalid weight. Please enter an integer between 1 and 10.")

#     return task, subtasks, priority, weight


# # Function to add date and task
# def add_task(df):
#     print("\n")
#     print("-" * 20)
#     print("Adding Task:")

#     while True:  # Enclosing loop for retrying all inputs if needed
#         try:
#             date = add_date()
#             task, subtasks, priority, weight = add_tasks_subtasks_weights()
#             break  # Exit the enclosing while loop if all inputs are valid

#         except ValueError:
#             print("Invalid input. Please try again.")

#     new_row = {"Date": date, "Task": task, "Subtasks": subtasks, "Priority": priority, "Weight": weight}
#     df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
#     df.to_csv("timeline.csv", index=False)
#     print("\n")
#     print("-" * 20)
#     print("task added successfully.")
#     print("-" * 20)
#     print("\n")
#     return df



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
def add_task(df):
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
        new_row = {"Date": subtask_dates[i], "Task": task, "Task Description": task_description,
                   "Subtask": subtask, "Subtask Description": subtask_descriptions[i],
                   "Priority": subtask_priorities[i], "Weight": subtask_weights[i]}
        new_rows.append(new_row)
    
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_csv("timeline.csv", index=False)
    print("\n")
    print("-" * 20)
    print("Task added successfully.")
    print("-" * 20)
    print("\n")
    return df

# Function to view existing timeline
def view_timeline(df):

    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no tasks currently in the timeline.")
        print("-" * 20)
        print("\n")
        
    else:
        print("\nExisting Timeline:")
        print(df)


def remove_task(df):
    print("\nRemoving task:")

    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no tasks currently in the timeline.")
        print("-" * 20)
        print("\n")
        
        return df  # Exit the function if empty

    # Print the list of tasks with indices (same as before)
    print("Index\tTask")
    print("-------\t-------")
    for index, row in df.iterrows():
        print(f"{index}\t{row['Task']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the task you want to remove (put -1 to go back to menu): "))
            if index in df.index:  # Check if index is valid
                break
            elif index == -1:
                print("Exiting to the main menu...")
                return df                
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Remove task and save data (same as before)
    df = df.drop(index, axis=0)
    df.to_csv("timeline.csv", index=False)
    print("task removed successfully.")
    print("-" * 20)
    print("\n")
    return df


# Function to change task weight
def change_task_priority(df):
    print("\nChanging task Priority:")

    if df.empty:  # Check if dataframe is empty
        print("There are no tasks currently in the timeline.")
        return df  # Exit the function if empty
    else:
        # Print the list of tasks with indices (same as before)
        print("Index\tTask\tPriority\tWeights")
        print("-------\t-------")
        for index, row in df.iterrows():
            print(f"{index}\t{row['Task']}\t{row['Priority']}\t{row['Weight']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the task you want to change weight for: "))
            if index in df.index:  # Check if index is valid
                break
            elif index == -1:
                return df 
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")


    # Get user input for weight
    while True:
        try:
            priority = input("Enter the new priority of the task (High, Medium, Low): ")
            if priority in ["High", "Medium", "Low"]:
                break
            elif priority == -1:
                print("Exiting to the main menu...")
                return df 
            else:
                print("Invalid priority. Please enter from High, Medium or Low.")
        except ValueError:
            print("Invalid input. Please enter from High, Medium or Low..")


    # Get user input for weight
    while True:
        try:
            weight = int(input("Enter the new weight of the task (1-10): "))
            if 1 <= weight <= 10:
                break
            elif index == -1:
                print("Exiting to the main menu...")
                return df 
            else:
                print("Invalid weight. Please enter a value between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")


    # Change weight and save data (same as before)
    df.loc[index, 'Priority'] = priority
    df.loc[index, 'Weight'] = weight
    df.to_csv("timeline.csv", index=False)
    print("task weight changed successfully.")
    return df


# Function to check for immediate deadlines or show the nearest deadline
def check_deadlines(df, threshold_days=1):
    current_date = datetime.datetime.now().date()
    nearest_deadline = None
    nearest_deadline_days = float('inf')
    immediate_deadlines = False
    
    for index, row in df.iterrows():
        task_date = datetime.datetime.strptime(row['Date'], "%Y-%m-%d").date()
        time_difference = (task_date - current_date).days
        if 0 <= time_difference <= threshold_days:
            immediate_deadlines = True
            print("\n")
            print("-" * 20)            
            print_colored_output(row['Priority'], f"Task '{row['Task']}' is due within {threshold_days} days: {row['Date']}")
            print("-" * 20)
            print("\n")
        elif time_difference < nearest_deadline_days:
            nearest_deadline = row
            nearest_deadline_days = time_difference
    
    if not immediate_deadlines:
        if nearest_deadline is not None:
            print("\n")
            print("-" * 20)
            print_colored_output(nearest_deadline['Priority'], f"The nearest deadline is '{nearest_deadline['Task']}' due on {nearest_deadline['Date']}")
            print("-" * 20)
            print("\n")
        elif nearest_deadline_days <= threshold_days:
            print("\n")
            print("-" * 20)
            print(f"No immediate deadlines. The nearest deadline is '{nearest_deadline['Task']}' due on {nearest_deadline['Date']}")
            print("-" * 20)
            print("\n")
        else:
            print("\n")
            print("-" * 20)
            print("No deadlines found in the timeline.")
            print("-" * 20)
            print("\n")


# Function to calculate internal weight based on priority and weight
def calculate_internal_weight(priority, weight):
    priority_values = {"High": 20, "Medium": 10, "Low": 5}
    return priority_values[priority] * weight


# Function to print colored output based on priority
def print_colored_output(priority, message):
    # colors = {"High": '\033[91m', "Medium": '\033[93m', "Low": '\033[92m'}
    colors = {"High": COLOR.get('red'), "Medium": COLOR.get('blue'), "Low": COLOR.get("green")}
    color_end = '\033[0m'
    print(colors[priority] + message + color_end)


#TODO: Show timeline based on range
# Function to print the text-based timeline
def print_text_timeline(data, horizontal=True):
    """
    Prints a text-based representation of a timeline from a pandas DataFrame or a CSV file.

    Args:
        data (pandas.DataFrame or str): A DataFrame containing timeline data or a path to a CSV file.
        horizontal (bool, optional): If True, prints a horizontal timeline. 
                                    If False, prints a vertical timeline. Defaults to True.
    """
    # Check if data is a DataFrame
    if isinstance(data, pd.DataFrame):
    # Sort data by date (assuming "Date" column exists)
        data = data.sort_values(by=["Date"])
    else:
        # Assume data is a CSV path, read it as a DataFrame
        data = pd.read_csv(data)
        # Sort data by date
        data = data.sort_values(by=["Date"])

    # Define priority symbols (modify as needed)
    priority_symbols = {"High": "*", "Medium": "-", "Low": " "}

    print("\n")
    print("-" * 20)
    # Print timeline header
    print("** Timeline **")
    print("_" * 20)

    # Function logic for printing tasks (horizontal or vertical)
    if horizontal:
        # Horizontal timeline logic (same as previous example)
        for index, row in data.iterrows():
            date_str = row["Date"]
            task_str = row["Task"]
            priority = row["Priority"]
            symbol = priority_symbols[priority]

            indent = "    " * (2 - len(priority))

            print(f"{indent}{symbol} {date_str}: {task_str}")
    else:
        # Vertical timeline logic (similar to previous example)
        for index, row in data.iterrows():
            date_str = row["Date"]
            task_str = row["task"]
            priority = row["Priority"]
            symbol = priority_symbols[priority]

            print(f"{symbol if priority != 'Low' else ' '}{' ' * (len(priority) - 1)} {date_str}")
            print(f"{' ' * (2 + len(priority))}{task_str}")

    # Print timeline footer
    print("-" * 20)
    print("\n")


# Function to define color mapping for priority
def get_priority_color(priority):
    priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    return priority_colors[priority]


#TODO: Show timeline based on range

# Function to visualize timeline with customizable interval and date formatting
def visualize_timeline(df, interval="W"):
    if df.empty:
        print("There are no tasks to visualize.")
        return

    # Convert date strings to datetime objects for plotting
    df["Date"] = pd.to_datetime(df["Date"])

    # Sort DataFrame by date
    df = df.sort_values(by="Date")

    # Extract data for plotting
    dates = df["Date"].tolist()
    tasks = df["Task"].tolist()
    priorities = df["Priority"].tolist()
    colors = [get_priority_color(p) for p in priorities]  # Get colors based on priority

    # Create the plot with adjusted y-axis limits (set minimum to 0)
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot a horizontal line for the timeline
    plt.axhline(y=0, color="black", linewidth=1)

    # Plot task markers with consistent size and color based on priority
    task_marker_size = 5  # Adjust marker size as needed
    for date, task, color in zip(dates, tasks, colors):
        ax.plot(
            date,
            0,
            marker="o",
            markersize=task_marker_size,
            linestyle="",
            markerfacecolor=color,
            markeredgewidth=2,
            markeredgecolor="black",
        )

    # # Generate regular interval dates (adjust frequency and format based on interval)
    # min_date = df["Date"].min()
    # max_date = df["Date"].max()
    # interval_dates = pd.date_range(start=min_date, end=max_date, freq=interval)

    # # Combine and sort all dates
    # all_dates = sorted(list(dates) + list(interval_dates))
    all_dates = sorted(list(dates))

    # Plot date markers (vertical lines) at all positions
    for date in all_dates:
        ax.axvline(x=date, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

    # # Set axis labels and title
    # ax.set_xlabel("Date")
    # ax.set_title("Timeline Visualization")

    # Set x-axis ticks and labels for all dates with dynamic format based on interval
    ax.set_xticks(all_dates)
    if interval in ["D", "W"]:  # Daily or weekly - show full date
        date_format = "%Y-%m-%d"
    elif interval in ["M", "BM"]:  # Monthly or bimonthly - show month and year
        date_format = "%Y-%m"
    else:  # Other intervals - consider customizing format or abbreviation
        date_format = "%y-%b"  # Abbreviated year and month
    
    
    ax.set_xticklabels([date.strftime(date_format) for date in all_dates], rotation=90, ha="right")

    # Remove y-axis ticks and labels
    ax.yaxis.set_visible(False)

    # Annotate task names above the markers (optional)
    for date, task, color in zip(dates, tasks, colors):
        ax.text(date, 0.1, task, ha="center", va="bottom", color=color, fontsize=10, rotation=90)

    # Optional: Color shading for intervals (using fill_between)
    if interval != "D":  # Avoid shading for daily intervals for better clarity
        start_dates = [d for d in all_dates[:-1] if d not in dates]
        end_dates = [d for d in all_dates[1:] if d not in dates]
        ax.fill_between(
            start_dates, 0, 1, color="white", alpha=0.2, label="No Deadline"
        )  # Adjust color and alpha as needed

    # plt.legend()  # Add legend if shading is used
    plt.tight_layout()

    # Display the plot
    plt.show()


# Function to search tasks by keyword
def search_tasks(df, keyword):
    filtered_df = df[df["Task"].str.contains(keyword, case=False)]  # Case-insensitive search
    if filtered_df.empty:
        print(f"No tasks found containing the keyword '{keyword}'.")
    else:
        print(f"\nSearch results for '{keyword}':")
        print(filtered_df)

def show_user_choice():
    print("-" * 20)
    print("Choose operation: [a/b/c/d/e/f/g/h/q]")
    print("-" * 20)
    print("a. Add date and task.")
    print("b. View existing tasks.")
    print("c. Remove existing task.")
    print("d. Change task priority.")
    print("e. Check immediate deadlines.")
    print("f. Check the entire timeline.")
    print("g. Visualize and save timeline.")
    print("h. Search timeline for tasks.")
    print("q. Quit")
    print("-" * 20)


def execute_user_choice(choice, timeline_df):
    if choice == "a":
        timeline_df = add_task(timeline_df)
    elif choice == "b":
        view_timeline(timeline_df)
    elif choice == "c":
        timeline_df = remove_task(timeline_df)
    elif choice == "d":
        timeline_df = change_task_priority(timeline_df)
    elif choice == "e":
        check_deadlines(timeline_df)
    elif choice == "f":
        print_text_timeline(timeline_df)
    elif choice == "g":
        visualize_timeline(timeline_df)
    elif choice == "h":
        keyword = input("Enter keyword to search for tasks: ")
        search_tasks(timeline_df.copy(), keyword)
    else:
        print("Invalid choice. Please select a valid option.")
        show_user_choice()
    return timeline_df


if __name__=="__main__":

    # Store a dictionary of colors.
    COLOR = {
        'blue': '\033[94m',
        'default': '\033[99m',
        'grey': '\033[90m',
        'yellow': '\033[93m',
        'black': '\033[90m',
        'cyan': '\033[96m',
        'green': '\033[92m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'red': '\033[91m'
    }

    # Load existing timeline data or create a new DataFrame if no data exists
    try:
        timeline_df = pd.read_csv("timeline.csv")
        if len(timeline_df) == 0:
            print("The timeline is currently empty.")
            # Optionally, provide instructions or exit the program here
    except FileNotFoundError:
        timeline_df = pd.DataFrame(columns=["Date", "Task", "Subtasks", "Priority", "Weight"])



    # show nearest deadline first
    check_deadlines(timeline_df)

    # create a counter to avoid unnecessary loop of options
    app_run_counter = 0
    # Main program loop
    while True:
        if app_run_counter == 0:
            show_user_choice()
            choice = input("Enter your choice: ")
            if choice == "q":
                print("Exiting program.")
                break
            else:
                timeline_df = execute_user_choice(choice=choice, timeline_df=timeline_df)
        else:
            app_run_choice = input("Do you want to continue editing your timeline? [y for continue/ n or q for exiting]: ")
            if app_run_choice.lower() == "y" or app_run_choice == "":
                show_user_choice()
                choice = input("Enter your choice: ")
                if choice == "q":
                    print("Exiting program.")
                    break
                else:
                    timeline_df = execute_user_choice(choice=choice, timeline_df=timeline_df)
            elif app_run_choice.lower() in ['n', 'q']:
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please enter y to continue, or n or q to exit.")

        app_run_counter += 1