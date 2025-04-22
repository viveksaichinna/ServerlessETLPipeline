import csv
import random
from datetime import datetime, timedelta

statuses = ['confirmed', 'shipped', 'pending', 'cancelled']
customers = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']

def random_date(start_days_ago=90):
    """
    Generate a random date within the past specified number of days.

    Args:
        start_days_ago (int): The maximum number of days in the past to generate the date. 
                              Defaults to 90.

    Returns:
        str: A string representing the randomly generated date in the format 'YYYY-MM-DD'.
    """
    days_ago = random.randint(0, start_days_ago)
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

def generate_orders(filename='orders.csv', num_orders=200):
    """
    Generates a CSV file with fake order data.
    Args:
        filename (str): The name of the CSV file to create. Defaults to 'orders.csv'.
        num_orders (int): The number of fake orders to generate. Defaults to 100.
    The generated CSV file will contain the following columns:
        - OrderID: A unique identifier for each order (e.g., O0001, O0002, etc.).
        - Customer: A randomly selected customer name.
        - Amount: A randomly generated order amount between 10 and 500, rounded to 2 decimal places.
        - Status: A randomly selected order status.
        - OrderDate: A randomly generated date.
    The function writes the generated data to the specified file and prints a confirmation message
    indicating the number of orders generated and the file location.
    Note:
        This function assumes the existence of the following:
        - A `customers` list containing customer names.
        - A `statuses` list containing possible order statuses.
        - A `random_date()` function to generate random dates.
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['OrderID', 'Customer', 'Amount', 'Status', 'OrderDate'])

        for i in range(1, num_orders + 1):
            row = [
                f"O{i:04}",
                random.choice(customers),
                round(random.uniform(10, 500), 2),
                random.choice(statuses),
                random_date()
            ]
            writer.writerow(row)

    print(f"Generated {num_orders} fake orders to {filename}")

# Run the generator
generate_orders()