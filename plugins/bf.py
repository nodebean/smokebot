"""brainfuck interpreter adapted from (public domain) code at
http://brainfuck.sourceforge.net/brain.py"""

from builtins import chr
from builtins import range
import re
import random
import unittest

from util import hook


@hook.command
def bf(inp, max_steps=1000000, buffer_size=5000):
    ".bf <prog> -- executes brainfuck program <prog>" ""

    program = re.sub("[^][<>+-.,]", "", inp)

    # create a dict of brackets pairs, for speed later on
    brackets = {}
    open_brackets = []
    for pos in range(len(program)):
        if program[pos] == "[":
            open_brackets.append(pos)
        elif program[pos] == "]":
            if len(open_brackets) > 0:
                brackets[pos] = open_brackets[-1]
                brackets[open_brackets[-1]] = pos
                open_brackets.pop()
            else:
                return "unbalanced brackets"
    if len(open_brackets) != 0:
        return "unbalanced brackets"

    # now we can start interpreting
    ip = 0  # instruction pointer
    mp = 0  # memory pointer
    steps = 0
    memory = [0] * buffer_size  # initial memory area
    rightmost = 0
    output = ""  # we'll save the output here

    # the main program loop:
    while ip < len(program):
        c = program[ip]
        if c == "+":
            memory[mp] = (memory[mp] + 1) % 256
        elif c == "-":
            memory[mp] = (memory[mp] - 1) % 256
        elif c == ">":
            mp += 1
            if mp > rightmost:
                rightmost = mp
                if mp >= len(memory):
                    # no restriction on memory growth!
                    memory.extend([0] * buffer_size)
        elif c == "<":
            mp = (mp - 1) % len(memory)
        elif c == ".":
            output += chr(memory[mp])
            if len(output) > 500:
                break
        elif c == ",":
            memory[mp] = random.randint(1, 255)
        elif c == "[":
            if memory[mp] == 0:
                ip = brackets[ip]
        elif c == "]":
            if memory[mp] != 0:
                ip = brackets[ip]

        ip += 1
        steps += 1
        if steps > max_steps:
            if output == "":
                output = "no output"
            output += " [exceeded %d iterations]" % max_steps
            break

    stripped_output = re.sub(r"[\x00-\x1F]", "", output)

    if stripped_output == "":
        if output != "":
            return "no printable output"
        return "no output"

    return stripped_output[:430]
