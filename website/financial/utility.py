import numpy as np
from datetime import datetime
import pandas as pd

def datetime_to_np_datetime(d1: datetime):
    """
    Takes in datetime returns np.datetime64
    """
    if not isinstance(d1, datetime):
        return d1
    return np.datetime64(d1)

def np_datetime_to_datetime(d1) -> datetime:
    """
    Takes in np.datetime64 and returns datetime
    """
    if isinstance(d1, datetime):
        return d1
    i = pd.to_datetime(d1)
    return datetime(i.year, i.month, i.day)

def date_greater_than_or_equal_to(d1, d2) -> bool:
    """
    d1, d2 are datetime objects
    Returns True iff d1 >= d2
    """
    d10 = np_datetime_to_datetime(d1)
    d20 = np_datetime_to_datetime(d2)
    return (d10 - d20).days >= 0

def date_within_range(sample_date, start_date, end_date)->bool:
    """
    Returns True iff sample_date is within the range of the two provided dates, not inclusive
    all variables are datetime objects
    """
    sample_date0 = np_datetime_to_datetime(sample_date)
    start_date0 = np_datetime_to_datetime(start_date)
    end_date0 = np_datetime_to_datetime(end_date)
    if date_greater_than_or_equal_to(start_date0, sample_date0):
        return False
    if date_greater_than_or_equal_to(sample_date0, end_date0):
        return False
    return True

def date_within_inclusive_range(sample_date, start_date, end_date)->bool:
    """
     Returns True iff sample_date is within the range of the two provided dates, inclusive
    all variables are datetime objects
    """
    sample_date0 = np_datetime_to_datetime(sample_date)
    start_date0 = np_datetime_to_datetime(start_date)
    end_date0 = np_datetime_to_datetime(end_date)
    if date_greater_than(start_date0, sample_date0):
        return False
    if date_greater_than(sample_date0, end_date0):
        return False
    return True

def date_greater_than(d1, d2):
    """
    Returns true iff d1 > d2
    """
    d10 = np_datetime_to_datetime(d1)
    d20 = np_datetime_to_datetime(d2)
    return (d10 - d20).days > 0

def date_within_days(d1, d2, day_gap)->bool:
    """
    Returns True iff the two dates are within "day_gap" days of each other
    """
    d10 = np_datetime_to_datetime(d1)
    d20 = np_datetime_to_datetime(d2)
    if date_greater_than_or_equal_to(d10, d20):
        return ((d10-d20).days - day_gap) >= 0
    else:
        return ((d20-d10).days - day_gap) >= 0
    
def represent_date(input_date)->str:
    """
    Takes in datetime object and outputs {date.day}/{date.month}/{date.year} as a string
    """
    date = np_datetime_to_datetime(input_date)
    return f"{date.day}/{date.month}/{date.year}"

class OutDatedError(Exception):
    def __init__(self, message=""):
        Exception.__init__(self)
        self.message = message
    def __str__(self):
        return f"Attempting to call a date that is not within the stock data. {self.message}"

class InsufficientDataError(Exception):
    def __str__(self):
        return "Amount of data given is insufficient to predict action"

class NotIncludedError(Exception):
    def __init__(self, date = ""):
        Exception.__init__(self)
        self.date = date
    def __str__(self):
        return f"Date {self.date} is not actively within data. (Within range, but no trades)"
        
class NotFoundError(Exception):
    def __str__(self):
        return "Error. The Ticker You Entered Is Not From That Exchange. Data Not Found Error."

class OtherImportError(Exception):
    def __str__(self):
        return "Some Import Error Occured"