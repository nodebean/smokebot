import os
import re

from util import hook


@hook.command(autohelp=False)
def mem(inp):
    ".mem -- returns bot's current memory usage -- linux/windows only"

    if os.name == "posix":
        status_file = open("/proc/%d/status" % os.getpid()).read()
        line_pairs = re.findall(r"^(\w+):\s*(.*)\s*$", status_file, re.M)
        status = dict(line_pairs)
        keys = "VmSize VmLib VmData VmExe VmRSS VmStk".split()
        return ", ".join(key + ":" + status[key] for key in keys)

    elif os.name == "nt":
        cmd = 'tasklist /FI "PID eq %s" /FO CSV /NH' % os.getpid()
        out = os.popen(cmd).read()

        total = 0
        for amount in re.findall(r"([,0-9]+) K", out):
            total += int(amount.replace(",", ""))

        return "memory usage: %d kB" % total

    return mem.__doc__
