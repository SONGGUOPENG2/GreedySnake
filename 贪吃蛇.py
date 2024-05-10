from time import sleep
import pygame
import random
from collections import deque

# 游戏界面大小
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
GRID_SIZE = 9  #食物大小
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
sleeper = 1  # 睡眠时间
speeder = 8000  # 速度
lengther = 300  # 初始长度

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (9, 133, 255)  # 新增的蓝色
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)

# 初始化pygame
pygame.init()

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SONGGUOPENG的贪吃蛇游戏')

# 游戏得分
score = 0

# 蛇类
class Snake:
    def __init__(self, length):
        self.head = [length, 4]
        self.body = []
        for ds in range(length, 1, -1):
            self.body.append([ds, 4])
        self.direction = "RIGHT"

    def move(self):
        if self.direction == "UP":
            self.head[1] -= 1
        elif self.direction == "DOWN":
            self.head[1] += 1
        elif self.direction == "LEFT":
            self.head[0] -= 1
        elif self.direction == "RIGHT":
            self.head[0] += 1

        # 添加新头部
        self.body.insert(0, list(self.head))

        # 删除尾部
        if len(self.body) > 1:
            self.body.pop()

        # 超出屏幕边界处理
        if self.head[0] < 0:
            self.head[0] = GRID_WIDTH - 1
        elif self.head[0] >= GRID_WIDTH:
            self.head[0] = 0
        if self.head[1] < 0:
            self.head[1] = GRID_HEIGHT - 1
        elif self.head[1] >= GRID_HEIGHT:
            self.head[1] = 0

    def change_direction(self, direction):
        if direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
        elif direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"

    def check_collision(self):
        if self.head in self.body[1:]:
            return True
        return False

    def eat(self, food):
        if self.head == food.position:
            self.body.append(food.position)
            food.generate_position()
            global score
            score += 1

    def draw(self):
        for i, segment in enumerate(self.body):
            color = PINK  # 默认颜色为粉红色
            if i < 2:  # 修改头部两个方块的颜色为蓝色
                color = BLUE
            pygame.draw.rect(
                screen,
                color,
                (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )


# 食物类
class Food:
    def __init__(self):
        self.position = [10, 10]

    def generate_position(self):
        while True:
            new_position = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
            if new_position not in snake.body:
                self.position = new_position
                break

    def draw(self):
        pygame.draw.rect(
            screen,
            RED,
            (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
        )


# 创建蛇和食物对象
snake_length = lengther  # 设置贪吃蛇的初始长度
snake = Snake(snake_length)
food = Food()

# 记录蛇的身体位置
snake_positions = set(tuple(pos) for pos in snake.body)


# 广度优先遍历函数，寻找吃到食物的路径
def bfs(snake, food):
    start = tuple(snake.head)
    queue = deque([(start, [])])
    visited = set(start)

    while queue:
        curr_pos, path = queue.popleft()
        if curr_pos == tuple(food.position):
            return path
        for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
            next_pos = move(curr_pos, direction)
            if next_pos not in visited and is_valid_position(next_pos):
                queue.append((next_pos, path + [direction]))
                visited.add(next_pos)
    return []


# 广度优先遍历函数，寻找最佳逃离路径
def bfs_escape(snake):
    start = tuple(snake.head)
    queue = deque([(start, [])])
    visited = set(start)

    while queue:
        curr_pos, path = queue.popleft()
        for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
            next_pos = move(curr_pos, direction)
            if next_pos not in visited and is_valid_position(next_pos):
                queue.append((next_pos, path + [direction]))
                visited.add(next_pos)
                if next_pos not in snake_positions:
                    return path + [direction]
    return []


# 移动函数，根据当前位置和方向返回下一个位置
def move(curr_pos, direction):
    if direction == "UP":
        return (curr_pos[0], curr_pos[1] - 1)
    elif direction == "DOWN":
        return (curr_pos[0], curr_pos[1] + 1)
    elif direction == "LEFT":
        return (curr_pos[0] - 1, curr_pos[1])
    elif direction == "RIGHT":
        return (curr_pos[0] + 1, curr_pos[1])


# 检查位置是否合法
def is_valid_position(pos):
    if (
        pos[0] < 0
        or pos[0] >= GRID_WIDTH
        or pos[1] < 0
        or pos[1] >= GRID_HEIGHT
    ):
        return False
    if pos in snake_positions:
        return False
    return True


# 游戏主循环
clock = pygame.time.Clock()
running = True

while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 小蛇自动运行，使用广度优先遍历算法
    path = bfs(snake, food)
    if path:
        next_direction = path[0]
        snake.change_direction(next_direction)
    else:
        # 如果没有找到路径，则计算最佳逃离路径
        escape_path = bfs_escape(snake)
        if escape_path:
            next_direction = escape_path[0]
            snake.change_direction(next_direction)

    # 更新蛇的身体位置
    snake_positions.clear()
    snake_positions.update(tuple(pos) for pos in snake.body)

    # 蛇移动
    snake.move()

    # 检查碰撞
    if snake.check_collision():
        running = False

    # 检查是否吃到食物
    snake.eat(food)

    # 渲染背景
    screen.fill(WHITE)

    # 绘制蛇和食物
    snake.draw()
    food.draw()

    # 显示得分
    font = pygame.font.Font(None, 36)
    text = font.render("SONGGUOPENG's Score: {}".format(score), True, BLACK)
    screen.blit(text, (10, 10))

    # 刷新屏幕
    pygame.display.flip()

    # 控制游戏速度
    clock.tick(speeder)

# 退出游戏
sleep(sleeper)
pygame.quit()