import pandas as pd

# Function to add date and event
def add_event(df):
    print("\nAdding Event:")
    date = input("Enter date (YYYY-MM-DD): ")
    event = input("Enter event: ")
    subevents = input("Enter subevents (if any, separated by comma): ").split(',')
    priority = input("Enter priority (High, Medium, Low): ")
    weight = int(input("Enter weight of the event (1-10): "))
    new_row = {"Date": date, "Event": event, "Subevents": subevents, "Priority": priority, "Weight": weight}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("timeline.csv", index=False)  # Save data to CSV file after adding event
    print("Event added successfully.")
    return df

# Function to view existing timeline
def view_timeline(df):
    print("\nExisting Timeline:")
    print(df)

# Function to remove existing event
def remove_event(df):
    print("\nRemoving Event:")
    index = int(input("Enter the index of the event you want to remove: "))
    df = df.drop(index, axis=0)
    df.to_csv("timeline.csv", index=False)  # Save data to CSV file after removing event
    print("Event removed successfully.")
    return df

# Function to change event weight
def change_weight(df):
    print("\nChanging Event Weight:")
    index = int(input("Enter the index of the event you want to change weight for: "))
    weight = int(input("Enter the new weight of the event (1-10): "))
    df.loc[index, 'Weight'] = weight
    df.to_csv("timeline.csv", index=False)  # Save data to CSV file after changing weight
    print("Event weight changed successfully.")
    return df

# Load existing timeline data or create a new DataFrame if no data exists
try:
    timeline_df = pd.read_csv("timeline.csv")
except FileNotFoundError:
    timeline_df = pd.DataFrame(columns=["Date", "Event", "Subevents", "Priority", "Weight"])

# Main program loop
while True:
    print("\nOptions:")
    print("a. Add date and event")
    print("b. View existing timeline")
    print("c. Remove existing event")
    print("d. Change event weight")
    print("q. Quit")

    choice = input("Enter your choice: ")

    if choice == "a":
        timeline_df = add_event(timeline_df)
    elif choice == "b":
        view_timeline(timeline_df)
    elif choice == "c":
        timeline_df = remove_event(timeline_df)
    elif choice == "d":
        timeline_df = change_weight(timeline_df)
    elif choice == "q":
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Please select a valid option.")
