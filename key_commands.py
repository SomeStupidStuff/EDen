import re

# General
BACKSPACE = "KEY_BACKSPACE"

def unkown_key_comb(window):
	window.error_buffer = "Unknown key combination %s->%s (Mode->Key)" % (window.mode, window.key.replace("\n", "\\n"))

def add_all_commands(window):
	window.add_command("n", "q", normal_quit_win)
	window.add_command("n", "k", normal_move_up)
	window.add_command("n", "j", normal_move_down)
	window.add_command("n", "O", normal_new_line_up)
	window.add_command("n", "o", normal_new_line_down)
	window.add_command("n", "h", normal_scroll_left)
	window.add_command("n", "l", normal_scroll_right)
	window.add_command("n", "0", normal_start_line)
	window.add_command("n", "$", normal_end_line)
	window.add_command("n", "d", normal_delete_line)
	window.add_command("n", "G", normal_go_bottom_file)
	window.add_command("n", "c", normal_change_line)
	window.add_command("n", "w", normal_write_file)
	window.add_command("n", "g", enter_go_mode)
	window.add_command("n", ":", enter_command_mode)
	window.add_command("n", "i", enter_insert_mode)

	window.add_command("g", "g", go_top_file)
	window.add_command("g", window.default_key, lambda window: (unkown_key_comb(window), enter_normal_mode(window)))

	window.add_command("c", window.default_key, command_add_char)
	window.add_command("c", BACKSPACE, command_delete_char)
	window.add_command("c", "\n", command_execute_command)

	window.add_command("i", window.default_key, insert_add_char)
	window.add_command("i", BACKSPACE, insert_delete_char)
	window.add_command("i", "\n", insert_newline)
	window.add_command("i", chr(27), enter_normal_mode)

# Normal mode
def enter_normal_mode(window):
	window.mode = "n"

def normal_quit_win(window):
	if (window.edited):
		normal_write_file(window)
	window.running = False

def normal_move_up(window):
	if (window.abs_line - 1 < 0):
		return
	window.abs_line -= 1
	normal_end_line(window)

def normal_move_down(window):
	if (window.abs_line + 1 >= len(window.lines)):
		return
	window.abs_line += 1
	normal_end_line(window)

def normal_new_line_up(window):
	window.lines.insert(window.abs_line, "")
	enter_insert_mode(window)

def normal_new_line_down(window):
	window.lines.insert(window.abs_line + 1, "")
	window.abs_line += 1
	enter_insert_mode(window)

def normal_scroll_left(window):
	window.line_offset = max(window.line_offset - 1, 0)

def normal_scroll_right(window):
	window.line_offset = min(window.line_offset + 1, max(len(window.lines[window.abs_line])-window.win_w+1, 0))

def normal_start_line(window):
	window.line_offset = 0

def normal_end_line(window):
	window.line_offset = max(len(window.lines[window.abs_line])-window.win_w+1, 0)

def normal_delete_line(window):
	del window.lines[window.abs_line]
	if (len(window.lines) == 0):
		window.lines.append("")
	elif (window.abs_line >= len(window.lines)):
		normal_move_up(window)

def normal_write_file(window, file_name=""):
	if (window.file_name):
		with open(window.file_name, "w+") as file:
			file.write('\n'.join(window.lines) + '\n')
		window.edited = False
	elif (file_name):
		window.file_name = file_name
		with open(file_name, "w+") as file:
			file.write('\n'.join(window.lines) + '\n')
		window.edited = False
	else:
		window.error_buffer = "File is unnamed"

def normal_go_bottom_file(window):
	window.abs_line = len(window.lines) - 1

def normal_change_line(window):
	window.edited = True
	normal_start_line(window)
	window.lines[window.abs_line] = ""
	enter_insert_mode(window)

# Go mode
def enter_go_mode(window):
	window.mode = "g"

def go_top_file(window):
	window.abs_line = 0
	enter_normal_mode(window)

# Command mode
def enter_command_mode(window):
	window.cursor_hidden = True
	window.mode = "c"

def command_execute_command(window):
	window.command_buffer = window.command_buffer.strip()
	matched = False

	if (window.command_buffer.lower().startswith("q") or window.command_buffer.lower() == "exit"):
		matched = True
		normal_quit_win(window)

	# regex matches

	#  write to
	match_string = r"(wto)\s+(.+)"
	match = re.match(match_string, window.command_buffer)
	if (match):
		matched = True
		normal_write_file(window, match.group(2))

	if (not matched):
		window.error_buffer = "Entered command is incorrect"

	# exit command mode
	enter_normal_mode(window)
	window.command_buffer = ""
	window.cursor_hidden = False

def command_add_char(window):
	window.command_buffer += window.key

def command_delete_char(window):
	if (window.command_buffer == ""):
		enter_normal_mode(window)
	else:
		window.command_buffer = window.command_buffer[:-1]

# Insert mode
def enter_insert_mode(window):
	window.mode = "i"

def insert_add_char(window):
	#TODO: Fix add char scrolling
	window.lines[window.abs_line] += window.key
	normal_scroll_right(window)
	window.edited = True

def insert_delete_char(window):
	normal_scroll_left(window)
	if (window.lines[window.abs_line] == "" and window.abs_line != 0):
		normal_delete_line(window)
		window.abs_line -= 1
	else:
		window.lines[window.abs_line] = window.lines[window.abs_line][:-1]

def insert_newline(window):
	window.lines.insert(window.abs_line + 1, "")
	window.abs_line += 1
