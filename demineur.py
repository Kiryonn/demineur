from random import randrange
from tkinter import Tk, Frame, Label, Canvas, Button, PhotoImage, Radiobutton
from tkinter.font import Font
from biblio import *


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Demineur")
        self._frame = None
        self.switchFrame(MainMenu)

    def switchFrame(self, FrameClass, **opt):
        if self._frame is not None:
            self._frame.destroy()
        self._frame = FrameClass(self, **opt)
        self._frame.pack()


class MainMenu(Frame):
    def __init__(self, master):
        """:type master: Tk"""
        Frame.__init__(self, master)
        Button(self, width=7, text="Play", command=self.play).pack(padx=100, pady=(50, 0))
        Button(self, width=7, text="Quitter", command=lambda: master.destroy()).pack(padx=100, pady=(0, 50))

    def play(self):
        self.master.switchFrame(Game)


class Game(Frame):
    def __init__(self, master):
        """:type master: Tk"""
        # super constructeur
        Frame.__init__(self, master)

        # attributs
        self.playing = False
        self.firstClick = True
        self.difficulty = Difficulty.EASY
        self.board = []
        self.bombsPos = []
        self.flagsPos = []
        self.casesState = []  # False normal, True appuyé
        self.nbBombs = 0
        self.boxSize = 25  # constante
        self.nbcols = 0
        self.nbrows = 0

        # images et sauvegardes des refs (necessaire pour avoir l'affichage des images correctement)
        self.imgNewGameButton = PhotoImage(file="img/smiley_normal.png")
        self.imgDef = PhotoImage(file="img/default.png")
        self.imgBomb = PhotoImage(file="img/mine.png")
        self.imgFlag = PhotoImage(file="img/flag.png")
        self.imgNumbers = [PhotoImage(file="img/%d.png" % i) for i in range(7)]

        # composants
        self.diffChoice = Frame(self)
        easy = Radiobutton(self.diffChoice, variable=0, text="débutant", value=0,
                           command=lambda: self.changeDifficulty(Difficulty.EASY))
        medium = Radiobutton(self.diffChoice, variable=0, text="intermediaire", value=1,
                             command=lambda: self.changeDifficulty(Difficulty.NORMAL))
        hard = Radiobutton(self.diffChoice, variable=0, text="expert", value=2,
                           command=lambda: self.changeDifficulty(Difficulty.HARD))
        self.nbBombDisplayer = Label(self, text=0)
        self.newGameButton = Button(self, image=self.imgNewGameButton, command=self.reinitialisation)
        self.time = Label(self, text="00:00")
        self.cnv = Canvas(self)

        # placement
        self.diffChoice.grid(row=0, column=0)
        easy.pack(anchor="w")
        medium.pack(anchor="w")
        hard.pack(anchor="w")
        self.nbBombDisplayer.grid(row=0, column=1)
        self.newGameButton.grid(row=0, column=2)
        self.time.grid(row=0, column=3)
        self.cnv.grid(row=1, column=0, columnspan=4)

        # events
        self.cnv.bind("<Button-1>", self.handlerLeftClick)
        self.cnv.bind("<Button-3>", self.handlerRightClick)

        # réglages
        self.reinitialisation()
        easy.select()

    def reinitialisation(self):
        # réglages de base
        self.firstClick = True
        self.playing = False
        self.time.configure(text="00:00")
        self.changeNewGameButtonImage(PhotoImage(file="img/smiley_normal.png"))
        self.cnv.delete("all")
        self.flagsPos.clear()

        # réglages selon la difficulté
        if self.difficulty == Difficulty.EASY:
            self.nbBombs = 10
            self.nbrows, self.nbcols = 9, 9
        elif self.difficulty == Difficulty.NORMAL:
            self.nbBombs = 40
            self.nbrows, self.nbcols = 16, 16
        else:
            self.nbBombs = 99
            self.nbrows, self.nbcols = 16, 30
        self.nbBombDisplayer.configure(text=self.nbBombs)

        # création du plateau
        self.board = [[0 for _2 in range(self.nbcols)] for _ in range(self.nbrows)]
        self.casesState = [[False for _2 in range(self.nbcols)] for _ in range(self.nbrows)]
        _ = 0
        while _ < self.nbBombs:
            i, j = randrange(self.nbrows), randrange(self.nbcols)
            if self.board[i][j] != -1:
                self.board[i][j] = -1
                self.bombsPos.append((i, j))
                for n in neighbors((i, j), self.nbrows - 1, self.nbcols - 1):
                    if self.board[n[0]][n[1]] != -1:
                        self.board[n[0]][n[1]] += 1
                _ += 1

        # affichage du plateau
        self.cnv.configure(width=self.boxSize * self.nbcols, height=self.boxSize * self.nbrows)
        for i in range(self.nbrows):
            for j in range(self.nbcols):
                tag = "(%d,%d)" % (i, j)
                self.cnv.create_image(j * self.boxSize, i * self.boxSize, image=self.imgDef, tag=tag, anchor="nw")

    def changeDifficulty(self, difficulty):
        """:type difficulty: Difficulty"""
        self.difficulty = difficulty
        self.reinitialisation()

    def changeNewGameButtonImage(self, image):
        self.newGameButton.configure(image=image)
        self.newGameButton.img = image

    def handlerLeftClick(self, event):
        if self.firstClick:
            self.firstClick = False
            self.playing = True
            self.time.configure(text="00:-1")
            self.timer()
        if self.playing:
            pos = getCase(event.x, event.y, self.boxSize)
            self.showCase(pos)

    def handlerRightClick(self, event):
        if self.playing:
            pos = getCase(event.x, event.y, self.boxSize)
            if not self.casesState[pos[0]][pos[1]]:
                nbBomb = int(self.nbBombDisplayer.cget("text"))
                for flagpos, id in self.flagsPos:
                    if flagpos == pos:
                        self.cnv.delete(id)
                        self.flagsPos.remove((flagpos, id))
                        self.nbBombDisplayer.configure(text=nbBomb + 1)
                        return
                self.flagsPos.append((pos, self.cnv.create_image(pos[1] * self.boxSize, pos[0] * self.boxSize,
                                                                 image=self.imgFlag, tag="f(%d%d)" % pos, anchor="nw")))
                self.nbBombDisplayer.configure(text=nbBomb - 1)
                if nbBomb == 1 and sorted([self.flagsPos[i][0] for i in range(self.nbBombs)]) == sorted(self.bombsPos):
                    self.win()

    def showCase(self, pos):
        if 0 <= pos[0] < self.nbrows and 0 <= pos[1] < self.nbcols and \
                pos not in [self.flagsPos[i][0] for i in range(len(self.flagsPos))]:
            if not self.casesState[pos[0]][pos[1]]:
                self.casesState[pos[0]][pos[1]] = True
                if self.board[pos[0]][pos[1]] == -1:
                    # le joueur à touché une bombe
                    self.cnv.itemconfig("(%d,%d)" % pos, image=self.imgBomb)
                    self.loose()
                elif self.board[pos[0]][pos[1]] == 0:
                    # le joueur à touché une case sans importance
                    self.cnv.itemconfig("(%d,%d)" % pos, image=self.imgNumbers[self.board[pos[0]][pos[1]]])
                    for n in neighbors(pos, self.nbrows, self.nbcols):
                        self.showCase(n)
                else:
                    # le joueur à touché un nombre
                    self.cnv.itemconfig("(%d,%d)" % pos, image=self.imgNumbers[self.board[pos[0]][pos[1]]])
                if self.playing and sum([line.count(False) for line in self.casesState]) == self.nbBombs:
                    self.win()
            else:
                if self.board[pos[0]][pos[1]] != -1 and self.board[pos[0]][pos[1]] != 0:
                    flagcmpt = 0
                    ns = neighbors(pos, self.nbrows-1, self.nbcols-1)
                    for n in ns:
                        if n in [self.flagsPos[_][0] for _ in range(len(self.flagsPos))]:
                            flagcmpt += 1
                    if self.board[pos[0]][pos[1]] == flagcmpt:
                        self.showSurronding(ns)

    def showSurronding(self, poss):
        for pos in poss:
            if pos not in [self.flagsPos[i][0] for i in range(len(self.flagsPos))] and not self.casesState[pos[0]][pos[1]]:
                if self.board[pos[0]][pos[1]] == 0 or self.board[pos[0]][pos[1]] == -1:
                    self.showCase(pos)
                else:
                    self.cnv.itemconfig("(%d,%d)" % pos, image=self.imgNumbers[self.board[pos[0]][pos[1]]])
                    self.casesState[pos[0]][pos[1]] = True
        if self.playing and sum([line.count(False) for line in self.casesState]) == self.nbBombs:
            self.win()

    def loose(self):
        self.playing = False
        f = Font(size=25)
        self.cnv.create_text(int(self.cnv.cget("width")) // 2, int(self.cnv.cget("height")) // 2, text="BOOOOOO !",
                             font=f, fill="red")
        self.changeNewGameButtonImage(PhotoImage(file="img/smiley_loose.png"))

    def win(self):
        self.playing = False
        f = Font(size=40)
        self.cnv.create_text(int(self.cnv.cget("width")) // 2, int(self.cnv.cget("height")) // 2, text="GG !", font=f,
                             fill="red")
        self.changeNewGameButtonImage(PhotoImage(file="img/smiley_win.png"))

    def timer(self):
        if self.firstClick:  # correction d'un bug qui lance la fonction a cause du after
            return
        minutes, secondes = self.time.cget("text").split(":")
        minutes, secondes = int(minutes), int(secondes) + 1
        if secondes == 60:
            minutes += 1
            secondes = 0
        minutes, secondes = str(minutes), str(secondes)
        if len(minutes) == 1:
            minutes = '0' + minutes
        if len(secondes) == 1:
            secondes = '0' + secondes
        self.time.configure(text=minutes + ":" + secondes)
        if self.playing:
            self.time.after(1000, self.timer)
