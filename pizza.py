#!/usr/bin/env python
# coding: utf-8

# Automatically generated from pizza.ipynb

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

print('Enter path to input file.')
# Read and display data
challenge = input()
file_in = Path(challenge)
file_out = Path(challenge.split(".")[0] + ".out")

with file_in.open(mode="r") as f:
    params = f.readline().replace("\n", "").split(" ")
    rows = int(params[0])
    cols = int(params[1])
    min_ing = int(params[2])
    max_cel = int(params[3])
    lines = []
    for line in f:
        row = []
        for char in line:
            if char == "M":
                row.append(0)
            elif char == "T":
                row.append(1)
        lines.append(row)

print("Rows:", rows)
print("Cols:", cols)
print("Min ingredient:", min_ing)
print("Max cells:", max_cel)
pizza = np.array(lines)
print(pizza)


def display_two(*arrs, cmaps, text=False):
    """Display two implots next to each other."""
    fig, axes = plt.subplots(1, len(arrs), figsize=(15, 10))
    for ax, arr, cmap in zip(axes, arrs, cmaps):
        ax.imshow(arr, cmap=cmap)
        if text:
            for (j, i), label in np.ndenumerate(arr):
                ax.text(i, j, f"{label:.2f}", ha="center", va="center", color="black")


def get_locs(r1, c1, r2, c2):
    """Get ndarray locations of given bounds."""
    rs = []
    cs = []
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            rs.append(r)
            cs.append(c)

    return rs, cs


def get_size(r1, c1, r2, c2):
    """Get the size of this slice."""
    return (r2 + 1 - r1) * (c2 + 1 - c1)


def get_count(sli):
    """Calculate how many of each ingredient are in this slice."""
    count = {0: 0, 1: 0}
    locs = get_locs(*sli)
    for r, c in zip(locs[0], locs[1]):
        count[pizza[(r, c)]] += 1

    return count


def get_num_done(sli):
    """How many of this slice have already been marked done."""
    return np.sum(done[get_locs(*sli)] == 1)


def get_prog(sli):
    """How many of the required ingredients does this slice have."""
    count = get_count(sli)
    return max(min_ing - count[0], 0) + max(min_ing - count[1], 0)


def large(sli):
    """Is this slice below size (0), exactly max size (1) or too big (2)."""
    size = get_size(*sli)
    if size < max_cel:
        return 0
    elif size == max_cel:
        return 1
    elif size > max_cel:
        return 2


def enough(sli):
    """Does this slice have enough of every ingredient."""
    count = get_count(sli)
    return min(tuple(count.values())) >= min_ing


def increment(r1, c1, r2, c2, opt):
    """Increment/decrement the specified corner of the slice."""
    if opt == 0:
        r1 -= 1 if r1 > 0 else 0
    elif opt == 1:
        c1 -= 1 if c1 > 0 else 0
    elif opt == 2:
        r2 += 1 if r2 < rows - 1 else 0
    elif opt == 3:
        c2 += 1 if c2 < cols - 1 else 0
    else:
        raise ValueError

    return r1, c1, r2, c2


def expand(sli, fill=False):
    """Find the most useful single expansion for this slice.

    When fill=False, slices will only grow until they have enough ingredients.
    With fill=True, slices will continue to grow until the upper limit.
    """

    # if the slice already has enough ingredients
    # or if the slice is already at max size
    change = False
    if not large(sli) and not (enough(sli) and not fill):
        num_done = get_num_done(sli)
        best_improve = 0
        prog = get_prog(sli)
        for opt in range(4):
            new = increment(*sli, opt)

            # if this new would result in too-large slice
            # or it treads onto cells already marked done
            # or it's the same cells
            if large(new) == 2 or get_num_done(new) > num_done or new == sli:
                continue

            # To make sure we don't do nothing, add the first
            # reasonable increase as our 'best'
            if not change:
                best = opt
                change = True

            # If this addition improves our progress more than the previos best
            improve = prog - get_prog(new)
            if improve > best_improve:
                best = opt
                change = True

    # If something has changed, make that experiment permanent and return
    if change:
        sli = increment(*sli, best)
    return change, sli


# This goes through the pizza, creating new slices as it goes, but not making
# them bigger than they need to be to satisfy the min_ingredients requirement.
slices = {}
done = np.zeros_like(pizza)
tried = np.zeros_like(pizza)

last_progress = 0
tot = rows * cols

count = 0
# While there undone or untried cells
while np.sum(done == 0) > 1 and np.sum(tried == 0) > 0:

    # Find the next untried cell
    not_done = np.where(tried == 0)
    r, c = not_done[0][0], not_done[1][0]
    sli = r, c, r, c

    while True:
        # Get the new slice, and whether it has changed
        change, sli = expand(sli)
        if change and enough(sli):  # If this slice has enough ingredients
            slices[count] = sli  # Add it to the official list
            done[get_locs(*sli)] = 1  # And mark that cell as done
            count += 1
            break

        elif not change:  # Otherwise we move on
            count += 1
            break

    # Whether or not these slices achieved anything, add the starting point to tried
    tried[get_locs(r, c, r, c)] = 1
    tried += done

    # Print progress every 10%
    progress = int(100 * (tot - np.sum(tried == 0)) / tot)
    if progress >= last_progress + 10:
        print(progress, "%")
        last_progress = progress


# Then we go back to the beginning, and expand each created slice as much as possible.
print("Expanding slices")
for key, sli in slices.items():
    while True:
        # with fill=True, the algorithm expands as much as it can
        change, sli = expand(sli, fill=True)
        if change and enough(sli):
            slices[key] = sli
            done[get_locs(*sli)] = 1
        else:
            break

# Create a sliced pizza, with each slice getting a unique value
out = np.ones_like(pizza) * -1
for key, value in slices.items():
    locs = get_locs(*value)
    out[locs] = key

display_two(pizza, out, cmaps=["Paired", "tab20"])

score = np.sum(done == 1)
print(score, "of max", rows * cols)
print(f"{100*score/(rows*cols):.0f} %")

with file_out.open("w") as f:
    print(len(slices), file=f)
    for _, value in slices.items():
        print(*value, file=f)
