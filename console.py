error = lambda msg, end="\n": print(f"\033[91m ERROR:\t\t \033[0m{msg}", end=end)
info = lambda msg, end="\n": print(f"\033[94m INFO:\t\t \033[0m{msg}", end=end)
success = lambda msg, end="\n": print(f"\033[92m SUCCESS:\t \033[0m{msg}", end=end)
warning = lambda msg, end="\n": print(f"\033[93m WARN:\t\t \033[0m{msg}", end=end)


colors = {
    "error": "\033[91m",
    "info": "\033[94m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "end": "\033[0m"
}
cfmt = lambda msg, color, then: f"{colors[color]}{msg}{colors['end']}{colors[then]}"
cprint = lambda msg, color, end="\n": print(f"{colors[color]}{msg}{colors['end']}", end=end)
def mcprint(**kwargs):
    for k,v in kwargs.items():
        print(f"{colors[k]}{v}{colors['end']}")

def bprint(msg: bool):
    if msg:
        cprint("True", "success")
    else:
        cprint("False", "error")