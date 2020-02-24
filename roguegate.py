import tcod
import tcod.event

tcod.console_set_custom_font('cp437_16x16.png', tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE)

with tcod.console_init_root(80, 40, title='RogueGate', order='F') as root_console:
	
	root_console.print(x=0, y=0, fg=(217,163,0), string='Hello World!')
	while True:
		tcod.console_flush()
		for event in tcod.event.wait():
			if event.type == "QUIT":
				raise SystemExit()

# END #
