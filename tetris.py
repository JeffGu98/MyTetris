import sys
import os
import json
import random
import pygame


# 游戏配置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

SIDE_PANEL_WIDTH = 220
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT + 60

TOP_LEFT_X = 20
TOP_LEFT_Y = 20

# 将高分文件放在用户主目录，避免打包后写入 .app 目录权限问题
HIGHSCORE_FILE = os.path.expanduser('~/.tetris_highscore.json')

# Hold 区域位置（可调整）
HOLD_PANEL_X = TOP_LEFT_X + PLAY_WIDTH + 30
HOLD_PANEL_Y = TOP_LEFT_Y + 460

# 形状定义（7 种俄罗斯方块）
S = [
	['.....',
	 '.....',
	 '..00.',
	 '.00..',
	 '.....'],
	['.....',
	 '..0..',
	 '..00.',
	 '...0.',
	 '.....']
]

Z = [
	['.....',
	 '.....',
	 '.00..',
	 '..00.',
	 '.....'],
	['.....',
	 '..0..',
	 '.00..',
	 '.0...',
	 '.....']
]

I = [
	['..0..',
	 '..0..',
	 '..0..',
	 '..0..',
	 '.....'],
	['.....',
	 '0000.',
	 '.....',
	 '.....',
	 '.....']
]

O = [
	['.....',
	 '.....',
	 '.00..',
	 '.00..',
	 '.....']
]

J = [
	['.....',
	 '.0...',
	 '.000.',
	 '.....',
	 '.....'],
	['.....',
	 '..00.',
	 '..0..',
	 '..0..',
	 '.....'],
	['.....',
	 '.....',
	 '.000.',
	 '...0.',
	 '.....'],
	['.....',
	 '..0..',
	 '..0..',
	 '.00..',
	 '.....']
]

L = [
	['.....',
	 '...0.',
	 '.000.',
	 '.....',
	 '.....'],
	['.....',
	 '..0..',
	 '..0..',
	 '..00.',
	 '.....'],
	['.....',
	 '.....',
	 '.000.',
	 '.0...',
	 '.....'],
	['.....',
	 '.00..',
	 '..0..',
	 '..0..',
	 '.....']
]

T = [
	['.....',
	 '..0..',
	 '.000.',
	 '.....',
	 '.....'],
	['.....',
	 '..0..',
	 '..00.',
	 '..0..',
	 '.....'],
	['.....',
	 '.....',
	 '.000.',
	 '..0..',
	 '.....'],
	['.....',
	 '..0..',
	 '.00..',
	 '..0..',
	 '.....']
]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [
	(48, 219, 91),   # S 绿色
	(255, 69, 58),   # Z 红色
	(10, 132, 255),  # I 蓝色
	(255, 214, 10),  # O 黄色
	(52, 199, 89),   # J 绿
	(255, 159, 10),  # L 橙
	(191, 90, 242)   # T 紫
]


class Piece:
	def __init__(self, x, y, shape):
		self.x = x
		self.y = y
		self.shape = shape
		self.color = SHAPE_COLORS[SHAPES.index(shape)]
		self.rotation = 0


def create_grid(locked_positions=None):
	if locked_positions is None:
		locked_positions = {}
	grid = [[(30, 30, 30) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
	for i in range(GRID_HEIGHT):
		for j in range(GRID_WIDTH):
			if (j, i) in locked_positions:
				grid[i][j] = locked_positions[(j, i)]
	return grid


def load_high_score():
	try:
		if os.path.exists(HIGHSCORE_FILE):
			with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
				data = json.load(f)
				return int(data.get('high_score', 0))
	except Exception:
		pass
	return 0


def save_high_score(score):
	try:
		with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
			json.dump({'high_score': int(score)}, f, ensure_ascii=False)
	except Exception:
		# 忽略写入失败，保证游戏不中断
		pass

def convert_shape_format(piece):
	positions = []
	shape = piece.shape[piece.rotation % len(piece.shape)]
	for i, line in enumerate(shape):
		for j, column in enumerate(line):
			if column == '0':
				positions.append((piece.x + j - 2, piece.y + i - 4))
	return positions


def valid_space(piece, grid):
	accepted_positions = [(j, i) for i in range(GRID_HEIGHT) for j in range(GRID_WIDTH) if grid[i][j] == (30, 30, 30)]
	formatted = convert_shape_format(piece)
	for pos in formatted:
		x, y = pos
		if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
			return False
		if y >= 0 and (x, y) not in accepted_positions:
			return False
	return True


def check_lost(positions):
	for _, y in positions:
		if y < 1:
			return True
	return False


def get_shape():
	return Piece(GRID_WIDTH // 2 + 1, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color, offset_y=0):
	font = pygame.font.SysFont('arial', size, bold=True)
	label = font.render(text, True, color)
	surface.blit(
		label,
		(TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2,
		 TOP_LEFT_Y + PLAY_HEIGHT // 2 - label.get_height() // 2 + offset_y)
	)


def clear_rows(grid, locked):
	cleared = 0
	for i in range(GRID_HEIGHT - 1, -1, -1):
		if (30, 30, 30) not in grid[i]:
			cleared += 1
			for j in range(GRID_WIDTH):
				try:
					del locked[(j, i)]
				except KeyError:
					pass
	if cleared > 0:
		# 将所有在被清除行之上的方块下移
		for key in sorted(list(locked.keys()), key=lambda k: k[1])[::-1]:
			x, y = key
			move_down = sum(1 for r in range(y + 1, GRID_HEIGHT) if all(grid[r][c] != (30, 30, 30) for c in range(GRID_WIDTH)))
			# 简化：逐行检查被清除行数
		# 更严谨的整体重建
		new_locked = {}
		for (x, y), color in locked.items():
			drop = 0
			for r in range(y + 1, GRID_HEIGHT):
				if (30, 30, 30) not in grid[r]:
					drop += 1
			new_locked[(x, y + drop)] = color
		locked.clear()
		locked.update(new_locked)
	return cleared


def draw_grid(surface, grid):
	# 背景框
	pygame.draw.rect(surface, (50, 50, 50), (TOP_LEFT_X - 3, TOP_LEFT_Y - 3, PLAY_WIDTH + 6, PLAY_HEIGHT + 6), 3)
	# 网格线
	for i in range(GRID_HEIGHT + 1):
		pygame.draw.line(surface, (40, 40, 40), (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
	for j in range(GRID_WIDTH + 1):
		pygame.draw.line(surface, (40, 40, 40), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def draw_next_shape(surface, piece):
	font = pygame.font.SysFont('arial', 22, bold=True)
	label = font.render('Next', True, (235, 235, 245))
	sx = TOP_LEFT_X + PLAY_WIDTH + 30
	sy = TOP_LEFT_Y + 40
	surface.blit(label, (sx, sy - 30))

	shape_format = piece.shape[piece.rotation % len(piece.shape)]
	for i, line in enumerate(shape_format):
		for j, column in enumerate(line):
			if column == '0':
				pygame.draw.rect(
					surface, piece.color,
					(sx + j * BLOCK_SIZE // 1.4, sy + i * BLOCK_SIZE // 1.4, BLOCK_SIZE // 1.4, BLOCK_SIZE // 1.4), 0
				)


def draw_hold_shape(surface, hold_shape):
	font = pygame.font.SysFont('arial', 22, bold=True)
	label = font.render('Hold', True, (235, 235, 245))
	sx = HOLD_PANEL_X
	sy = HOLD_PANEL_Y
	surface.blit(label, (sx, sy - 30))
	if not hold_shape:
		return
	# 使用默认旋转的第 0 帧绘制
	shape_format = hold_shape[0]
	color = SHAPE_COLORS[SHAPES.index(hold_shape)]
	for i, line in enumerate(shape_format):
		for j, column in enumerate(line):
			if column == '0':
				pygame.draw.rect(
					surface, color,
					(sx + j * BLOCK_SIZE // 1.4, sy + i * BLOCK_SIZE // 1.4, BLOCK_SIZE // 1.4, BLOCK_SIZE // 1.4), 0
				)


def draw_window(surface, grid, score=0, level=1, lines=0, high_score=0):
	surface.fill((18, 18, 18))
	# 标题
	font = pygame.font.SysFont('arial', 28, bold=True)
	label = font.render('Tetris', True, (235, 235, 245))
	surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2, 5))

	# 分数与信息
	info_font = pygame.font.SysFont('arial', 20)
	sx = TOP_LEFT_X + PLAY_WIDTH + 30
	sy = TOP_LEFT_Y + 140
	info = [
		f'Score: {score}',
		f'Best: {high_score}',
		f'Level: {level}',
		f'Lines: {lines}',
		'Controls:',
		'←/→: Move',
		'↑: Rotate',
		'↓: Soft drop',
		'Space: Hard drop',
		'C: Hold   P: Pause',
		'R: Restart  Q: Quit'
	]
	for idx, text in enumerate(info):
		lbl = info_font.render(text, True, (200, 200, 205))
		surface.blit(lbl, (sx, sy + idx * 24))

	# 绘制网格与块
	for i in range(GRID_HEIGHT):
		for j in range(GRID_WIDTH):
			color = grid[i][j]
			if color != (30, 30, 30):
				pygame.draw.rect(
					surface, color,
					(TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0
				)

	draw_grid(surface, grid)


def hard_drop(piece, grid):
	# 直接下落到最底部
	drop = 0
	while True:
		piece.y += 1
		if not valid_space(piece, grid):
			piece.y -= 1
			break
		drop += 1
	return drop


def score_for_lines(lines_cleared):
	return {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}.get(lines_cleared, 0)


def main(surface):
	locked_positions = {}
	grid = create_grid(locked_positions)

	current_piece = get_shape()
	next_piece = get_shape()
	hold_shape = None
	hold_used = False

	clock = pygame.time.Clock()
	fall_time = 0
	# 调快初始下落速度，缩短“出生到落下”的等待
	fall_speed = 0.35  # 初始下落间隔（秒）

	score = 0
	total_lines = 0
	level = 1
	paused = False
	high_score = load_high_score()

	left_repeat_timer = 0
	right_repeat_timer = 0
	down_repeat_timer = 0
	# 按下起始时间记录与长按阈值（秒）
	press_start = {}
	LONG_PRESS_THRESHOLD = 0.20

	running = True
	while running:
		grid = create_grid(locked_positions)
		dt = clock.tick(60) / 1000.0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit(0)
			if event.type == pygame.KEYDOWN:
				# 记录按下时间用于长按判定
				press_start[event.key] = pygame.time.get_ticks()
				if event.key == pygame.K_q:
					pygame.quit()
					sys.exit(0)
				if event.key == pygame.K_r:
					return 'restart'
				if event.key == pygame.K_p:
					paused = not paused
				if paused:
					continue
				if event.key == pygame.K_c:
					# Hold / 交换：仅在本回合未使用过 Hold 时允许
					if not hold_used:
						if hold_shape is None:
							# 首次 Hold：把当前方块存入 Hold，切到下一个方块
							hold_shape = current_piece.shape
							current_piece = next_piece
							next_piece = get_shape()
							# 放置到出生位置
							current_piece.x = GRID_WIDTH // 2 + 1
							current_piece.y = 0
							current_piece.rotation = 0
							# 如果出生位置不合法，尝试微调；失败则不执行 Hold
							if not valid_space(current_piece, grid):
								adjusted = False
								for dx in (-1, 1, -2, 2):
									current_piece.x += dx
									if valid_space(current_piece, grid):
										adjusted = True
										break
									current_piece.x -= dx
								if not adjusted:
									# 还原：取消首次 Hold（保持原状态）
									current_piece = Piece(GRID_WIDTH // 2 + 1, 0, hold_shape)
									# 由于取消，保持 hold_used=False 并清空 hold_shape
									hold_shape = None
									break
							else:
								hold_used = True
						else:
							# 交换：准备取出 Hold 的方块作为当前方块
							take_shape = hold_shape
							put_shape = current_piece.shape
							new_piece = Piece(GRID_WIDTH // 2 + 1, 0, take_shape)
							current_piece = new_piece
							hold_shape = put_shape
							hold_used = True
				if event.key == pygame.K_LEFT:
					current_piece.x -= 1
					if not valid_space(current_piece, grid):
						current_piece.x += 1
				elif event.key == pygame.K_RIGHT:
					current_piece.x += 1
					if not valid_space(current_piece, grid):
						current_piece.x -= 1
				elif event.key == pygame.K_DOWN:
					current_piece.y += 1
					if not valid_space(current_piece, grid):
						current_piece.y -= 1
				elif event.key == pygame.K_UP:
					current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
					if not valid_space(current_piece, grid):
						current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
				elif event.key == pygame.K_SPACE:
					gained = hard_drop(current_piece, grid)
					score += gained * 2
			if event.type == pygame.KEYUP:
				# 抬起时清除记录并重置对应重复计时器
				start = press_start.pop(event.key, None)
				if event.key == pygame.K_LEFT:
					left_repeat_timer = 0.0
				elif event.key == pygame.K_RIGHT:
					right_repeat_timer = 0.0

		keys = pygame.key.get_pressed()
		repeat_interval = 0.2  # 重复操作的时间间隔，单位秒

		left_repeat_timer += dt
		right_repeat_timer += dt
		down_repeat_timer += dt

		# 仅在超过长按阈值后触发左右重复移动
		left_held_ms = None
		right_held_ms = None
		if pygame.K_LEFT in press_start:
			left_held_ms = pygame.time.get_ticks() - press_start[pygame.K_LEFT]
		if pygame.K_RIGHT in press_start:
			right_held_ms = pygame.time.get_ticks() - press_start[pygame.K_RIGHT]

		if keys[pygame.K_LEFT] and (left_held_ms is not None and left_held_ms >= LONG_PRESS_THRESHOLD * 1000) and left_repeat_timer >= repeat_interval:
			current_piece.x -= 1
			if not valid_space(current_piece, grid):
				current_piece.x += 1
			left_repeat_timer = 0.0

		if keys[pygame.K_RIGHT] and (right_held_ms is not None and right_held_ms >= LONG_PRESS_THRESHOLD * 1000) and right_repeat_timer >= repeat_interval:
			current_piece.x += 1
			if not valid_space(current_piece, grid):
				current_piece.x -= 1
			right_repeat_timer = 0.0

		# 软降长按：仅当超过长按阈值后连续下移
		down_held_ms = None
		if pygame.K_DOWN in press_start:
			down_held_ms = pygame.time.get_ticks() - press_start[pygame.K_DOWN]
		if keys[pygame.K_DOWN] and (down_held_ms is not None and down_held_ms >= LONG_PRESS_THRESHOLD * 1000) and down_repeat_timer >= 0.04:
			current_piece.y += 1
			if not valid_space(current_piece, grid):
				current_piece.y -= 1
			down_repeat_timer = 0.0

		if paused:
			draw_window(surface, grid, score, level, total_lines, high_score)
			draw_text_middle(surface, 'Paused', 48, (250, 250, 255))
			pygame.display.update()
			continue

		fall_time += dt
		if fall_time >= fall_speed:
			fall_time = 0
			current_piece.y += 1
			if not valid_space(current_piece, grid):
				current_piece.y -= 1
				# 锁定到位
				for x, y in convert_shape_format(current_piece):
					if y > -1:
						locked_positions[(x, y)] = current_piece.color
				current_piece = next_piece
				next_piece = get_shape()
				hold_used = False  # 新方块生成后可再次使用 hold
				cleared = clear_rows(create_grid(locked_positions), locked_positions)
				if cleared:
					total_lines += cleared
					score += score_for_lines(cleared)
					# 提升关卡与速度：整体更快，间隔更短
					level = 1 + total_lines // 10
					fall_speed = max(0.06, 0.45 - (level - 1) * 0.06)
				# 更新最高分（即时保存）
				if score > high_score:
					high_score = score
					save_high_score(high_score)

		for x, y in convert_shape_format(current_piece):
			if y > -1:
				grid[y][x] = current_piece.color

		draw_window(surface, grid, score, level, total_lines, high_score)
		draw_next_shape(surface, next_piece)
		draw_hold_shape(surface, hold_shape)

		if check_lost([(x, y) for (x, y) in locked_positions.keys()]):
			draw_text_middle(surface, 'Game Over', 54, (255, 90, 90))
			pygame.display.update()
			pygame.time.delay(1600)
			return 'gameover'

		pygame.display.update()


def main_menu():
	pygame.init()
	pygame.display.set_caption('Tetris')
	surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

	while True:
		surface.fill((18, 18, 18))
		draw_text_middle(surface, 'Press Any Key', 44, (235, 235, 245), offset_y=-20)
		draw_text_middle(surface, 'Q: Quit  R: Restart', 22, (180, 180, 190), offset_y=30)
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit(0)
			if event.type == pygame.KEYDOWN:
				result = main(surface)
				if result == 'restart':
					continue
				else:
					# 返回菜单
					pass


if __name__ == '__main__':
	try:
		main_menu()
	except Exception as e:
		print('Error:', e)
		pygame.quit()
		sys.exit(1)

