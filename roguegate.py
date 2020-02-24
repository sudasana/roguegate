import libtcodpy as libtcod

# create mouse and key event holders
mouse = libtcod.Mouse()
key = libtcod.Key()

libtcod.console_set_custom_font('cp437_16x16.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE)

root_console = libtcod.console_init_root(80, 40, title='RogueGate', order='F')
libtcod.sys_set_fps(50)

libtcod.console_print(0, 0, 0, 'Hello world!')

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
