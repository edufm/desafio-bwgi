
import csv
import pathlib
from pprint import pprint
from datetime import datetime


def match_date(date_1_str: str, date_2_str: str) -> bool: # I hate this but i couldnt figure out a better way to handle months/years
    """ Compare 2 dates and check if they are one day within each other

    Args: 
        date_1_str: first date to compare
        date_2_str: second date to compare

    Return
        True if dates within one day else False
    """
    date_1 = datetime.strptime(date_1_str, '%Y-%m-%d').date()
    date_2 = datetime.strptime(date_2_str, '%Y-%m-%d').date()

    if abs((date_1 - date_2).days) <= 1:
        return True
    return False


inp_list_type = list[list[str, str, str, str]]
out_list_type = list[list[str, str, str, str, str]]


def reconcile_accounts(t1: inp_list_type, t2: inp_list_type) -> tuple[out_list_type, out_list_type]:
    """ Check if two lists of lists of strings are cointained within each other given a 1 day date tolerance

    Args:
        t1: first list of lists to compare
        t2: second list of lists to compare

    Returns:
        both lists tagged with FOUND or MISSING in each other    
    """
    # Create copies of the list with hashes for each element on the list to make comparison faster
    th1 = [[date, dep, val, tar, hash((dep, val, tar))] for date, dep, val, tar in t1]
    th2 = [[date, dep, val, tar, hash((dep, val, tar))] for date, dep, val, tar in t2]
    
    # Sort both lists to make sure dates are matching as soon as possible
    th1 = sorted(th1, key=lambda x: x[0])
    th2 = sorted(th2, key=lambda x: x[0])

    # Keep track of which elements in list2 have already been used
    used_indices_t2 = set()

    # Iterate over first list and check if the data is found on second list
    result_1, result_2 = [], []
    for date1, dep1, val1, tar1, h1 in th1:
        # Iterate through list2 to find the first match in order
        for index2, (date2, dep2, val2, tar2, h2) in enumerate(th2):
            if index2 not in used_indices_t2:
                # filters all atributes except dates
                if h1 == h2:
                    # filters dates
                    if match_date(date1, date2):
                        result_1.append([date1, dep1, val1, tar1, "FOUND"])
                        used_indices_t2.add(index2)  
                        break
        else:
            result_1.append([date1, dep1, val1, tar1, "MISSING"])

    # Create tags for list 2
    for index2, (date2, dep2, val2, tar2, h2) in enumerate(th2):
        result_2.append([date2, dep2, val2, tar2, "MISSING" if index2 not in used_indices_t2 else "FOUND"])

    return result_1, result_2


if __name__ == "__main__":
    # Set files path
    file_transactions_1 = pathlib.Path(__file__).parent.resolve() / 'transactions1.csv'
    file_transactions_2 = pathlib.Path(__file__).parent.resolve() / 'transactions2.csv'

    # Load data from files
    t1 = list(csv.reader(file_transactions_1.open(encoding="UTF-8")))
    t2 = list(csv.reader(file_transactions_2.open(encoding="UTF-8")))

    # Runs function
    t1r, t2r = reconcile_accounts(t1, t2)
    pprint(t1r)
    pprint(t2r)