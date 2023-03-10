"""
dice.py: written by Scaevolus 2008, updated 2009
simulates dicerolls
"""
from builtins import str
from builtins import map
from builtins import range
import re
import random
import unittest

from util import hook


whitespace_re = re.compile(r"\s+")
valid_diceroll = r"^([+-]?(?:\d+|\d*d(?:\d+|F))(?:[+-](?:\d+|\d*d(?:\d+|F)))*)( .+)?$"
valid_diceroll_re = re.compile(valid_diceroll, re.I)
sign_re = re.compile(r"[+-]?(?:\d*d)?(?:\d+|F)", re.I)
split_re = re.compile(r"([\d+-]*)d?(F|\d*)", re.I)


def nrolls(count, n):
    "roll an n-sided die count times"
    if n == "F":
        return [random.randint(-1, 1) for x in range(min(count, 100))]
    if n < 2:  # it's a coin
        if count < 5000:
            return [random.randint(0, 1) for x in range(count)]
        else:  # fake it
            return [int(random.normalvariate(0.5 * count, (0.75 * count) ** 0.5))]
    else:
        if count < 5000:
            return [random.randint(1, n) for x in range(count)]
        else:  # fake it
            return [
                int(
                    random.normalvariate(
                        0.5 * (1 + n) * count,
                        (((n + 1) * (2 * n + 1) / 6.0 - (0.5 * (1 + n)) ** 2) * count)
                        ** 0.5,
                    )
                )
            ]


@hook.command("roll")
# @hook.regex(valid_diceroll, re.I)
@hook.command
def dice(inp):
    ".dice <diceroll> -- simulates dicerolls, e.g. .dice 2d20-d5+4 roll 2 " "D20s, subtract 1D5, add 4"

    try:  # if inp is a re.match object...
        (inp, desc) = inp.groups()
    except AttributeError:
        (inp, desc) = valid_diceroll_re.match(inp).groups()

    if "d" not in inp:
        return

    spec = whitespace_re.sub("", inp)
    if not valid_diceroll_re.match(spec):
        return "Invalid diceroll"
    groups = sign_re.findall(spec)

    total = 0
    rolls = []

    for roll in groups:
        count, side = split_re.match(roll).groups()
        if count in ["", " ", "+", "-"]:
            count = int("%s1" % count)
        else:
            count = int(count)

        if side.upper() == "F":  # fudge dice are basically 1d3-2
            for fudge in nrolls(count, "F"):
                if fudge == 1:
                    rolls.append("\x033+\x0F")
                elif fudge == -1:
                    rolls.append("\x034-\x0F")
                else:
                    rolls.append("0")
                total += fudge
        elif side == "":
            total += count
        else:
            side = int(side)
            try:
                if count > 0:
                    dice = nrolls(count, side)
                    rolls += list(map(str, dice))
                    total += sum(dice)
                else:
                    dice = nrolls(-count, side)
                    rolls += [str(-x) for x in dice]
                    total -= sum(dice)
            except OverflowError:
                return "Thanks for overflowing a float, jerk >:["

    if desc:
        return "%s: %d (%s=%s)" % (desc.strip(), total, inp, ", ".join(rolls))
    else:
        return "%d (%s=%s)" % (total, inp, ", ".join(rolls))


class DiceTest(unittest.TestCase):
    def test_complex_roll_with_subtraction(self):
        actual = dice("2d20-d5+4")

        match = re.match(
            "(?P<result>\d+) \(2d20-d5\+4=(?P<a>\d+), (?P<b>\d+), -(?P<c>\d+)\)", actual
        )

        assert match is not None

        expected_result = (
            int(match.group("a")) + int(match.group("b")) - int(match.group("c")) + 4
        )

        assert expected_result == int(match.group("result"))
