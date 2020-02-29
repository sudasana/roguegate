# -*- coding: UTF-8 -*-
# Python 3.6.6 x64
# Libtcod 1.6.4 x64

#    RogueGate, a 7-day Roguelike
#    Mark Johnson and Gregory Adam Scott, 10:00 GMT 29th February 2020 - 7th March 2020
#    Copyright (c) 2020 Mark Johnson and Gregory Adam Scott
#
#    This file is part of RogueGate.
#
#    RogueGate is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RogueGate is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with RogueGate, in the form of a file named "gpl.txt".
#    If not, see <https://www.gnu.org/licenses/>.

##### Libraries #####
import os, sys						# OS-related stuff
import libtcodpy as libtcod
import shelve						# saving and loading games
from random import choice
from math import sqrt


##### Constants #####
NAME = 'RogueGate'					# game name
VERSION = '0.1'						# game version
RENDERER = libtcod.RENDERER_OPENGL2
LIMIT_FPS = 50
WINDOW_WIDTH, WINDOW_HEIGHT = 80, 40
WINDOW_XM, WINDOW_YM = int(WINDOW_WIDTH/2), int(WINDOW_HEIGHT/2)

##### Colour Definitions #####
KEY_COLOR = libtcod.Color(255,0,255)			# key color for transparency
CONSOLE_COL_1 = libtcod.Color(255,217,102)		# console colours from brightest to darkest
CONSOLE_COL_2 = libtcod.Color(255,204,51)
CONSOLE_COL_3 = libtcod.Color(255,191,0)
CONSOLE_COL_4 = libtcod.Color(217,163,0)
CONSOLE_COL_5 = libtcod.Color(178,134,0)
CONSOLE_COL_6 = libtcod.Color(140,105,0)
CONSOLE_COL_7 = libtcod.Color(102,77,0)
CONSOLE_COL_8 = libtcod.Color(64,48,0)

##### Map Cell Type Definitions #####
CELL_NULL = 0						# not active, no interactions possible
CELL_TILE = 1						# generic linoleum tile flooring
CELL_WALL = 2						# solid concrete wall
CELL_DOOR = 3						# door, further info stored in the doors list

CELL_MARKER = 100					# a marker of some kind, used for debugging

##### BlockFloor Object - represents one floor of one block of the entire complex #####
class BlockFloor():
	def __init__(self):
		
		self.char_map = {}			# map of cells
		self.center_point = (0,0)
		self.rooms = []				# list of rooms in (x,y,w,h) format
		
		self.light_map = {}			# light values for cells
		
		# generate the map for this block-floor
		self.GenerateMap()
	
	
	# set a given cell to a cell type, ignores if not on map
	def SetCell(self, x, y, new_type, skip_replace, skip_floors):
		if (x,y) not in self.char_map: return
		if skip_floors and self.char_map[(x,y)] == CELL_TILE: return
		if skip_replace and self.char_map[(x,y)] != CELL_NULL: return
		self.char_map[(x,y)] = new_type
	
	
	# get the cell code of the given cell; if not on map, will return CELL_NULL
	def GetCell(self, x, y):
		if (x,y) not in self.char_map: return CELL_NULL
		return self.char_map[(x,y)]
	
	
	# generate or re-generate the map, 61x40
	def GenerateMap(self):
		
		# create a room: h, w is the floor space, with one extra layer of walls
		def AddRoom(x1, y1, w, h, skip_replace=False, skip_floors=False):
			for x in range(x1, x1+w):
				for y in range(y1, y1+h):
					self.SetCell(x, y, CELL_TILE, skip_replace, skip_floors)
			# horizontal walls
			for x in range(x1, x1+w):
				self.SetCell(x, y1-1, CELL_WALL, skip_replace, skip_floors)
				self.SetCell(x, y1+h, CELL_WALL, skip_replace, skip_floors)
			# vertical walls
			for y in range(y1-1, y1+h+1):
				self.SetCell(x1-1, y, CELL_WALL, skip_replace, skip_floors)
				self.SetCell(x1+w, y, CELL_WALL, skip_replace, skip_floors)
		
		# character map - one for each possible map cell
		# set all cells to null to start
		for x in range(61):
			for y in range(40):
				self.char_map[(x,y)] = CELL_NULL
		
		# clear list of rooms
		self.rooms = []
		
		# set a main horizontal hallway to start
		hx1 = libtcod.random_get_int(0, 2, 6)
		hy1 = libtcod.random_get_int(0, 8, 30)
		hw = libtcod.random_get_int(0, 53, 59) - hx1
		AddRoom(hx1, hy1, hw, 3)
		
		# set up a vertical hallway
		vx1 = libtcod.random_get_int(0, 12, 50)
		vy1 = libtcod.random_get_int(0, 4, 8)
		vh = libtcod.random_get_int(0, 30, 38) - vy1
		AddRoom(vx1, vy1, 3, vh, skip_floors=True)
		
		# record center point
		self.center_point = (vx1+1, hy1+1)
		
		# determine the height of the rooms off the horizontal hallway
		room_height_upper = libtcod.random_get_int(0, 2, 6) + libtcod.random_get_int(0, 2, 6)
		room_height_lower = libtcod.random_get_int(0, 2, 6) + libtcod.random_get_int(0, 2, 6)
		
		# adjust in case they would go off the map
		if hy1-1-room_height_upper <= 0:
			room_height_upper = hy1-2
		if hy1+2+room_height_lower >= 37:
			room_height_lower = 37-hy1-2
		
		# run across the x axis and try to add upper rooms
		x = hx1
		while x < hx1+hw:
			
			if x >= 60: break
			
			width = libtcod.random_get_int(0, 2, 4) + libtcod.random_get_int(0, 2, 4)
			
			# check for blocking walls
			room_clear = True
			for x1 in range(x, x+width):
				if x1 >= 60:
					room_clear = False
				if not room_clear: break
				for y1 in range(hy1-room_height_upper, hy1-1):
					if self.char_map[(x1,y1)] == CELL_WALL:
						room_clear = False
						break
			
			# if not enough space, try to adjust the room width
			if not room_clear:
				width = x1-x
				if width <= 2:
					x += 2
					continue
			
			# create the room
			AddRoom(x, hy1-room_height_upper-1, width, room_height_upper, skip_replace=True)
			# record it
			self.rooms.append((x, hy1-room_height_upper-1, width, room_height_upper))
			
			x += width+1
		
		# run across the x axis and try to add lower rooms
		x = hx1
		while x < hx1+hw:
			
			if x >= 60: break
			
			width = libtcod.random_get_int(0, 2, 4) + libtcod.random_get_int(0, 2, 4)
			
			# check for blocking walls
			room_clear = True
			for x1 in range(x, x+width):
				if x1 >= 60:
					room_clear = False
				if not room_clear: break
				for y1 in range(hy1+4, hy1+3+room_height_lower):
					if self.char_map[(x1,y1)] == CELL_WALL:
						room_clear = False
						break
			
			# if not enough space, try to adjust the room width
			if not room_clear:
				width = x1-x
				if width <= 2:
					x += 2
					continue
			
			# create the room
			AddRoom(x, hy1+4, width, room_height_lower, skip_replace=True)
			self.rooms.append((x, hy1+4, width, room_height_lower))
			
			x += width+1

		
		# TODO: do the same for the vertical hallway?
		
		
		# create doors to connect rooms to at least one hallway
		
		for (x, y, w, h) in self.rooms:
			possible_door_cells = []
			
			# check upper wall
			for x1 in range(x, x+w):
				if self.GetCell(x1-1, y-1) != CELL_WALL: continue
				if self.GetCell(x1+1, y-1) != CELL_WALL: continue
				if self.GetCell(x1,y-2) == CELL_TILE:
					possible_door_cells.append((x1, y-1))
				
			# check lower wall
			for x1 in range(x, x+w):
				if self.GetCell(x1-1, y+h) != CELL_WALL: continue
				if self.GetCell(x1+1, y+h) != CELL_WALL: continue
				if self.GetCell(x1,y+h+1) == CELL_TILE:
					possible_door_cells.append((x1, y+h))
		
			if len(possible_door_cells) == 0:
				continue
			
			(x1, y1) = choice(possible_door_cells)
			self.SetCell(x1, y1, CELL_DOOR, False, False)
	
	
	# generate or re-generate the light map for all cells in this block-level
	def GenerateLightMap(self):
		
		# set all initial values to 0
		for x in range(61):
			for y in range(40):
				self.light_map[(x,y)] = 0

		# TESTING - cast light around the player
		(px, py) = game.player.location
		distance = 6
		
		for xm in range(0-distance,distance+1):
			for ym in range(0-distance,distance+1):
				
				# cell is off map
				if (px+xm, py+ym) not in self.light_map:
					continue
				
				point_distance = round(GetDistanceBetween(0, 0, xm, ym), 2)
				if point_distance > float(distance):
					continue
				
				# set this cell's light level based on distance from player
				light_level = round(point_distance / float(distance), 2)
				
				self.light_map[(px+xm, py+ym)] = 255 - int(255.0 * light_level)



##### Entity Object - represents the player, one of the burglars, etc.
class Entity:
	def __init__(self):
		self.is_player = False
		self.location = (0,0)		# current location in the world
	
	# draw entity onto the entity console
	def DrawMe(self):
		
		if self.is_player:
			(x,y) = self.location
			libtcod.console_put_char_ex(entity_con, x, y, 64,
				CONSOLE_COL_1, libtcod.black)
						


##### Game Object - holds everything for a given game #####
class Game:
	def __init__(self):
		
		# TEMP - only one block-floor to start
		self.block_floor = BlockFloor()
		
		# list of entities in the world
		self.entities = []
		
		# create player object
		new_entity = Entity()
		new_entity.is_player = True
		new_entity.location = self.block_floor.center_point
		self.entities.append(new_entity)
		
		self.player = new_entity
	
	
	# try to move the player one cell in the given direction
	def MovePlayer(self, x_dist, y_dist):
		
		(x,y) = self.player.location
		
		# make sure new location would still be on map
		if x+x_dist < 0 or x+x_dist >= 61:
			return False
		if y+y_dist < 0 or y+y_dist >= 40:
			return False
		
		# check for wall blocking
		if self.block_floor.char_map[(x+x_dist,y+y_dist)] == CELL_WALL: return False
		
		x = x+x_dist
		y = y+y_dist
		
		self.player.location = (x,y)
		return True
	
	
	# update the information console
	def UpdateInfoCon(self):
		libtcod.console_clear(info_con)
		libtcod.console_print(info_con, 4, 1, '06-17-72')
		libtcod.console_print(info_con, 4, 4, 'Block A')
		libtcod.console_print(info_con, 4, 5, 'Ground Floor')
	
	
	# update the floor map console
	def UpdateMapCon(self):
		libtcod.console_clear(map_con)
		
		# draw each map cell to the console
		for x in range(61):
			for y in range(40):
				cell = self.block_floor.char_map[(x,y)]
				if cell == CELL_NULL:
					continue
				elif cell == CELL_TILE:
					char = 250
					col = CONSOLE_COL_8
				elif cell == CELL_WALL:
					char = 178
					col = CONSOLE_COL_4
				elif cell == CELL_DOOR:
					char = 196
					col = CONSOLE_COL_3
				elif floor_cell == CELL_MARKER:
					char = 254
					col = CONSOLE_COL_1
				
				# change display colour depending on light level of this cell
				l = self.block_floor.light_map[(x,y)]
				col = col * libtcod.Color(l, l, l)
				
				# draw the display character for this cell
				libtcod.console_put_char_ex(map_con, x, y, char, col, libtcod.black)
	
	
	# draw entities to the entity console
	def UpdateEntityCon(self):
		libtcod.console_clear(entity_con)
		for entity in self.entities:
			entity.DrawMe()
	
	
	# update the game screen and blit to the root console
	def UpdateScreen(self):
		libtcod.console_clear(con)
		libtcod.console_blit(info_con, 0, 0, 0, 0, con, 0, 0)
		libtcod.console_blit(map_con, 0, 0, 0, 0, con, 19, 0)
		libtcod.console_blit(entity_con, 0, 0, 0, 0, con, 19, 0)
		libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
		DrawVLine(con, 18, 0, 40, 179)
		libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
	
	# do the input loop for the active game
	def DoInputLoop(self):
		
		global info_con, map_con, entity_con
		
		# create the main screen consoles
		info_con = NewConsole(18, 40, libtcod.black, CONSOLE_COL_2)
		map_con = NewConsole(61, 40, libtcod.black, CONSOLE_COL_2)
		entity_con = NewConsole(61, 40, KEY_COLOR, CONSOLE_COL_2, key_colour=True)
		
		# draw consoles and game screen for first time
		self.UpdateInfoCon()
		self.UpdateMapCon()
		self.UpdateEntityCon()
		self.UpdateScreen()
		
		SaveGame()
		
		exit_loop = False
		while not exit_loop:
			
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			# TEMP - quit to main menu right away
			if key.vk == libtcod.KEY_ESCAPE:
				SaveGame()
				exit_loop = True
				continue
			
			key_char = chr(key.c).lower()
			
			# player movement
			if key_char in ['a', 's', 'd', 'w']:
				
				x_dist = 0
				y_dist = 0
				if key_char == 'a':
					x_dist = -1
				elif key_char == 'd':
					x_dist = 1
				elif key_char == 'w':
					y_dist = -1
				else:
					y_dist = 1
				
				if self.MovePlayer(x_dist, y_dist):
					
					self.block_floor.GenerateLightMap()
					self.UpdateMapCon()
					self.UpdateEntityCon()
					
					self.UpdateScreen()
					SaveGame()
				
				continue
			
			# DEBUG - regenerate the block-floor map
			if key_char == 'g':
				self.block_floor.GenerateMap()
				self.player.location = self.block_floor.center_point	# move the player too
				self.UpdateMapCon()
				self.UpdateEntityCon()
				self.UpdateScreen()
				SaveGame()
				continue
		



##### General Functions ######

# get the distance between two points
def GetDistanceBetween(x1, y1, x2, y2):
	return sqrt(abs(x1-x2)**2 + abs(y1-y2)**2)


# save the current game in progress
def SaveGame():
	save = shelve.open('savegame', 'n')
	save['game'] = game
	save.close()


# load a saved game
def LoadGame():
	global game
	save = shelve.open('savegame')
	game = save['game']
	save.close()


# shortcut for generating consoles
def NewConsole(x, y, bg, fg, key_colour=False):
	new_con = libtcod.console_new(x, y)
	libtcod.console_set_default_background(new_con, bg)
	libtcod.console_set_default_foreground(new_con, fg)
	if key_colour:
		libtcod.console_set_key_color(new_con, KEY_COLOR)
	libtcod.console_clear(new_con)
	return new_con


# draw a rectangle of the given character to the give console
def DrawRect(console, x, y, w, h, char):
	if w < 3 or h < 3: return
	for x1 in range(x, x+w+1):
		libtcod.console_put_char(con, x1, y, char)
		libtcod.console_put_char(con, x1, y+h, char)
	for y1 in range(y+1, y+h):
		libtcod.console_put_char(con, x, y1, char)
		libtcod.console_put_char(con, x+w, y1, char)


# draw a vertical line of the given character
def DrawVLine(console, x, y, h, char):
	for y1 in range(y, y+h+1):
		libtcod.console_put_char(con, x, y1, char)


# get keyboard and/or mouse event; returns False if no new key press
def GetInputEvent():
	global key_down
	event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
		key, mouse)
	if key_down:
		if event != libtcod.EVENT_KEY_RELEASE:
			return False
		key_down = False
	if event != libtcod.EVENT_KEY_PRESS:
		return False
	key_down = True
	return True


# clear all keyboard events
def FlushKeyboardEvents():
	global key_down
	exit = False
	while not exit:
		libtcod.console_flush()
		event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
		if event != libtcod.EVENT_KEY_PRESS: exit = True
	key_down = False


##########################################################################################
#                                       Main Menu                                        #
##########################################################################################

global game, key_down
key_down = False

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()

libtcod.console_set_custom_font('cp437_16x16.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE)
root_console = libtcod.console_init_root(WINDOW_WIDTH, WINDOW_HEIGHT, title=NAME + ' ' + VERSION,
	order='F')
libtcod.sys_set_fps(LIMIT_FPS)


# create double buffer console
con = libtcod.console_new(WINDOW_WIDTH, WINDOW_HEIGHT)
libtcod.console_set_default_background(con, libtcod.black)
libtcod.console_set_default_foreground(con, CONSOLE_COL_4)
libtcod.console_clear(con)

# Draw the main menu to the root console
def DrawMainMenu():
	libtcod.console_clear(con)
	libtcod.console_set_default_foreground(con, CONSOLE_COL_4)
	
	libtcod.console_print_ex(con, WINDOW_XM, 6, libtcod.BKGND_NONE, libtcod.CENTER,
		'06-17-72')
	DrawRect(con, 26, 10, 27, 9, 178)
	DrawVLine(con, 25, 10, 9, 177)
	DrawVLine(con, 54, 10, 9, 177)
	DrawVLine(con, 24, 10, 9, 176)
	DrawVLine(con, 55, 10, 9, 176)
	
	libtcod.console_set_default_foreground(con, CONSOLE_COL_2)
	libtcod.console_print_ex(con, WINDOW_XM, 12, libtcod.BKGND_NONE, libtcod.CENTER,
		'RogueGate Complex')
	libtcod.console_print_ex(con, WINDOW_XM, 16, libtcod.BKGND_NONE, libtcod.CENTER,
		'"A City within a City!"')
	
	libtcod.console_set_default_foreground(con, CONSOLE_COL_6)
	libtcod.console_print_ex(con, WINDOW_XM, 23, libtcod.BKGND_NONE, libtcod.CENTER,
		'Security System ' + VERSION)
	libtcod.console_print_ex(con, WINDOW_XM, 24, libtcod.BKGND_NONE, libtcod.CENTER,
		'Main Menu')
	
	# action keys
	libtcod.console_set_default_foreground(con, CONSOLE_COL_1)
	libtcod.console_put_char(con, 32, 28, 'N')
	libtcod.console_put_char(con, 32, 29, 'C')
	#libtcod.console_put_char(con, 32, 30, 'O')
	libtcod.console_set_default_foreground(con, CONSOLE_COL_1)
	libtcod.console_put_char(con, 32, 31, 'Q')
	
	libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
	libtcod.console_print(con, 36, 28, 'New Session')
	libtcod.console_print(con, 36, 29, 'Continue Session')
	#libtcod.console_print(con, 36, 30, 'Options')
	libtcod.console_set_default_foreground(con, CONSOLE_COL_1)
	libtcod.console_print(con, 36, 31, 'Quit')
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	
	
# draw main menu to the screen for the first time
DrawMainMenu()

exit_game = False
while not exit_game:
	if libtcod.console_is_window_closed(): sys.exit()
	libtcod.console_flush()
	if not GetInputEvent(): continue
	
	key_char = chr(key.c).lower()
	
	if key_char == 'q':
		exit_game = True
		continue
	
	# continue saved session
	elif key_char == 'c':
		LoadGame()
		
		# start the input loop
		game.DoInputLoop()
		
		# re-draw main menu
		DrawMainMenu()
		continue
	
	# New session
	elif key_char == 'n':
		
		# create a new game object
		game = Game()
		
		# generate the light map for the block-floor
		game.block_floor.GenerateLightMap()
		
		# start the input loop
		game.DoInputLoop()
		
		# re-draw main menu
		DrawMainMenu()
		continue
		

# END #
