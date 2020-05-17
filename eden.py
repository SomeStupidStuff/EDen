#!/usr/bin/env python3
import curses
import os
from sys import argv
from key_commands import add_all_commands

# Curses eats any prints so we have to store any prints for after the window is destroyed
debug_log = []

def to_pages(window):
	"""Separates 1d array of lines into a 2d array of pages which have a max length of window.page_length"""
	pages = []
	cpy = list(window.lines)
	while (cpy):
		pages.append(cpy[:window.page_length])
		cpy = cpy[window.page_length:]
	return pages

class WindowState:
	def __init__(self):
		super(WindowState, self).__init__()

		self.file_name = ""
		try:
			self.file_name = argv[1]
			self.set_file(self.file_name)
		except IOError:
			# Incase of file not being create
			self.file_name = argv[1]
			os.mknod(self.file_name)
			self.set_file(self.file_name)
		except IndexError:
			# Incase of no file being provided
			self.lines = [""]
			# Put to stop closing of file since there is none
			self.ofile = False

		self.init_screen()
		self.init_vars()

	def set_file(self, file_name):
		self.ofile = open(self.file_name, "r+")

	def init_vars(self):
		self.edited = False
		self.cursor_hidden = False

		self.abs_line = 0
		self.rel_line = 0
		if (self.file_name):
			self.lines = self.ofile.read().split('\n')

		self.status_buffer = ""
		self.command_buffer = ""
		self.error_buffer = ""

		# potential config vars
		self.save_on_exit = True


		self.page = 0
		self.page_length = self.win_h - 1

		self.mode = "n"
		self.key = ""

		self.running = True

	def init_screen(self):
		self.window = curses.initscr()
		self.window.keypad(True)
		self.window.scrollok(1)

		self.win_h, self.win_w = self.window.getmaxyx()

		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)
		curses.start_color()


	def finish(self):
		curses.nocbreak()
		self.window.keypad(False)
		curses.echo()
		curses.endwin()
		if (self.file_name and self.ofile):
			self.ofile.close()

class CommandHandler:
	def __init__(self):
		super(CommandHandler, self).__init__()
		# Different editing modes
		self.commands = {
			"n" : {},
			"g" : {},
			"c" : {},
			"i" : {}
		}
		self.default_key = "_"

	def add_command(self, mode, key, func):
		self.commands[mode][key] = func

	def key_comb(self, mode, key):
		# If the key is not in the mode, but there is a default key in the mode, the default function will be called
		if (key not in self.commands[mode] and self.default_key in self.commands[mode]):
			self.commands[mode][self.default_key](self)
		elif (key in self.commands[mode]):
			self.commands[mode][key](self)


class Window(WindowState, CommandHandler):
	def __init__(self):
		super(Window, self).__init__()

		self.CURSOR_COLOR = 1
		self.NON_CURSOR_COLOR = 2
		self.ERROR_COLOR = 3
		self.COMMAND_COLOR = 4
		curses.init_pair(self.NON_CURSOR_COLOR, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(self.CURSOR_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
		curses.init_pair(self.ERROR_COLOR, curses.COLOR_YELLOW, curses.COLOR_RED)
		curses.init_pair(self.COMMAND_COLOR, curses.COLOR_BLUE, curses.COLOR_BLACK)

	def update(self):
		self.page = self.abs_line // self.page_length
		self.rel_line = self.abs_line % self.page_length
		self.status_buffer = "Mode: %s    File: %s%s    Line %d/%d" % (self.mode, self.file_name if self.file_name else "Empty Buffer", "[+]" if self.edited else "", self.abs_line + 1, len(self.lines))

	def render_lines(self):
		"""Renders the lines in the form of pages. Also handles keyboard input"""
		pages = to_pages(self)
		current_page = pages[self.page]

		for i, line in enumerate(current_page):
			if (len(line) == 0):
				line += " "
			if (i == self.rel_line and not self.cursor_hidden):
				self.window.addstr(line, curses.color_pair(self.CURSOR_COLOR))
			else:
				self.window.addstr(line, curses.color_pair(self.NON_CURSOR_COLOR))
			self.window.addch('\n')

		self.key = self.window.getkey()
		# If there is an error, a key input is eaten
		# Error is removed too fast otherwise
		if (self.error_buffer):
			self.error_buffer = ""
			self.cursor_hidden = False
		else:
			self.key_comb(self.mode, self.key)

	def render_buffer(self):
		"""
		Renders the error buffer only if it is not empty.
		If it is empty, it renders the command buffer.
		Buffers are rendered at the bottom of the screen
		"""
		self.window.move(self.win_h - 1, 0)
		if (self.mode == "c"):
			self.window.addstr(":" + self.command_buffer, curses.color_pair(self.COMMAND_COLOR))
		elif (self.error_buffer):
			self.cursor_hidden = True
			self.window.addstr(self.error_buffer, curses.color_pair(self.ERROR_COLOR))
		else:
			self.window.addstr(self.status_buffer, curses.color_pair(self.COMMAND_COLOR))
		self.window.move(0, 0)
	
	def run(self):
		while self.running:
			self.window.clear()
			self.window.refresh()
			self.update()
			self.render_buffer()
			self.render_lines()


win = Window()
add_all_commands(win)
try:
	win.run()
finally:
	win.finish()
	for i in debug_log:
		print(i)
