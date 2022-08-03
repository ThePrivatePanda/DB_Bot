import math
import re
from typing import Optional

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d|w))")
kmb_amount_regex = re.compile(r"(?:(\d*\.?\d*)(k|m|b))")
e_amount_regex = re.compile(r"^((\d*\.?\d*)e(\d*\.?\d*))$")
letters_regex = re.compile(r"[a-z]+")

def convert_time(time: str):
    units = {
        "s": 1,
        "m": 60,
        "h": 60*60,
        "d": 60*60*24,
        "w": 60*60*24*7,
    }

    time = time.lower()
    matches = re.findall(time_regex, time)

    if not matches:
        return False

    print(matches)

    if len([i for i in [j[1] for j in matches] if i not in units.keys()]) > 0:
        return False
    
    t = 0
    for amount, unit in matches:
        t += int(amount) * units[unit]
    
    return t


def convert_amount(amt: str) -> Optional[int]:
    units = {
        "k": 1000,
        "m": 1000000,
        "b": 1000000000,
        "e": 1
    }

    amt = amt.lower()
    letters = re.findall(letters_regex, amt)
    
    if any(i not in units.keys() for i in letters):
        return False

    if "e" in letters:
        if any(i in letters for i in ["k", "m", "b"]):
            return False
        reg = e_amount_regex
        matches = re.findall(reg, amt)
        if len(matches) != 1 or len(matches[0]) != 3:
            return False
        return float(matches[0][1]) * (10**int(matches[0][2])) 
    else:
        reg = kmb_amount_regex
        matches = re.findall(reg, amt)
        if len(matches) != 0:
            if any(i for i in [j[1] for j in matches] if i not in units.keys()):
                return False

            amount = 0
            for x, unit in matches:
                amount += int(x) * units[unit]
        else:
            try:
                amount = int(amt)
            except:
                return False

        return amount
