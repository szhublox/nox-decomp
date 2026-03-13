#!/bin/env python

import os
import pathlib
import logging
import re

GAME_FILES = (
    "../abi_wrappers.c",
    "GAME1.c",
    "GAME2.c",
    "GAME3.c",
    "GAME4.c",
    "GAME5.c",
    "GAME_ABI.c",
    "compat.c",
    "draw.c",
    "imm.c",
    "input.c",
    "netextras.c",
    "proto.h",
    "sm.c",
)
ADDR_REGEX = re.compile("_([0-9A-F]{6})")

logging.basicConfig(level=logging.INFO)


def funcs_to_rewrite(logger) -> set[str]:
    sub_regex = re.compile("^sub_[0-9A-F]{6}$")
    full_regex = re.compile(r"^([_a-zA-Z0-9 *]+ )?([_a-zA-Z0-9]+)(\(.*\);)?$")

    with open("../funcs.txt") as file:
        file_funcs = file.readlines()

    skip_indices = set()
    funcs = set()
    for index, line in enumerate(file_funcs):
        if index in skip_indices:
            continue

        line = line.strip()
        if not line:
            continue

        if line.startswith(("#", "//")):
            logger.debug("skipped comment or preprocessor: %s", line)
            continue

        comment = line.find(" //")
        if comment > -1:
            line = line[0:comment]

        if not (addr_match := ADDR_REGEX.search(line)):
            logger.info("skipped (no addr): %s", line)
            continue

        while " " in line and not line.endswith(";"):
            logger.info("appending to %s", line)
            index += 1
            skip_indices.add(index)
            line += f" {file_funcs[index].strip()}"

        if not (full_match := full_regex.match(line)):
            logger.error(f"not matched: {line}")
            continue

        if sub_regex.match(full_match.group(2)):
            logger.debug("nothing to do: %s", full_match.group(2))
            continue

        funcs.add((addr_match.group(1), full_match.group(2)))

    return funcs


if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent.parent)
    funcs = funcs_to_rewrite(logging.getLogger(f"{__name__}:prepare"))

    texts = []
    for filename in GAME_FILES:
        with open(filename, newline="") as file:
            texts.append(file.read())

    for func in funcs:
        for index, text in enumerate(texts):
            texts[index] = text.replace(f"sub_{func[0]}", func[1])

    for index, filename in enumerate(GAME_FILES):
        with open(filename, "w", newline="") as file:
            file.write(texts[index])
