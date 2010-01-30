import curses
import pylife

class LifeScreen:
  def redraw(self):
    self.screen.leaveok(1)
    h, w = self.screen.getmaxyx()
    self.screen.clear()
    cells = self.board.getAll(self.visibleRect())
    for x, y in cells:
      if x - self.offsetx == w - 1:
        self.screen.insch(y - self.offsety, x - self.offsetx, ord('*'))
      else:
        self.screen.addch(y - self.offsety, x - self.offsetx, ord('*'))
    self.showmem()
    self.screen.leaveok(0)
    self.showcursor()


  def __init__(self, screen, board):
    self.screen = screen
    self.board = board
    self.height, self.width = screen.getmaxyx()
    self.offsety, self.offsetx = -self.height / 2, -self.width / 2
    self.curx, self.cury = 0, 0
    self.steps = 0

  def visibleRect(self):
    return (self.offsetx, self.offsety,
            self.offsetx + self.width, self.offsety + self.height)

  def redraw(self):
    self.screen.leaveok(1)
    h, w = self.screen.getmaxyx()
    self.screen.clear()
    cells = self.board.getAll(self.visibleRect())
    for x, y in cells:
      if x - self.offsetx == w - 1:
        self.screen.insch(y - self.offsety, x - self.offsetx, ord('*'))
      else:
        self.screen.addch(y - self.offsety, x - self.offsetx, ord('*'))
    self.showmem()
    self.screen.leaveok(0)
    self.showcursor()

  def showmem(self):
    self.screen.addstr(0, 0, str(self.steps) + self.board.info())

  def showcursor(self):
    self.screen.move(self.cury - self.offsety, self.curx - self.offsetx)

  def update(self, x, y):
    if (self.curx >= self.offsetx
        and self.curx < self.offsetx + self.width
        and self.cury >= self.offsety
        and self.cury < self.offsety + self.height):
      if self.board.get(x, y):
        ch = ord('*')
      else:
        ch = ord(' ')
      self.screen.addch(y - self.offsety, x - self.offsetx, ch)

  def toggle(self):
    value = 1 - self.board.get(self.curx, self.cury)
    self.board.set(self.curx, self.cury, value)
    self.update(self.curx, self.cury)
    self.showmem()
    self.showcursor()

  def step(self, steps):
    if self.board.width() > 2 ** 28: self.collect()
    self.board.step(steps)
    self.steps = self.steps + steps
    self.redraw()
    self.showcursor()

  def bigstep(self):
    if self.steps == 0: self.step(1)
    else: self.step(self.steps)

  def keepcentered(self):
    maxx, maxy = self.curx - self.width / 4, self.cury - self.height / 4
    minx, miny = maxx - self.width / 2, maxy - self.height / 2
    offsetx = min(maxx, max(minx, self.offsetx))
    offsety = min(maxy, max(miny, self.offsety))
    if self.offsetx != offsetx or self.offsety != offsety:
      self.offsetx, self.offsety = offsetx, offsety
      self.redraw()

  def clear(self):
    self.board.clear()
    self.steps = 0
    self.redraw()

  def collect(self):
    self.board.collect()
    self.redraw()

  def move(self, key):
    if key == curses.KEY_UP or key == ord('k'): self.cury = self.cury - 1
    elif key == curses.KEY_DOWN or key == ord('j'): self.cury = self.cury + 1
    elif key == curses.KEY_LEFT or key == ord('h'): self.curx = self.curx - 1
    elif key == curses.KEY_RIGHT or key == ord('l'): self.curx = self.curx + 1
    else: return False
    self.keepcentered()
    self.showcursor()
    return True

  def find(self):
    cells = self.board.getAll()
    if len(cells) > 0:
      self.curx, self.cury = cells[0]
      self.keepcentered()
      self.showcursor()

  def main(self):
    self.redraw()
    while 1:
      key = self.screen.getch()
      if key == ord('.'): self.toggle()
      elif self.move(key): pass
      elif key == ord(' '): self.step(1)
      elif key == ord('s'): self.bigstep()
      elif key == ord('r'): self.redraw()
      elif key == ord('C'): self.clear()
      elif key == ord('f'): self.find()
      elif key == ord('c'): self.collect()
      elif key == ord('q'): break

def main(stdscr):
  board = pylife.LifeBoard()
  screen = LifeScreen(stdscr, board)
  screen.main()

curses.wrapper(main)
