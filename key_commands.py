# General
BACKSPACE = "KEY_BACKSPACE"

def unkown_key_comb(window):
	window.error_buffer = "Unknown key combination %s->%s (Mode->Key)" % (window.mode, window.key.replace("\n", "\\n"))

def add_all_commands(window):
	window.add_command("n", "q", normal_quit_win)
	window.add_command("n", "k", normal_move_up)
	window.add_command("n", "j", normal_move_down)
	window.add_command("n", "d", normal_delete_line)
	window.add_command("n", "G", normal_go_bottom_file)
	window.add_command("n", "c", normal_change_line)
	window.add_command("n", "w", normal_write_file)
	window.add_command("n", "g", enter_go_mode)
	window.add_command("n", "i", enter_insert_mode)

	window.add_command("g", "g", go_top_file)
	window.add_command("g", window.default_key, lambda window: (unkown_key_comb(window), enter_normal_mode(window)))

	window.add_command("i", window.default_key, insert_add_char)
	window.add_command("i", BACKSPACE, insert_delete_char)
	window.add_command("i", "\n", enter_normal_mode)

# Normal mode
def enter_normal_mode(window):
	window.mode = "n"

def normal_quit_win(window):
	window.running = False

def normal_move_up(window):
	if (window.abs_line - 1 < 0):
		return
	window.abs_line -= 1

def normal_move_down(window):
	if (window.abs_line + 1 >= window.max_lines):
		return
	window.abs_line += 1

def normal_delete_line(window):
	del window.lines[window.abs_line]
	if (window.max_lines == 0):
		window.lines.append("")
	elif (window.abs_line >= window.max_lines):
		normal_move_up(window)

def normal_write_file(window):
	window.edited = False
	with open(window.file_name, "w+") as file:
		file.write('\n'.join(window.lines) + '\n')

def normal_go_bottom_file(window):
	window.abs_line = window.max_lines - 1

def normal_change_line(window):
	window.edited = True
	window.lines[window.abs_line] = ""
	enter_insert_mode(window)

# Go mode
def enter_go_mode(window):
	window.mode = "g"

def go_top_file(window):
	window.abs_line = 0
	enter_normal_mode(window)

# Insert
def enter_insert_mode(window):
	window.mode = "i"

def insert_add_char(window):
	window.lines[window.abs_line] += window.key
	window.edited = True

def insert_delete_char(window):
	window.lines[window.abs_line] = window.lines[window.abs_line][:-1]
