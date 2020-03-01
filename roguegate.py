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
from random import choice, shuffle
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
CONSOLE_COL_8 = libtcod.Color(16,12,0)			# dark background colour

##### Map Cell Type Definitions #####
CELL_NULL = 0						# not active, no interactions possible
CELL_TILE = 1						# generic linoleum tile flooring
CELL_WALL = 2						# solid concrete wall
CELL_DOOR = 3						# door, further info stored in the doors list

CELL_MARKER = 100					# a marker of some kind, used for debugging

BLOCK_LINKS = [(0,-1), (1,0), (0,1), (-1,0)]		# list of directions for links to adjacent blocks



##### BlockFloor Object - represents one floor of one block of the entire complex #####
class BlockFloor():
	def __init__(self, outdoor=False):
		
		self.outdoor=outdoor			# block is only the ground floor of an outdoor area
		self.letter = ''			# block letter, A-
		
		self.links = {				# links to adjacent blocks
			(0,-1): False,
			(1,0): False,
			(0,1): False,
			(-1,0): False
		}
		
		self.char_map = {}			# map of cells
		self.center_point = (0,0)
		self.rooms = []				# list of rooms in (x,y,w,h) format
		self.light_entities = []		# list of lights in the map
		
		self.light_map = {}			# light values for cells
		
		# generate the map for this block-floor
		self.GenerateMap()
	
	
	# add a light entity at the given location
	def AddLight(self, x, y, light_radius):
		new_entity = Entity()
		new_entity.location = (x, y)
		new_entity.light_radius = light_radius
		self.light_entities.append(new_entity)
	
	
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
		
		# clear list of rooms, light entities
		self.rooms = []
		self.light_entities = []
		
		# outdoor blocks are set up differently
		if self.outdoor:
			for x in range(61):
				for y in range(40):
					self.char_map[(x,y)] = CELL_TILE
			self.center_point = (30, 20)
			for x in range(10, 51, 10):
				self.AddLight(x, 20, 5)
			for y in range(10, 31, 10):
				if y == 20: continue
				self.AddLight(30, y, 5)
			return
		
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
		
		# record center point and add a light here
		self.center_point = (vx1+1, hy1+1)
		self.AddLight(vx1+1, hy1+1, 5)
		
		# add lights down each hallway
		for x in range(vx1+1, hx1, -15):
			self.AddLight(x, hy1+1, 5)
		for x in range(vx1+1, hx1+hw, 15):
			self.AddLight(x, hy1+1, 5)
		
		
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
		
		# cast light from the given point to the given radius
		def CastLight(x, y, radius):
			
			if radius == 0: return
			
			for xm in range(0-radius,radius+1):
				for ym in range(0-radius,radius+1):
					
					# cell is off map
					if (x+xm, y+ym) not in self.light_map:
						continue
					
					point_distance = round(GetDistanceBetween(0, 0, xm, ym), 2)
					if point_distance > float(radius):
						continue
					
					# calculate what the new light level would be based on distance from player
					new_level = 255 - int(255.0 * round(point_distance / float(radius), 2))
					
					# if level is higher, set new level
					
					# set this cell's light level 
					if new_level > self.light_map[(x+xm, y+ym)]:
						self.light_map[(x+xm, y+ym)] = new_level
			
		
		# set all initial values to low light
		for x in range(61):
			for y in range(40):
				self.light_map[(x,y)] = 25
		
		# cast light from each light entity
		for entity in self.light_entities:
			(x,y) = entity.location
			CastLight(x, y, entity.light_radius)

		# TESTING - cast light around the player
		(x, y) = game.player.location
		CastLight(x, y, 6)
		
		
		
		



##### Entity Object - represents the player, one of the burglars, etc.
class Entity:
	def __init__(self):
		self.is_player = False
		self.block = None		# pointer to block location
		self.location = (0,0)		# current location in the world
		self.light_radius = 0		# entity emits light ot his radius
	
	# draw entity onto the entity console
	def DrawMe(self):
		
		(x,y) = self.location
		
		# light entity
		if self.light_radius > 0:
			libtcod.console_put_char_ex(entity_con, x, y, 254,
				CONSOLE_COL_1, libtcod.black)

		elif self.is_player:
			libtcod.console_put_char_ex(entity_con, x, y, 64,
				CONSOLE_COL_1, libtcod.black)
						


##### Game Object - holds everything for a given game #####
class Game:
	def __init__(self):
		
		self.hour = 19			# current time
		self.minute = 0	
		self.next_day = False		# if clock has passed midnight already
		
		# list of entities in the world
		self.entities = []
		
		# building blocks within the complex, 5x3 possible locations
		self.block_map = {}
		self.GenerateBlocks()
		
		self.active_block = None			# current block in viewport
		
		# create player object
		new_entity = Entity()
		new_entity.is_player = True
		self.entities.append(new_entity)
		self.player = new_entity
		
		# put player in block A to start and move viewport to there
		self.MovePlayerToBlock('A')
		self.active_block = self.player.block
	
	
	# move the player to the center of the given block
	def MovePlayerToBlock(self, block_letter):
		for x in range(5):
			for y in range(3):
				if self.block_map[(x,y)].letter == block_letter:
					self.player.block = self.block_map[(x,y)]
					self.player.location = self.block_map[(x,y)].center_point
					return
	
	
	# generate a series of building blocks for the complex
	def GenerateBlocks(self):
		
		for tries in range(300):
			
			# clear any existing blocks
			for x in range(5):
				for y in range(3):
					self.block_map[(x,y)] = None
		
			# run through block locations and roll for presence of a building block
			block_list = list(self.block_map.keys())
			shuffle(block_list)
			total_blocks = 0
			
			for (x,y) in block_list:
				
				# blocks in center of complex have less chance of being spawned
				if y == 1 and 0 < x < 4:
					chance = 30
				else:
					chance = 80
				
				# modify by already existing number of blocks
				chance -= total_blocks * 5
				
				if libtcod.random_get_int(0, 1, 100) <= chance:
					self.block_map[(x,y)] = BlockFloor()
					total_blocks += 1
				else:
					self.block_map[(x,y)] = BlockFloor(outdoor=True)
			
			# apply block number restrictions
			if total_blocks <= 7 or total_blocks >= 11:
				continue
			else: 
				break
		
		# apply letters to blocks and link blocks to adjacent ones
		i = 0
		for y in range(3):
			for x in range(5):
				if not self.block_map[(x,y)].outdoor:
					self.block_map[(x,y)].letter = chr(i+65)
					i += 1
				
				# check for links
				for (xm, ym) in BLOCK_LINKS:
					if (x+xm, y+ym) in self.block_map:
						self.block_map[(x,y)].links[(xm,ym)] = True
		
		
	# try to move the player one cell in the given direction
	def MovePlayer(self, x_dist, y_dist):
		
		(x,y) = self.player.location
		
		# make sure new location would still be on map
		if x+x_dist < 0 or x+x_dist >= 61:
			return False
		if y+y_dist < 0 or y+y_dist >= 40:
			return False
		
		# check for wall blocking
		if self.active_block.char_map[(x+x_dist,y+y_dist)] == CELL_WALL: return False
		
		x = x+x_dist
		y = y+y_dist
		
		self.player.location = (x,y)
		return True
	
	
	# display the building block map
	def ViewMap(self):
		
		# update the map display
		def UpdateMap():
			libtcod.console_set_default_background(con, CONSOLE_COL_8)
			libtcod.console_rect(con, 8, 4, 64, 32, True, libtcod.BKGND_SET)
			libtcod.console_set_default_background(con, libtcod.black)
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			DrawBox(con, 8, 4, 63, 31)
			
			libtcod.console_set_default_foreground(con, CONSOLE_COL_2)
			libtcod.console_print_ex(con, WINDOW_XM, 6, libtcod.BKGND_NONE, libtcod.CENTER,
				'RogueGate Building Map')
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			# TEMP - static
			libtcod.console_print_ex(con, WINDOW_XM, 8, libtcod.BKGND_NONE, libtcod.CENTER,
				'Ground Floor')
			
			# display blocks
			for x in range(5):
				for y in range(3):
					
					# outdoor area
					if self.block_map[(x,y)].outdoor:
						libtcod.console_set_default_foreground(con, CONSOLE_COL_7)
						DrawRect(con, 14+(x*11), 11+(y*7), 8, 4, 176)
					
					# regular building
					else:
						libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
						DrawBox(con, 14+(x*11), 11+(y*7), 8, 4)
						# display block letter
						libtcod.console_print(con, 18+(x*11), 12+(y*7),
							self.block_map[(x,y)].letter)
					
					# indicate if player in currently in this block
					if self.player.block == self.block_map[(x,y)]:
						libtcod.console_put_char(con, 18+(x*11),
							13+(y*7), 64)
					
					# display links to adjacent blocks
					libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
					for (xm, ym) in BLOCK_LINKS:
						if self.block_map[(x,y)].links[(xm, ym)] is True:
							
							# vertical link
							if xm == 0:
								char = 186
								x1 = 18+(x*11)
								if ym == -1:
									y1 = 10+(y*7)
								else:
									y1 = 16+(y*7)
							
							# horizontal link
							else:
								char = 205
								y1 = 13+(y*7)
								if xm == -1:
									x1 = 13+(x*11)
								else:
									x1 = 23+(x*11)
							
							libtcod.console_put_char(con, x1, y1, char)
			
			libtcod.console_set_default_foreground(con, CONSOLE_COL_1)
			libtcod.console_print(con, 32, 33, 'Esc')
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			libtcod.console_print(con, 37, 33, 'Close Map')
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
		
		# display the map for the first time
		UpdateMap()
		
		# wait for player input
		exit_loop = False
		while not exit_loop:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			if key.vk == libtcod.KEY_ESCAPE:
				exit_loop = True
				continue
			
			key_char = chr(key.c).lower()
			
			# DEBUG - regenerate block map
			if key_char == 'g':
				self.GenerateBlocks()
				self.MovePlayerToBlock('A')
				self.active_block = self.player.block
				self.active_block.GenerateLightMap()
				self.UpdateMapCon()
				self.UpdateEntityCon()
				UpdateMap()
				SaveGame()
				continue
		
		pass
	
	# update the information console, 18x40
	def UpdateInfoCon(self):
		libtcod.console_clear(info_con)
		
		libtcod.console_set_default_foreground(info_con, CONSOLE_COL_2)
		
		# display current date and time
		if self.next_day:
			text = '06-17-72'
		else:
			text = '06-18-72'
		libtcod.console_print(info_con, 2, 1, text)
		
		text = str(self.hour).zfill(2) + ':' + str(self.minute).zfill(2)
		libtcod.console_print(info_con, 2, 2, text)
		
		libtcod.console_print(info_con, 2, 5, 'Block ' + self.active_block.letter)
		libtcod.console_print(info_con, 2, 6, 'Ground Floor')
		
		# security status
		libtcod.console_print(info_con, 2, 9, 'Status: CLEAR')
		
		
		# action key commands
		libtcod.console_set_default_foreground(info_con, CONSOLE_COL_1)
		libtcod.console_print(info_con, 2, 38, 'M')
		
		libtcod.console_set_default_foreground(info_con, CONSOLE_COL_3)
		libtcod.console_print(info_con, 5, 38, 'View Map')
		
	
	
	# update the floor map console
	def UpdateMapCon(self):
		libtcod.console_clear(map_con)
		
		# draw each map cell to the console
		for x in range(61):
			for y in range(40):
				cell = self.active_block.char_map[(x,y)]
				if cell == CELL_NULL:
					continue
				elif cell == CELL_TILE:
					char = 250
					col = CONSOLE_COL_7
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
				l = self.active_block.light_map[(x,y)]
				col = col * libtcod.Color(l, l, l)
				
				# draw the display character for this cell
				libtcod.console_put_char_ex(map_con, x, y, char, col, libtcod.black)
	
	
	# draw entities to the entity console
	def UpdateEntityCon(self):
		libtcod.console_clear(entity_con)
		
		# draw light entitites first
		for entity in self.active_block.light_entities:
			entity.DrawMe()
		
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
					self.active_block.GenerateLightMap()
					self.UpdateMapCon()
					self.UpdateEntityCon()
					self.UpdateScreen()
					SaveGame()
				
				continue
			
			# view building block map
			elif key_char == 'm':
				self.ViewMap()
				self.UpdateScreen()
				continue
			
			# DEBUG - regenerate the block-floor map
			elif key_char == 'g':
				self.active_block.GenerateMap()
				self.player.location = self.active_block.center_point	# move the player too
				self.active_block.GenerateLightMap()
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


# draw a box of single lines with corners
def DrawBox(console, x, y, w, h):
	for x1 in range(x+1, x+w):
		libtcod.console_put_char(console, x1, y, 196)
		libtcod.console_put_char(console, x1, y+h, 196)
	for y1 in range(y+1, y+h):
		libtcod.console_put_char(console, x, y1, 179)
		libtcod.console_put_char(console, x+w, y1, 179)
	libtcod.console_put_char(con, x, y, 218)
	libtcod.console_put_char(con, x+w, y, 191)
	libtcod.console_put_char(con, x, y+h, 192)
	libtcod.console_put_char(con, x+w, y+h, 217)


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
		game.active_block.GenerateLightMap()
		
		# start the input loop
		game.DoInputLoop()
		
		# re-draw main menu
		DrawMainMenu()
		continue
		

# END #
