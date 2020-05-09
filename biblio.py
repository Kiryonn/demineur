import enum


class Difficulty(enum.Enum):
    EASY = 0
    NORMAL = 1
    HARD = 2


def neighbors(pos, nlig, ncol):
    res = []
    for i in range(max(pos[0] - 1, 0), min(pos[0] + 1, nlig) + 1):
        for j in range(max(pos[1] - 1, 0), min(pos[1] + 1, ncol) + 1):
            if i != pos[0] or j != pos[1]:
                res.append((i, j))
    return res


def print2d(tab):
    for line in tab:
        print(line)


def getimagepath(nb):
    if nb == -1:
        return "img/mine.png"
    else:
        return "img/%d.png" % nb


def getCase(x, y, dim):
    return y // dim, x // dim
