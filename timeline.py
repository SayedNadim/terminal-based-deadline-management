# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# dates = ["2007-6-29", "2008-7-11", "2009-6-29", "2010-9-21", "2011-10-14", "2012-9-21", "2013-9-20",
#          "2014-9-19", "2015-9-25", "2016-3-31", "2016-9-16", "2017-9-22", "2017-11-3", "2018-9-21",
#          "2018-10-26", "2019-9-20", "2020-11-13", "2021-9-24", "2022-9-16"
#         ]
# phones = ["iPhone", "iPhone-3G", "iPhone-3GS", "iPhone 4", "iPhone 4S", "iPhone 5", "iPhone 5C/5S",
#           "iPhone 6/6 Plus", "iPhone 6S/6s Plus", "iPhone SE", "iPhone 7/7 Plus", "iPhone 8/8 Plus",
#           "iPhone X", "iPhone Xs/Max", "iPhone XR", "iPhone 11/Pro/Max", "iPhone 12 Pro", "iPhone 13 Pro",
#           "iPhone 14 Plus/Pro Max"
#          ]

# iphone_df = pd.DataFrame(data={"Date": dates, "Product": phones})
# iphone_df["Date"] = pd.to_datetime(iphone_df["Date"])
# iphone_df["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(iphone_df))]

with plt.style.context("fivethirtyeight"):
    fig, ax = plt.subplots(figsize=(9,18))

    ax.plot([0,]* len(iphone_df), iphone_df.Date, "-o", color="black", markerfacecolor="white");

    ax.set_yticks(pd.date_range("2007-1-1", "2023-1-1", freq="ys"), range(2007, 2024));
    ax.set_xlim(-7,7);

    for idx in range(len(iphone_df)):
        dt, product, level = iphone_df["Date"][idx], iphone_df["Product"][idx], iphone_df["Level"][idx]
        dt_str = dt.strftime("%b-%Y")
        ax.annotate(dt_str + "\n" + product, xy=(0.1 if level>0 else -0.1, dt),
                    xytext=(level, dt),
                    arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),
                    va="center"
                   );

    ax.spines[["left", "top", "right", "bottom"]].set_visible(False);
    ax.spines[["left"]].set_position(("axes", 0.5));
    ax.xaxis.set_visible(False);
    ax.set_title("iPhone Release Dates", pad=10, loc="left", fontsize=25, fontweight="bold");
    ax.grid(False)

plt.show()

import pandas as pd
import datetime
import time
import sys
import matplotlib.pyplot as plt

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


def change_weight(df):
    print("\nChanging Event Weight:")

    if df.empty:  # Check if dataframe is empty
        print("There are no events currently in the timeline.")
        return df  # Exit the function if empty

    # Get user input for index
    while True:
        try:
            index = int(input("Enter the index of the event you want to change weight for: "))
            if index in df.index:  # Check if index is valid
                break
            else:
                print("Invalid index. Please enter a valid index from the list.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # Get user input for weight
    while True
