import numpy as np
import random

def initialize_board():
    board=np.zeros((6, 7))
    return board

def p1_move(board):
    move=random.randint(1, 7)
    for i in range(6):
        if board[5-i][move-1]==0:
            board[5-i][move-1]=1
            break
        else:
            continue
    return board

def p2_move(board):
    move=random.randint(1, 7)
    for i in range(6):
        if board[5-i][move-1]==0:
            board[5-i][move-1]=2
            break
        else:
            continue
    return board

def check_win(board):
    win=False
    p1_win=False
    p2_win=False
    for i in range(3):
        for j in range(4):
            if np.all(board[i:i+4, j]==1) or np.all(board[j:j+4, i]==1) or np.all(np.array([board[i][j], board[i+1][j+1], board[i+2][j+2], board[i+3][j+3]])==1):
                p1_win=True
                print('Player 1 wins!')
                return p1_win
            elif np.all(board[i:i+4, j]==2) or np.all((board[j:j+4, i])==2) or np.all(np.array([board[i][j], board[i+1][j+1], board[i+2][j+2], board[i+3][j+3]])==2):
                p2_win=True
                print('Player 2 wins!')
                return p2_win            
    return win

def check_draw(board):
    draw=False
    if np.all(board)!=0:
        draw=True
        print('Draw!')
    return draw

board=initialize_board()
print(board)

while not check_win(board) and not check_draw(board):
    board=p1_move(board)
    print(board)
    if check_win(board) or check_draw(board):
        break
    board=p2_move(board)
    print(board)
