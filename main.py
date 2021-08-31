import pygame as pg

#import gui objects
import sys
sys.path.insert(1, '/Python Projects/GuiObjects')

from GUIObjects import *

width, height = 1200, 900

screen = pg.display.set_mode((width, height))

fps = 60

t = 0.0
step = 0.01

down = False
up = False
reachedMax = False
reachedMin = True
draw = True

allPoints = []
curves = []

class QuadraticBeizerCurve:
	def __init__(self, positions, radius, color, drawColor):
		self.points = []

		self.points.append(Point(positions[0], 12, color, connection=None))
		for pos in positions[1:]:
			self.points.append(Point(pos, 12, color, connection=self.points[-1]))

		self.a = Point(positions[0], 12, drawColor, trace = False, connection = None)
		self.b = Point(positions[0], 12, drawColor, trace = False, connection = self.a)
		self.c = Point(positions[0], 12, drawColor, trace = False, connection = self.b)

		self.d = Point(positions[0], 12, drawColor, trace = False, connection = None)
		self.e = Point(positions[0], 12, drawColor, trace = False, connection = self.d)

		self.drawingPoint = Point(positions[0], 12, drawColor, trace = True)

		curves.append(self)

	def Lerp(self, p1, p2, t):
		return ((1 - t) * p1[0] + t * p2[0], (1 - t) * p1[1] + t * p2[1])

	def Quadratic(self, p1, p2, p3, p4, t):
		a = self.Lerp(p1.pos, p2.pos, t)
		self.a.pos = a
		b = self.Lerp(p2.pos, p3.pos, t)
		self.b.pos = b
		c = self.Lerp(p3.pos, p4.pos, t)
		self.c.pos = c

		d = self.Lerp(a, b, t)
		self.d.pos = d
		e = self.Lerp(b, c, t)
		self.e.pos = e

		return self.Lerp(d, e, t)

	def Update(self, pos1, pos2):
		self.p1.pos = pos1
		self.p2.pos = pos2


class Line:
	def __init__(self, pos1, pos2, color):
		self.pos1 = pos1
		self.pos2 = pos2
		self.color = color

	def Draw(self):
		pg.draw.line(screen, self.color, self.pos1, self.pos2)


class Point:
	def __init__(self, pos, radius, color, connection=None, connectionColor=lightGray, trace=False):
		self.pos = pos
		self.radius = radius
		self.color = color
		self.connectionColor = connectionColor
		self.connection = connection
		self.trace = trace

		self.gotFirstPos = True
		self.gotSecondPos = False
		self.firstPos = self.pos
		self.secondPos = self.pos
		self.max = False
		self.clicked = False
		self.draw = True

		self.lines = []

		allPoints.append(self)

	def Draw(self):
		pg.draw.circle(screen, self.color, self.pos, self.radius)
		pg.draw.circle(screen, black, self.pos, 4)
		if self.connection != None:
			pg.draw.line(screen, self.connectionColor, self.pos, self.connection.pos, 4)

	def Update(self):
		if self.trace and not self.max and self.draw:
			if not self.gotFirstPos:
				self.firstPos = self.secondPos
				self.gotFirstPos = True

			elif self.gotFirstPos and not self.gotSecondPos:
				self.secondPos = self.pos
				self.gotSecondPos = True

				self.lines.append(Line(self.firstPos, self.secondPos, self.color))
				self.gotFirstPos = False
				self.gotSecondPos = False

		pg.draw.circle(screen, self.color, self.pos, 2)

		for line in self.lines:
			line.Draw()

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if pg.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2).collidepoint(pg.mouse.get_pos()):
					self.clicked = True
					self.draw = False

		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				if pg.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2).collidepoint(pg.mouse.get_pos()):
					self.clicked = False

				self.draw = True
				self.gotFirstPos = True
				self.gotSecondPos = False
				self.firstPos = self.pos
				self.secondPos = self.pos
				self.lines = []
				self.max = False

		if self.clicked:
			self.pos = pg.mouse.get_pos()


Label(screen, "t value", (0, 0, 500, 20), (lightBlack, darkWhite), f"T: {str(t)}", ("arial", 16, white))

Button(screen, "step up", (0, height // 2 - 80, 90, 80), (lightBlack, darkWhite, lightRed), "Step Up", ("arial", 16, white), isHoldButton=True)
Label(screen, "step value",  (0, height // 2, 90, 80), (lightBlack, darkWhite), f"Step: {str(step)}", ("arial", 16, white))
Button(screen, "step down", (0, height // 2 + 80, 90, 80), (lightBlack, darkWhite, lightRed), "Step Down", ("arial", 16, white), isHoldButton=True)

QuadraticBeizerCurve([(100, 800), (200, 200), (800, 200), (900, 800)], 12, lightRed, lightBlue)


def DrawLoop():
	screen.fill(darkGray)

	for point in allPoints:
		point.Update()
		if draw:
			point.Draw()

		# if reachedMax:
		# 	point.max = True

	DrawGui()

	pg.display.update()


def Update():
	global t, reachedMax, reachedMin, step
	for l in allLabels:
		if l.name == "t value":
			l.UpdateText(f"T: {str(t)}", ("arial", 16, white))

		if l.name == "step value":
			l.UpdateText(f"Step: {str(step)}", ("arial", 16, white))

	for button in allButtons:
		if button.name == "step up" and button.active:
			step = min(round(step + 0.001, 3), 1)
			# button.active = False
		if button.name == "step down" and button.active:
			step = max(round(step - 0.001, 3), 0.001)
			# button.active = False

	if down and not up:
		t = max(t - step, 0.0)
	elif not down and up:
		t = min(1.0, t + step)
	elif down and up:
		if reachedMax and not reachedMin:
			t = max(t - step, 0.0)
		elif not reachedMax and reachedMin:
			t = min(1.0, t + step)

		if t == 1:
			reachedMax = True
			reachedMin = False
		elif t == 0:
			reachedMax = False
			reachedMin = True


	for curve in curves:
		curve.drawingPoint.pos = curve.Quadratic(curve.points[0], curve.points[1], curve.points[2], curve.points[3], t)


while running:
	clock.tick_busy_loop(fps)
	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

			if event.key == pg.K_1:
				down = True
				up = False

			if event.key == pg.K_2:
				down = False
				up = True

			if event.key == pg.K_3:
				down = True
				up = True

			if event.key == pg.K_4:
				down = False
				up = False

			if event.key == pg.K_SPACE:
				draw = not draw

		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 5:
				# down
				t = max(t - step, 0.0)
			if event.button == 4:
				# up
				t = min(1.0, t + step)

		HandleGUI(event)

		for point in allPoints:
			point.HandleEvent(event)

	Update()
	DrawLoop()
