from .board import Board
#from scoreboard import Scoreboard
import random
import json

def printf(board):
    for x in board:
        print(x)

class Game:
    # state: Operating, Moving, Over
    def __init__(self, name='null', width=400, height=600, size=4):
        self.name = name
        #self.test_board()
        self.board = Board(size)
        self.board.create_new_num()
        self.board.create_new_num()
        self.blocks = self.board.board
        #self.display = Display(name, width, height, size, self.blocks)
        self.activated = True
        self.state = 1 # 0: moving, 1: can move, 2: game over
        self.map_size = size
        self.dialog = None

    def board4print(self):
        return [[(1 << self.board.board[w][h])\
                for w in range(self.map_size)]\
                for h in range(self.map_size)]

    def to_json(self):
        out = {
            'size':self.map_size, 
            'board':str(self.board4print()), 
            'state':self.state,
            'score':self.board.score,
        }
        return json.dumps(out)

    def to_json_with_last_move(self, direction):
        out = {
            'size':self.map_size, 
            'board':self.board4print(), 
            'state':self.state,
            'score':self.board.score,
            'direction':direction,
        }
        return json.dumps(out, ensure_ascii=False)
    '''
    def run(self):
        print('Runing')
        direction = 0
        key_released = True
        while self.activated:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    print('Quit')
                    self.activated = False
                    return
            if self.state == 2:
                continue
            self.state = 0
            key = pygame.key.get_pressed()
            if not self.display.moving and key_released:
                key_released = False
                self.state = 1
                direction = self.check_direction(key)
                if direction == 0:
                    self.state = 0
                    key_released = True
                self.display.updateScore(self.board.score)
                self.move(direction)
            if not self.display.moving and self.check_direction(key) == 0:
                key_released = True
            self.display.update(self.state, direction, self.board.board)
            if not self.board.is_continue() and self.dialog is None and direction == 0:  #判断能否移动，且是否已经有排行榜
                self.over()
    '''
    def move(self, direction):
        if direction == 4: # Right
            if self.board.operation_right():   #返回True才会生成新数
                self.board.create_new_num()
        elif direction == 3: # Left
            if self.board.operation_left():
                self.board.create_new_num()
        elif direction == 1: # Up
            if self.board.operation_up():
                self.board.create_new_num()
        elif direction == 2: # Down
            if self.board.operation_down():
                self.board.create_new_num()
        #print(self.board.get_points())
        #printf(self.board.board)

    def score_board(self):
        try:
            if self.dialog:
                self.dialog.close()
            self.dialog = Scoreboard(size_str=str(self.map_size), use_zip=True, write=True, name0=self.name, score0=self.board.score)
            self.dialog.show()
        except Exception as e:
            print("Scoreboard error.")
            print(str(e))

    def check_direction(self, key):
        if key[pygame.K_UP]:
            return 1
        elif key[pygame.K_DOWN]:
            return 2
        elif key[pygame.K_LEFT]:
            return 3
        elif key[pygame.K_RIGHT]:
            return 4
        else:
            return 0

    def test_board(self):
        '''测试用，实际没有用的函数'''
        self.blocks = []
        for i in range(size):
            self.blocks.append([0] * size)
        x0 = random.randrange(size)
        y0 = random.randrange(size)
        z0 = random.randrange(1, 3)
        self.blocks[x0][y0] = z0
        x1 = random.randrange(size)
        y1 = random.randrange(size)
        while x1 == x0 and y1 == y0:
            x1 = random.randrange(size)
            y1 = random.randrange(size)
        z1 = random.randrange(1, 3)
        self.blocks[x1][y1] = z1
        #'''test
        print(self.blocks)
        #'''

    def over(self):
        print('Game Over')
        self.state = 2
        #self.display.set_gameover_display()
        #self.score_board()

    def quit(self):
        pass
        #self.display.quit()
    
