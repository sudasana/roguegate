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




##### General Drawing Functions ######

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
	libtcod.console_put_char(con, 32, 30, 'O')
	libtcod.console_put_char(con, 32, 31, 'Q')
	
	libtcod.console_set_default_foreground(con, CONSOLE_COL_3)
	libtcod.console_print(con, 36, 28, 'New Session')
	libtcod.console_print(con, 36, 29, 'Continue Session')
	libtcod.console_print(con, 36, 30, 'Options')
	libtcod.console_print(con, 36, 31, 'Quit')
	
	libtcod.console_blit(con, 0, 0, 0, 0, 0, 0, 0)
	
	
	
# draw main menu to the screen for the first time
DrawMainMenu()

exit_game = False
while not exit_game:
	if libtcod.console_is_window_closed(): sys.exit()
	libtcod.console_flush()
	event = libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE|libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
		key, mouse)
	if event != libtcod.EVENT_KEY_PRESS: continue
	
	if key.vk == libtcod.KEY_ESCAPE:
		exit_game = True

# END #
