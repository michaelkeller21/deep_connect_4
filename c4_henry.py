class Board:
    def __init__(self):
        self.grid = np.array([[0,0,0,0,0,0],
                             [0,0,0,0,0,0],
                             [0,0,0,0,0,0],
                             [0,0,0,0,0,2],
                             [0,0,0,0,1,1],
                             [0,0,0,2,1,0],
                             [2,0,2,1,0,0],
                             ])

        self.full = np.array([False, False, False, False, False, False, False])
        self.w, self.h = self.grid.shape
        self.consecutive = 4

    def fill_col(self, col_idx, val):
        idx = [i for i, pos in enumerate(self.grid[col_idx][::-1]) if not pos]
        if idx:
            self.grid[col_idx][self.h - idx.pop() - 1] = val

    def move(self, col_idx, player):
        if not self.full[col_idx]:
            self.fill_col(col_idx, player)

        self.check_state()
    
    def is_win(self):
      for player in [1,2]:

        # testing vertically
        for col in self.grid:
          for idx in range(self.w - self.consecutive):
            if (col[idx:idx + self.consecutive] == player).all():
              print("vert")
              return player

        # testing horizontally
        for col in self.grid.T:
          for idx in range(self.w - self.consecutive):
            if (col[idx:idx + self.consecutive] == player).all():
              print("hori")
              return player 

        # testing diagonals
        for k in range(-3, 3):
          for idx in range(self.h - self.consecutive):

            rl_diag = np.diag(self.grid, k=k)[idx:idx + self.consecutive]
            lr_diag = np.diag(np.fliplr(self.grid), k=k)[idx:idx + self.consecutive]

            if (rl_diag == player).all() or (lr_diag == player).all()\
            and len(rl_diag) == self.consecutive:
              print("dia")
              return player

    def check_state(self):
      for i, col in enumerate(self.grid):
        if (col != 0).all():
          self.full[i] = True

      res = self.is_win()
      if res:
        print(res)
          

    def render(self):
      sns.heatmap(np.rot90(self.grid), linewidth=1, vmin=0, vmax=2)

    def simulate(self):
      while not self.full.all():
        self.move(randrange(0, 7), 1)
        self.move(randrange(0, 7), 2)

      self.render()
      print(self.is_win())
