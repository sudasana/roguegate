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
from copy import deepcopy


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
CELL_LINK = 4						# represents a link to another block

CELL_MARKER = 100					# a marker of some kind, used for debugging

BLOCK_LINKS = [(0,-1), (1,0), (0,1), (-1,0)]		# list of directions for links to adjacent blocks

FLOOR_NAMES = ['Ground', 'Second', 'Third', 'Fourth']

SINTABLE = [
	0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453,
	0.12187, 0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192,
	0.25882, 0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461,
	0.39073, 0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000,
	0.51504, 0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566,
	0.62932, 0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934,
	0.73135, 0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902,
	0.81915, 0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295,
	0.89101, 0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969,
	0.94552, 0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815,
	0.98163, 0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756,
	0.99863, 0.99939, 0.99985, 1.00000, 0.99985, 0.99939, 0.99863, 0.99756,
	0.99619, 0.99452, 0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815,
	0.97437, 0.97030, 0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969,
	0.93358, 0.92718, 0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295,
	0.87462, 0.86603, 0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902,
	0.79864, 0.78801, 0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934,
	0.70711, 0.69466, 0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566,
	0.60182, 0.58779, 0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000,
	0.48481, 0.46947, 0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461,
	0.35837, 0.34202, 0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192,
	0.22495, 0.20791, 0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453,
	0.08716, 0.06976, 0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490,
	-0.05234, -0.06976, -0.08716, -0.10453, -0.12187, -0.13917, -0.15643,
	-0.17365, -0.19081, -0.20791, -0.22495, -0.24192, -0.25882, -0.27564,
	-0.29237, -0.30902, -0.32557, -0.34202, -0.35837, -0.37461, -0.39073,
	-0.40674, -0.42262, -0.43837, -0.45399, -0.46947, -0.48481, -0.50000,
	-0.51504, -0.52992, -0.54464, -0.55919, -0.57358, -0.58779, -0.60182,
	-0.61566, -0.62932, -0.64279, -0.65606, -0.66913, -0.68200, -0.69466,
	-0.70711, -0.71934, -0.73135, -0.74314, -0.75471, -0.76604, -0.77715,
	-0.78801, -0.79864, -0.80902, -0.81915, -0.82904, -0.83867, -0.84805,
	-0.85717, -0.86603, -0.87462, -0.88295, -0.89101, -0.89879, -0.90631,
	-0.91355, -0.92050, -0.92718, -0.93358, -0.93969, -0.94552, -0.95106,
	-0.95630, -0.96126, -0.96593, -0.97030, -0.97437, -0.97815, -0.98163,
	-0.98481, -0.98769, -0.99027, -0.99255, -0.99452, -0.99619, -0.99756,
	-0.99863, -0.99939, -0.99985, -1.00000, -0.99985, -0.99939, -0.99863,
	-0.99756, -0.99619, -0.99452, -0.99255, -0.99027, -0.98769, -0.98481,
	-0.98163, -0.97815, -0.97437, -0.97030, -0.96593, -0.96126, -0.95630,
	-0.95106, -0.94552, -0.93969, -0.93358, -0.92718, -0.92050, -0.91355,
	-0.90631, -0.89879, -0.89101, -0.88295, -0.87462, -0.86603, -0.85717,
	-0.84805, -0.83867, -0.82904, -0.81915, -0.80902, -0.79864, -0.78801,
	-0.77715, -0.76604, -0.75471, -0.74314, -0.73135, -0.71934, -0.70711,
	-0.69466, -0.68200, -0.66913, -0.65606, -0.64279, -0.62932, -0.61566,
	-0.60182, -0.58779, -0.57358, -0.55919, -0.54464, -0.52992, -0.51504,
	-0.50000, -0.48481, -0.46947, -0.45399, -0.43837, -0.42262, -0.40674,
	-0.39073, -0.37461, -0.35837, -0.34202, -0.32557, -0.30902, -0.29237,
	-0.27564, -0.25882, -0.24192, -0.22495, -0.20791, -0.19081, -0.17365,
	-0.15643, -0.13917, -0.12187, -0.10453, -0.08716, -0.06976, -0.05234,
	-0.03490, -0.01745, -0.00000
]
 
COSTABLE = [
	1.00000, 0.99985, 0.99939, 0.99863, 0.99756, 0.99619, 0.99452,
	0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815, 0.97437, 0.97030,
	0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969, 0.93358, 0.92718,
	0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295, 0.87462, 0.86603,
	0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902, 0.79864, 0.78801,
	0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934, 0.70711, 0.69466,
	0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566, 0.60182, 0.58779,
	0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000, 0.48481, 0.46947,
	0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461, 0.35837, 0.34202,
	0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192, 0.22495, 0.20791,
	0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453, 0.08716, 0.06976,
	0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490, -0.05234, -0.06976,
	-0.08716, -0.10453, -0.12187, -0.13917, -0.15643, -0.17365, -0.19081,
	-0.20791, -0.22495, -0.24192, -0.25882, -0.27564, -0.29237, -0.30902,
	-0.32557, -0.34202, -0.35837, -0.37461, -0.39073, -0.40674, -0.42262,
	-0.43837, -0.45399, -0.46947, -0.48481, -0.50000, -0.51504, -0.52992,
	-0.54464, -0.55919, -0.57358, -0.58779, -0.60182, -0.61566, -0.62932,
	-0.64279, -0.65606, -0.66913, -0.68200, -0.69466, -0.70711, -0.71934,
	-0.73135, -0.74314, -0.75471, -0.76604, -0.77715, -0.78801, -0.79864,
	-0.80902, -0.81915, -0.82904, -0.83867, -0.84805, -0.85717, -0.86603, 
	-0.87462, -0.88295, -0.89101, -0.89879, -0.90631, -0.91355, -0.92050,
	-0.92718, -0.93358, -0.93969, -0.94552, -0.95106, -0.95630, -0.96126,
	-0.96593, -0.97030, -0.97437, -0.97815, -0.98163, -0.98481, -0.98769,
	-0.99027, -0.99255, -0.99452, -0.99619, -0.99756, -0.99863, -0.99939,
	-0.99985, -1.00000, -0.99985, -0.99939, -0.99863, -0.99756, -0.99619,
	-0.99452, -0.99255, -0.99027, -0.98769, -0.98481, -0.98163, -0.97815,
	-0.97437, -0.97030, -0.96593, -0.96126, -0.95630, -0.95106, -0.94552,
	-0.93969, -0.93358, -0.92718, -0.92050, -0.91355, -0.90631, -0.89879,
	-0.89101, -0.88295, -0.87462, -0.86603, -0.85717, -0.84805, -0.83867,
	-0.82904, -0.81915, -0.80902, -0.79864, -0.78801, -0.77715, -0.76604,
	-0.75471, -0.74314, -0.73135, -0.71934, -0.70711, -0.69466, -0.68200,
	-0.66913, -0.65606, -0.64279, -0.62932, -0.61566, -0.60182, -0.58779,
	-0.57358, -0.55919, -0.54464, -0.52992, -0.51504, -0.50000, -0.48481,
	-0.46947, -0.45399, -0.43837, -0.42262, -0.40674, -0.39073, -0.37461,
	-0.35837, -0.34202, -0.32557, -0.30902, -0.29237, -0.27564, -0.25882,
	-0.24192, -0.22495, -0.20791, -0.19081, -0.17365, -0.15643, -0.13917,
	-0.12187, -0.10453, -0.08716, -0.06976, -0.05234, -0.03490, -0.01745,
	-0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453, 0.12187,
	0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192, 0.25882,
	0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461, 0.39073,
	0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000, 0.51504,
	0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566, 0.62932,
	0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934, 0.73135,
	0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902, 0.81915,
	0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295, 0.89101,
	0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969, 0.94552,
	0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815, 0.98163,
	0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756, 0.99863,
	0.99939, 0.99985, 1.00000
]




##### BlockFloor Object - represents one floor of one block of the entire complex #####
class BlockFloor():
	def __init__(self, floor, outdoor=False):
		
		self.floor = floor
		self.outdoor = outdoor			# block is only the ground floor of an outdoor area
		self.letter = ''			# block letter, A-
		
		self.links = {				# links to adjacent blocks
			(0,-1): None,
			(1,0): None,
			(0,1): None,
			(-1,0): None
		}
		
		self.link_locations = {			# cell locations of links to other blocks
			(0,-1): None,
			(1,0): None,
			(0,1): None,
			(-1,0): None
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
		hx1 = libtcod.random_get_int(0, 8, 10)
		hy1 = libtcod.random_get_int(0, 8, 30)
		hw = libtcod.random_get_int(0, 43, 49) - hx1
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
		
		
	# generate link cells for this block to adjacent ones
	def GenerateLinks(self):
		for (xm, ym) in BLOCK_LINKS:
			
			# link in this direction
			if self.links[(xm, ym)]:
				
				(x, y) = self.center_point
				
				link_set = False
				while not link_set:
					
					# edge of map
					if self.GetCell(x+xm, y+ym) == CELL_NULL:
						pass
					
					elif self.GetCell(x, y) != CELL_WALL:
						x += xm
						y += ym
						continue
					
					self.SetCell(x, y, CELL_LINK, False, False)
					self.link_locations[(xm, ym)] = (x,y)
					link_set = True
					continue
	
	
	# generate or re-generate the light map for all cells in this block-level
	def GenerateLightMap(self):
		
		def Raycast(x, y, radius, facing=None):
			
			STEP = 2			# how many steps per cycle
			
			# if light has a facing, only cast it for 90 degrees in that direction
			if facing is None:
				cast_start = 0
				cast_end = 361
			else:
				
				if facing == (0,-1):
					cast_start = 135
					cast_end = 225
				elif facing == (-1,0):
					cast_start = 225
					cast_end = 315
				elif facing == (0,1):
					cast_start = 315
					cast_end = 45
				elif facing == (1,0):
					cast_start = 45
					cast_end = 135
				else:
					print('ERROR: Incorrect facing on entity')
					return
			
			for i in range(0, 361, STEP):
				
				if facing is not None:
					if facing == (0,1):
						if i < cast_start and i > cast_end: continue
					else:
						if i < cast_start and i < cast_end: continue
						if i > cast_start and i > cast_end: continue
				
				ax = SINTABLE[i]	# Get precalculated value sin(x / (180 / pi))
				ay = COSTABLE[i]	# cos(x / (180 / pi))
				
				rx = float(x)
				ry = float(y)
				
				for z in range(radius): # Cast the ray
					rx += ax
					ry += ay
					
					cx, cy = int(rx), int(ry)
					
					# ray is off the map or in unplayable area
					if self.GetCell(cx, cy) == CELL_NULL: break
					
					# add light
					new_level = 255 - int(255 * z * 0.1)
					if new_level <= 0:
						continue
					
					if new_level > self.light_map[(cx, cy)]:
						self.light_map[(cx, cy)] = new_level
					
					# ray hit a wall or door
					if self.GetCell(cx, cy) in [CELL_WALL, CELL_DOOR]:
						break

		# reset light levels
		for x in range(61):
			for y in range(40):
				self.light_map[(x,y)] = 25
		
		# cast static lights
		for entity in self.light_entities:
			(x, y) = entity.location
			Raycast(x, y, entity.light_radius)
				
		# cast light from player flashlight
		(x, y) = game.player.location
		Raycast(x, y, 12, facing=game.player.facing)


	# generate the player visibility map for this block, store info in game object
	# uses recursive shadowcasting, based on:
	# http://www.roguebasin.com/index.php?title=Python_shadowcasting_implementation
	def GenerateVisMap(self):
		
		# Multipliers for transforming coordinates to other octants:
		MULT = [
			[1,  0,  0, -1, -1,  0,  0,  1],
			[0,  1, -1,  0,  0, -1,  1,  0],
			[0,  1,  1,  0,  0, -1, -1,  0],
			[1,  0,  0,  1, -1,  0,  0, -1]
		]
		
		# shadowcasting function
		def ShadowCast(cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
			
			def IsBlocked(x, y):
				return (x < 0 or y < 0
					or x >= 61 or y >= 40
					or self.GetCell(x, y) in [CELL_WALL, CELL_DOOR])
			
			if start < end: return
			
			radius_squared = radius * radius
			
			for j in range(row, radius+1):
				dx, dy = -j-1, -j
				blocked = False
				while dx <= 0:
					dx += 1
				
					# translate the dx, dy coordinates into map coordinates
					mx, my = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
					
					# l_slope and r_slope store the slopes of the left and right
					# extremities of the square we're considering
					l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
					
					if start < r_slope:
						continue
					elif end > l_slope:
						break
					else:
						# ray is touching this square, set it as visible
						if dx*dx + dy*dy < radius_squared:
							game.vis_map[(mx,my)] = True
						
						if blocked:
							
							# we're scanning a row of blocked squares
							if IsBlocked(mx, my):
								new_start = r_slope
								continue
							else:
								blocked = False
								start = new_start
						
						else:
							if IsBlocked(mx, my) and j < radius:
								blocked = True
								ShadowCast(cx, cy, j+1, start, l_slope,
									radius, xx, xy, yx, yy, id+1)
								new_start = r_slope
			
				# Row is scanned; do next row unless last square was blocked
				if blocked:
					break

		
		# clear current vis map
		for x in range(61):
			for y in range(40):
				game.vis_map[(x,y)] = False
		
		# cast in all 8 octants
		(x,y) = game.player.location
		for octant in range(8):
			ShadowCast(x, y, 1, 1.0, 0.0, 100,
                             MULT[0][octant], MULT[1][octant],
                             MULT[2][octant], MULT[3][octant], 0)
		
	


##### Entity Object - represents the player, one of the burglars, etc.
class Entity:
	def __init__(self):
		self.is_player = False
		self.block = None		# pointer to block location
		self.location = (0,0)		# current location in the world
		self.facing = None		# direction facing
		self.light_radius = 0		# entity emits light to this radius
	
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
		# dictionary, one list per coordinate
		self.block_map = {}
		self.GenerateBlocks()
		for x in range(5):
			for y in range(3):
				for block in self.block_map[(x,y)]:
					block.GenerateLinks()
		
		self.active_block = None			# current block in viewport
		self.active_floor = 0				# current floor in viewport
		self.vis_map = {}				# visibility for player in current block
		for x in range(61):
			for y in range(40):
				self.vis_map[(x,y)] = False
		
		# create player object
		new_entity = Entity()
		new_entity.is_player = True
		self.entities.append(new_entity)
		self.player = new_entity
		
		# put player in block A to start and move viewport to there
		self.MovePlayerToBlock('A')
		self.active_block = self.player.block
	
	
	# warp the player to the ground floor, center of the given block
	def MovePlayerToBlock(self, block_letter):
		for x in range(5):
			for y in range(3):
				block = self.block_map[(x,y)][0]
				if block.letter == block_letter:
					self.player.block = block
					self.player.location = block.center_point
					self.player.facing = (0,1)
					return
	
	
	# generate a series of building blocks for the complex
	def GenerateBlocks(self):
		
		for tries in range(300):
			
			# clear any existing blocks
			for x in range(5):
				for y in range(3):
					self.block_map[(x,y)] = []
		
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
					self.block_map[(x,y)].append(BlockFloor(0))
					total_blocks += 1
				else:
					self.block_map[(x,y)].append(BlockFloor(0, outdoor=True))
			
			# apply block number restrictions
			if total_blocks <= 9 or total_blocks >= 13:
				continue
			else: 
				break
		
		# apply letters and check for upper floor generation
		i = 0
		for y in range(3):
			for x in range(5):
				if self.block_map[(x,y)][0].outdoor: continue
				
				self.block_map[(x,y)][0].letter = chr(i+65)
				
				# possible 2nd, 3rd, and 4th floor
				for f in range(1, 5):
					
					# roll to break here
					if libtcod.random_get_int(0, 1, 100) <= f*10:
						break
				
					block_floor = deepcopy(self.block_map[(x,y)][0])
					block_floor.floor = f
					block_floor.letter = chr(i+65)
					self.block_map[(x,y)].append(block_floor)
				
				# TODO: add stair and elevator connections here
				if len(self.block_map[(x,y)]) > 1:
					pass
				
				
				# increase block letter
				i += 1
		
		# run through each block, apply letters and check for links
		for y in range(3):
			for x in range(5):
				
				for block in self.block_map[(x,y)]:
					
					# link blocks to adjacent ones
					for (xm, ym) in BLOCK_LINKS:
						
						if (x+xm,y+ym) not in self.block_map:
							continue
						
						block_list = self.block_map[(x+xm,y+ym)]
						
						# adjacent floor exists, link to it
						if len(block_list) > block.floor:
							block.links[(xm,ym)] = block_list[block.floor]
				
				
		
		
	# try to move the player one cell in the given direction
	def MovePlayer(self, x_dist, y_dist):
		
		# check for shift modifier
		max_moves = 1
		
		if key.shift:
			max_moves = 3
		
		for i in range(max_moves):
		
			(x,y) = self.player.location
			
			# make sure new location would still be on map
			if x+x_dist < 0 or x+x_dist >= 61:
				return
			if y+y_dist < 0 or y+y_dist >= 40:
				return
			
			# FUTURE: check for door blocking
			
			# check for wall blocking
			if self.active_block.char_map[(x+x_dist,y+y_dist)] == CELL_WALL: return
			
			# check for leaving the play area
			if self.active_block.char_map[(x+x_dist,y+y_dist)] == CELL_NULL: return
			
			# if play is not yet facing this rdirection, rotate them
			if self.player.facing != (x_dist, y_dist):
				self.player.facing = (x_dist, y_dist)
				#return
			
			# move the player
			self.player.location = (x+x_dist, y+y_dist)
	
	
	# try to warp the player to an adjacent block
	def LinkPlayer(self):
		
		for (xm, ym) in BLOCK_LINKS:
			if self.active_block.link_locations[(xm, ym)] is not None:
				(x, y) = self.active_block.link_locations[(xm, ym)]
				
				# player is on a link location
				if self.player.location == (x, y):
					
					# move them to the adjacent block and move view
					self.player.block = self.active_block.links[(xm, ym)]
					self.active_block = self.player.block
					
					# place them at the corresponding link location in the new block
					xm = 0 - xm
					ym = 0 - ym
					
					self.player.location = self.active_block.link_locations[(xm, ym)]
					
					return True
		
		return False
	
	
	# display the building block map
	def ViewMap(self):
		
		# update the map display
		def UpdateMap(floor):
			libtcod.console_set_default_background(con, CONSOLE_COL_8)
			libtcod.console_rect(con, 8, 4, 64, 32, True, libtcod.BKGND_SET)
			libtcod.console_set_default_background(con, libtcod.black)
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			DrawBox(con, 8, 4, 63, 31)
			
			libtcod.console_set_default_foreground(con, CONSOLE_COL_2)
			libtcod.console_print_ex(con, WINDOW_XM, 6, libtcod.BKGND_NONE, libtcod.CENTER,
				'RogueGate Building Map')
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			
			text = FLOOR_NAMES[floor] + ' Floor'
			libtcod.console_print_ex(con, WINDOW_XM, 8, libtcod.BKGND_NONE, libtcod.CENTER,
				text)
			
			# display blocks on this floor
			for x in range(5):
				for y in range(3):
					
					# floor does not exist in this block
					if len(self.block_map[(x,y)]) <= floor:
						libtcod.console_set_default_foreground(con, libtcod.black)
						DrawRect(con, 14+(x*11), 11+(y*7), 8, 4, 176)
						continue
					
					block = self.block_map[(x,y)][floor]
					
					# outdoor area
					if block.outdoor:
						libtcod.console_set_default_foreground(con, CONSOLE_COL_7)
						DrawRect(con, 14+(x*11), 11+(y*7), 8, 4, 176)
					
					# regular building
					else:
						libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
						DrawBox(con, 14+(x*11), 11+(y*7), 8, 4)
						# display block letter
						libtcod.console_print(con, 18+(x*11), 12+(y*7),
							block.letter)
					
					# indicate if player in currently in this block
					if self.player.block == block:
						libtcod.console_set_default_foreground(con, CONSOLE_COL_1)
						libtcod.console_put_char(con, 18+(x*11),
							13+(y*7), 64)
					
					# display links to adjacent blocks
					libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
					for (xm, ym) in BLOCK_LINKS:
						if block.links[(xm, ym)] is not None:
							
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
			libtcod.console_print(con, 34, 33, 'M')
			libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
			libtcod.console_print(con, 37, 33, 'Close Map')
			
			libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
		
		# set the currently displayed floor
		display_floor = self.player.block.floor
		
		# display the map for the first time
		UpdateMap(display_floor)
		
		# wait for player input
		exit_loop = False
		while not exit_loop:
			if libtcod.console_is_window_closed(): sys.exit()
			libtcod.console_flush()
			if not GetInputEvent(): continue
			
			key_char = chr(key.c).lower()
			
			# exit map view
			if key_char == 'm':
				exit_loop = True
			
			# change displayed floor
			elif key_char in ['w', 's']:
				if key_char == 'w' and display_floor < 3:
					display_floor += 1
				elif key_char == 's' and display_floor > 0:
					display_floor -= 1
				else:
					continue
				UpdateMap(display_floor)

	
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
		
		if not self.active_block.outdoor:
			libtcod.console_print(info_con, 2, 5, 'Block ' + self.active_block.letter)
			text = FLOOR_NAMES[self.active_block.floor] + ' Floor'
			libtcod.console_print(info_con, 2, 6, text)
		
		# security status
		libtcod.console_print(info_con, 2, 9, 'Status: CLEAR')
		
		
		# action key commands
		libtcod.console_set_default_foreground(info_con, CONSOLE_COL_1)
		libtcod.console_print(info_con, 2, 32, 'WASD')
		libtcod.console_print(info_con, 1, 33, '+Shft')
		libtcod.console_print(info_con, 4, 34, 'E')
		libtcod.console_print(info_con, 4, 35, 'M')
		
		libtcod.console_set_default_foreground(info_con, CONSOLE_COL_3)
		libtcod.console_print(info_con, 8, 32, 'Move')
		libtcod.console_print(info_con, 8, 33, 'Run')
		libtcod.console_print(info_con, 8, 34, 'Enter')
		libtcod.console_print(info_con, 8, 35, 'Map')
		
	
	
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
				elif cell == CELL_LINK:
					char = 240
					col = CONSOLE_COL_1
				elif floor_cell == CELL_MARKER:
					char = 254
					col = CONSOLE_COL_1
				
				# if not visible to player, display as dark as possible
				if not self.vis_map[(x,y)]:
					col = CONSOLE_COL_8
				else:
				
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
				
				self.MovePlayer(x_dist, y_dist)
				self.active_block.GenerateVisMap()
				self.active_block.GenerateLightMap()
				self.UpdateMapCon()
				self.UpdateEntityCon()
				self.UpdateScreen()
				SaveGame()
				continue
			
			# link to new block
			elif key_char == 'e':
				if self.LinkPlayer():
					self.active_block.GenerateVisMap()
					self.active_block.GenerateLightMap()
					self.UpdateInfoCon()
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
			
			# unrecognized command, flush it
			FlushKeyboardEvents()



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
libtcod.console_set_default_background(0, libtcod.black)
libtcod.console_set_default_foreground(0, CONSOLE_COL_2)

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
		
		# show loading screen, since generating the game object can take some time
		libtcod.console_clear(0)
		libtcod.console_print_ex(0, WINDOW_XM, WINDOW_YM-2, libtcod.BKGND_NONE,
			libtcod.CENTER, 'Loading...')
		libtcod.console_flush()
		
		# create a new game object
		game = Game()
		
		# generate the visibility and light maps for the block-floor
		game.active_block.GenerateVisMap()
		game.active_block.GenerateLightMap()
		
		# start the input loop
		game.DoInputLoop()
		
		# re-draw main menu
		DrawMainMenu()
		continue
		

# END #
