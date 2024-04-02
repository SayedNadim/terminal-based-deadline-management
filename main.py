import datetime
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd


# Function to add date and event
def add_event(df):
    print("\n")
    print("-" * 20)
    print("Adding Event:")

    while True:  # Enclosing loop for retrying all inputs if needed
        try:
            date = input("Enter date (YYYY-MM-DD): ")
            datetime.datetime.strptime(date, "%Y-%m-%d")  # Validate format
            date = date.replace("-0", "-")  # Remove leading zeros from single-digit dates

            event = input("Enter event: ")
            subevents = input("Enter subevents (if any, separated by comma): ").split(',')

            while True:  # Loop until valid priority is entered
                priority = input("Enter priority (High, Medium, Low): ")
                if priority in ["High", "Medium", "Low"]:
                    break
                print("Invalid priority. Please enter High, Medium, or Low.")

            weight = int(input("Enter weight of the event (1-10): "))
            if not 1 <= weight <= 10:
                raise ValueError  # Raise for outer try-except to catch

            break  # Exit the enclosing while loop if all inputs are valid

        except ValueError:
            print("Invalid input. Please try again.")

    new_row = {"Date": date, "Event": event, "Subevents": subevents, "Priority": priority, "Weight": weight}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("timeline.csv", index=False)
    print("Event added successfully.")
    print("-" * 20)
    print("\n")
    return df


# Function to view existing timeline
def view_timeline(df):

    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no events currently in the timeline.")
        print("-" * 20)
        print("\n")
        
    else:
        print("\nExisting Timeline:")
        print(df)


def remove_event(df):
    print("\nRemoving Event:")

    if df.empty:  # Check if dataframe is empty
        print("\n")
        print("-" * 20)   
        print("There are no events currently in the timeline.")
        print("-" * 20)
        print("\n")
        
        return df  # Exit the function if empty

    # Print the list of events with indices (same as before)
    print("Index\tEvent")
    print("-------\t-------")
    for index, row in df.iterrows():
        print(f"{index}\t{row['Event']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the event you want to remove (put -1 to go back to menu): "))
            if index in df.index:  # Check if index is valid
                break
            elif index == -1:
                print("Exiting to the main menu...")
                return df                
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Remove event and save data (same as before)
    df = df.drop(index, axis=0)
    df.to_csv("timeline.csv", index=False)
    print("Event removed successfully.")
    print("-" * 20)
    print("\n")
    return df


# Function to change event weight
def change_event_priority(df):
    print("\nChanging Event Priority:")

    if df.empty:  # Check if dataframe is empty
        print("There are no events currently in the timeline.")
        return df  # Exit the function if empty
    else:
        # Print the list of events with indices (same as before)
        print("Index\tEvent")
        print("-------\t-------")
        for index, row in df.iterrows():
            print(f"{index}\t{row['Event']}\t{row['Priority']}\t{row['Weight']}")

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the event you want to change weight for: "))
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
            priority = input("Enter the new priority of the event (High, Medium, Low): ")
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
            weight = int(input("Enter the new weight of the event (1-10): "))
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
    print("Event weight changed successfully.")
    return df


# Function to check for immediate deadlines or show the nearest deadline
def check_deadlines(df, threshold_days=1):
    current_date = datetime.datetime.now().date()
    nearest_deadline = None
    nearest_deadline_days = float('inf')
    immediate_deadlines = False
    
    for index, row in df.iterrows():
        event_date = datetime.datetime.strptime(row['Date'], "%Y-%m-%d").date()
        time_difference = (event_date - current_date).days
        if 0 <= time_difference <= threshold_days:
            immediate_deadlines = True
            print("\n")
            print("-" * 20)            
            print_colored_output(row['Priority'], f"Event '{row['Event']}' is due within {threshold_days} days: {row['Date']}")
            print("-" * 20)
            print("\n")
        elif time_difference < nearest_deadline_days:
            nearest_deadline = row
            nearest_deadline_days = time_difference
    
    if not immediate_deadlines:
        if nearest_deadline is not None:
            print("\n")
            print("-" * 20)
            print_colored_output(nearest_deadline['Priority'], f"The nearest deadline is '{nearest_deadline['Event']}' due on {nearest_deadline['Date']}")
            print("-" * 20)
            print("\n")
        elif nearest_deadline_days <= threshold_days:
            print("\n")
            print("-" * 20)
            print(f"No immediate deadlines. The nearest deadline is '{nearest_deadline['Event']}' due on {nearest_deadline['Date']}")
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

    # Function logic for printing events (horizontal or vertical)
    if horizontal:
        # Horizontal timeline logic (same as previous example)
        for index, row in data.iterrows():
            date_str = row["Date"]
            event_str = row["Event"]
            priority = row["Priority"]
            symbol = priority_symbols[priority]

            indent = "    " * (2 - len(priority))

            print(f"{indent}{symbol} {date_str}: {event_str}")
    else:
        # Vertical timeline logic (similar to previous example)
        for index, row in data.iterrows():
            date_str = row["Date"]
            event_str = row["Event"]
            priority = row["Priority"]
            symbol = priority_symbols[priority]

            print(f"{symbol if priority != 'Low' else ' '}{' ' * (len(priority) - 1)} {date_str}")
            print(f"{' ' * (2 + len(priority))}{event_str}")

    # Print timeline footer
    print("-" * 20)
    print("\n")

#TODO: Show timeline based on range
# Function to define color mapping for priority
def get_priority_color(priority):
    priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    return priority_colors[priority]

# Function to define color mapping for priority
def get_priority_color(priority):
    priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    return priority_colors[priority]


# Function to visualize timeline with customizable interval and date formatting
def visualize_timeline(df, interval="W"):
    if df.empty:
        print("There are no events to visualize.")
        return

    # Convert date strings to datetime objects for plotting
    df["Date"] = pd.to_datetime(df["Date"])

    # Sort DataFrame by date
    df = df.sort_values(by="Date")

    # Extract data for plotting
    dates = df["Date"].tolist()
    events = df["Event"].tolist()
    priorities = df["Priority"].tolist()
    colors = [get_priority_color(p) for p in priorities]  # Get colors based on priority

    # Create the plot with adjusted y-axis limits (set minimum to 0)
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot a horizontal line for the timeline
    plt.axhline(y=0, color="black", linewidth=1)

    # Plot event markers with consistent size and color based on priority
    event_marker_size = 20  # Adjust marker size as needed
    for date, event, color in zip(dates, events, colors):
        ax.plot(
            date,
            0,
            marker="o",
            markersize=event_marker_size,
            linestyle="",
            markerfacecolor=color,
            markeredgewidth=2,
            markeredgecolor="black",
        )

    # Generate regular interval dates (adjust frequency and format based on interval)
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    interval_dates = pd.date_range(start=min_date, end=max_date, freq=interval)

    # Combine and sort all dates
    all_dates = sorted(list(dates) + list(interval_dates))

    # Plot date markers (vertical lines) at all positions
    for date in all_dates:
        ax.axvline(x=date, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

    # Set axis labels and title
    ax.set_xlabel("Date")
    ax.set_title("Timeline Visualization")

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

    # Annotate event names above the markers (optional)
    for date, event, color in zip(dates, events, colors):
        ax.text(date, 0.1, event, ha="center", va="bottom", color=color, fontsize=10, rotation=90)

    # Optional: Color shading for intervals (using fill_between)
    if interval != "D":  # Avoid shading for daily intervals for better clarity
        start_dates = [d for d in all_dates[:-1] if d not in dates]
        end_dates = [d for d in all_dates[1:] if d not in dates]
        ax.fill_between(
            start_dates, 0, 1, color="lightgray", alpha=0.2, label="No Deadline"
        )  # Adjust color and alpha as needed

    plt.legend()  # Add legend if shading is used
    plt.tight_layout()

    # Display the plot
    plt.show()


# Function to search events by keyword
def search_events(df, keyword):
    filtered_df = df[df["Event"].str.contains(keyword, case=False)]  # Case-insensitive search
    if filtered_df.empty:
        print(f"No events found containing the keyword '{keyword}'.")
    else:
        print(f"\nSearch results for '{keyword}':")
        print(filtered_df)

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
        timeline_df = pd.DataFrame(columns=["Date", "Event", "Subevents", "Priority", "Weight"])



    # show nearest deadline first
    check_deadlines(timeline_df)

    # Main program loop
    while True:
        print("-" * 20)
        print("Options:")
        print("-" * 20)
        print("a. Add date and event.")
        print("b. View existing events.")
        print("c. Remove existing event.")
        print("d. Change event priority.")
        print("e. Check immediate deadlines.")
        print("f. Check the entire timeline.")
        print("g. Visualize and save timeline.")
        print("h. Search timeline for events.")
        print("q. Quit")
        print("-" * 20)

        choice = input("Enter your choice: ")

        if choice == "a":
            timeline_df = add_event(timeline_df)
        elif choice == "b":
            view_timeline(timeline_df)
        elif choice == "c":
            timeline_df = remove_event(timeline_df)
        elif choice == "d":
            timeline_df = change_event_priority(timeline_df)
        elif choice == "e":
            check_deadlines(timeline_df)
        elif choice == "f":
            print_text_timeline(timeline_df)
        elif choice == "g":
            visualize_timeline(timeline_df)
        elif choice == "h":
            keyword = input("Enter keyword to search for events: ")
            search_events(timeline_df.copy(), keyword)
        elif choice == "q":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")
