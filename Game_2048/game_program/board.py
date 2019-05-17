import random

class Board:
    def __init__(self, size):
        self.size = size
        self.score = 0
        #print("interesting")
        l = [0 for x in range(self.size)]
        self.board= []                       #board 存储数字
        for x in range(self.size):
            self.board.append(l[:])
            
    def operation_down(self):                  #向下
        yes = False                            #yes 为true说明操作有效
        for i in range(self.size):
            visit = []
            for j in range(self.size - 2, -1, -1):
                for k in range(j, self.size-1):
                    if self.board[i][k+1] == 0:
                        if self.board[i][k] != 0:
                            yes = True
                            self.board[i][k+1] = self.board[i][k]
                            self.board[i][k] = 0
                    elif self.board[i][k+1] == self.board[i][k] and k+1 not in visit and k not in visit:
                        self.board[i][k+1] += 1
                        self.score += 1 << self.board[i][k+1] # 加分
                        self.board[i][k] = 0
                        visit.append(k+1)
                        yes = True
                    else :
                        break
        return yes
        
    def operation_up(self):                           #向上
        yes = False                                 #yes 为true说明操作有效
        for i in range(self.size):
            visit = []
            for j in range(1, self.size):
                for k in range(j, 0, -1):
                    if self.board[i][k-1] == 0:
                        if self.board[i][k] != 0:
                            yes = True
                            self.board[i][k-1] = self.board[i][k]
                            self.board[i][k] = 0
                    elif self.board[i][k] == self.board[i][k-1] and k not in visit and k-1 not in visit:
                        self.board[i][k-1] += 1
                        self.score += 1 << self.board[i][k-1] # 加分
                        self.board[i][k] = 0
                        visit.append(k-1)
                        yes = True
                    else :
                        break
        return yes
    def operation_left(self):
        yes = False
        for j in range(self.size):
            visit = []
            for i in range(1, self.size):
                for k in range(i, 0, -1):
                    if self.board[k-1][j] == 0:
                        if self.board[k][j] != 0:
                            yes = True
                            self.board[k-1][j] = self.board[k][j]
                            self.board[k][j] = 0
                    elif self.board[k][j] == self.board[k-1][j] and k not in visit and k-1 not in visit:
                        self.board[k-1][j] += 1
                        self.score += 1 << self.board[k-1][j] # 加分
                        self.board[k][j] = 0
                        visit.append(k-1)
                        yes = True
                    else :
                        break
        return yes
        
    def operation_right(self):
        yes = False
        for j in range(self.size):
            visit = []
            for i in range(self.size - 2, -1, -1):
                for k in range(i, self.size-1):
                    if self.board[k+1][j] == 0:
                        if self.board[k][j] != 0:
                            yes = True
                            self.board[k+1][j] = self.board[k][j]
                            self.board[k][j] = 0
                    elif self.board[k+1][j] == self.board[k][j] and k+1 not in visit and k not in visit:
                        self.board[k+1][j] += 1
                        self.score += 1 << self.board[k+1][j] # 加分
                        self.board[k][j] = 0
                        visit.append(k+1)
                        yes = True
                    else :
                        break
        return yes 
    def is_continue(self):
        for i in range(self.size):
            for j in range(self.size):
                if j + 1 in range(self.size) and self.board[i][j]==self.board[i][j+1] or self.board[i][j]==0:
                    return True
                if i + 1 in range(self.size) and self.board[i+1][j]==self.board[i][j]:
                    return True
                
        return False
        
    def create_new_num(self):                   #随机创建新的数，当表盘满的时候会失败，结合上下左右操作yes使用
        random.seed()
        zero_or_one = random.randint(0,4)     #因为2048有时产生2，有时产生4, 2的概率大
        new_num = 1
        if zero_or_one == 0:
            new_num = 2
        zero_num = 0                            #统计0的个数
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    zero_num += 1
        index = random.randint(0, zero_num-1)       #根据0的个数随机产生一个位置，插上新数字
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0 and index == 0 :
                    self.board[i][j] = new_num
                    return 
                elif self.board[i][j] == 0:
                    index -= 1
        
    def get_points(self):                   #分数，表盘数字之和（废弃）
        point = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    point += 2 ** self.board[i][j]
        return point


