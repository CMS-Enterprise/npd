import random
from datetime import date, timedelta


def random_date(start_date=None, end_date=None):
    """
    Generates a single random date between start_date and end_date (inclusive).
    """
    if start_date is None:
        start_date = date(1900, 1, 1)
    if end_date is None:
        end_date = date.today()
    # Calculate the total number of days in the range
    days_diff = (end_date - start_date).days

    # Generate a random number of days to add
    random_days = random.randint(0, days_diff)

    # Add the random days to the start date
    return start_date + timedelta(days=random_days)
