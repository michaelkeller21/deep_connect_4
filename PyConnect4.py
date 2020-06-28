import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from random import randrange, choice, random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from copy import deepcopy
from tensorflow.keras.optimizers import Adam

def fill_col(grid, col_idx, val):
  h = 6
  idx = [i for i, pos in enumerate(grid[col_idx][::-1]) if not pos]
  if idx:
    grid[col_idx][h - idx.pop() - 1] = val

  return grid

def check_win(grid):
  consecutive = 4
  w, h = 7, 6

  for player in [1,2]:

    # testing vertically
    for col in grid:
      for idx in range(h - consecutive + 1):
        if (col[idx:idx + consecutive] == player).all():
          print("vert", player)
          return player

    # testing horizontally
    for col in grid.T:
      for idx in range(w - consecutive + 1):
        if (col[idx:idx + consecutive] == player).all():
          print("hori", player)
          return player 

    # testing diagonals
    for k in range(-3, 3):
      for idx in range(h - consecutive):

        rl_diag = np.diag(grid, k=k)[idx:idx + consecutive]
        lr_diag = np.diag(np.fliplr(grid), k=k)[idx:idx + consecutive]

        if (rl_diag == player).all() or (lr_diag == player).all()            and len(rl_diag) == consecutive:
          print("dia", player)
          return player

def q_learn(reward, predictions, decay=0.5):
  output = deepcopy(predictions)[::-1]
  q_reward = reward
  for pred, move in output:
    move_index =  np.unravel_index(move, pred.shape)
    pred[ move_index ] = np.clip(pred[ move_index ] + q_reward, 0, 1)
    q_reward *= decay

  return [m[0] for m in output]

class Board:
  def __init__(self, render):
    self.grid = np.zeros((7,6))
    self.history = []
    self.full = np.array([False, False, False, False, False, False, False])
    self.w, self.h = self.grid.shape
    self.consecutive = 4
    self.players = [-1, 1]
    self.render = render
    self.turn = self.players[0]
    self.end = False
    self.opponent_method = self.random_move

  def reset_board(self):
    self.grid = np.zeros((7,6))
    self.full = np.array([False, False, False, False, False, False, False])
    self.end = False
    self.history = []
    self.turn = -1

  def available_moves(self):
    return np.where(self.full == False)[0]

  def fill_col(self, col_idx, val):
    idx = [i for i, pos in enumerate(self.grid[col_idx][::-1]) if not pos]
    if idx:
      self.grid[col_idx][self.h - idx.pop() - 1] = val
  
  def check_win(self):
    for player in self.players:

      # testing vertically
      for col in self.grid:
        for idx in range(self.h - self.consecutive + 1):
          if (col[idx:idx + self.consecutive] == player).all():
            print("vert", player)
            return player

      # testing horizontally
      for col in self.grid.T:
        for idx in range(self.w - self.consecutive + 1):
          if (col[idx:idx + self.consecutive] == player).all():
            print("hori", player)
            return player 

      # testing diagonals
      for k in range(-3, 3):
        for idx in range(self.h - self.consecutive):

          rl_diag = np.diag(self.grid, k=k)[idx:idx + self.consecutive]
          lr_diag = np.diag(np.fliplr(self.grid), k=k)[idx:idx + self.consecutive]

          if (rl_diag == player).all() or (lr_diag == player).all()              and len(rl_diag) == self.consecutive:
            print("dia", player)
            return player

  def check_full(self):
    for idx, col in enumerate(self.grid):
      if (col != 0).all():
        self.full[idx] = True

  def move(self, col_idx, player):
    if self.available_moves().any() and self.turn == player:
      self.fill_col(col_idx, player)
      self.turn = player * -1
    else: print("invalid move attempted or out of order move attempted")


  def random_move(self, grid):
    for col_idx, col in enumerate(grid):
      grid = deepcopy(grid)
      grid = fill_col(grid, col_idx, self.turn)
      if check_win(grid):
        return col_idx, _
      else:
        return choice(self.available_moves()), _

  def step(self, move):
    self.check_full()
    self.history.append((self.grid, move))

    self.move(move, -1)
    reward = 0

    if self.check_win() == -1:
      print("first player won")
      reward = 1
      self.end = True

    elif not self.available_moves().any():
      print("first player ended match")
      reward = 0.5
      self.end = True
    
    if self.end:
      return reward, self.grid

    # other players turn
    move, pred = self.opponent_method(self.grid)

    self.move(move, 1)
    self.check_full()

    if self.check_win() == 1:
      print("second player wins")
      reward = -2
      self.end = True

    if not self.available_moves().any():
      print("second player ended game")
      reward = 0.5
      self.end = True
    
    return reward, self.grid

  def render_board(self):
    if self.render:
      sns.heatmap(np.rot90(self.grid), linewidth=1, vmin=-1, vmax=1)
      plt.show()

  def simulate(self, agent, opponent=None, n=1, epsilon=0.3):
    memory = []
    if opponent:
      self.opponent_method = opponent.decide_move

    for i in range(n):
      print(f"game {i}")
      predictions = []
      while self.available_moves().any() and not self.end:

        move, pred = agent.decide_move(self.grid)
        if random() < epsilon:
          move = choice(self.available_moves())
    
        predictions.append([pred, move])
        reward, state = self.step(move)
        self.render_board()

      # q learning update
      updated_q = q_learn(reward, predictions, decay=0.1)

      for j in range(len(self.history)):
        memory.append((self.history[j], updated_q[j], predictions[j]))
      self.reset_board()
    return memory

class Agent:
  def __init__(self, id):
    self.id = id
    self.model = self.create_model()

  def decide_move(self, grid, valid=True):
    model_input = np.zeros([1,7,6,2])

    model_input[0,:,:,0] = grid == 1
    model_input[0,:,:,1] = grid == 2
    
    pred = np.squeeze(self.model.predict(model_input))

    if valid:
      invalid = [i for i, col in enumerate(grid) if np.all(col)]
      for idx in invalid:
        pred[idx] = 0

    return pred.argmax(), pred

  def create_model(self):
    adam = Adam(lr=0.001)
    model = Sequential()
    model.add(Flatten(input_shape=[7,6,2]))
    model.add(Dense(84, activation='relu'))
    model.add(Dense(42, activation='relu'))
    model.add(Dense(21, activation='relu'))     
    model.add(Dense(7, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=adam)    
    return model

b = Board(render=False)
b.reset_board()

a1 = Agent(1)
a2 = Agent(2)

memory = []
memory = b.simulate(a1, opponent=a2, n=10000, epsilon=.9)

_X = np.array([m[0][0] for m in memory])
X = np.zeros([*_X.shape,2])

X[:,:,:,0] = (_X == 1)
X[:,:,:,1] = (_X == 2)

y = np.array([m[1] for m in memory])

print(X.shape, y.shape)

hist = a1.model.fit(X, y, epochs=100, batch_size=64)

b = Board(render=False)

while not b.end and b.available_moves().any():
  move, pred = a1.decide_move(b.grid, valid=True)
  print(pred)
  b.move(move, b.turn)
  b.render_board()

  if not b.end and b.available_moves().any():
    move = int(input())
    if move not in b.available_moves():
      print("column is full")
      move = int(input())
    b.move(move, b.turn)
    b.render_board()
  else:
    b.end = True