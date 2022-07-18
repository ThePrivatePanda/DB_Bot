import re
time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d|w))")

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

