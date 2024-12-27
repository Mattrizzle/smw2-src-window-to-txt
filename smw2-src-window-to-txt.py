import os
import argparse
import re
from itertools import chain
from pathlib import Path

def load_file(path):
	try:
		file = open(path, 'rb')		# Open file in read bytes mode
		while True:
			data = file.read(-1)  
			if not data:
				break
			return data
	except IOError:
		print('ERROR: Failed to open file.')
		exit()

def save_file(path, address, data):
	try:
		file = open(path, 'wb')		# Open file in write bytes mode
		if True:
			file.seek(address)
			file.write(data)
			return
	except IOError:
		print('ERROR: Failed to open file.')
		exit()

parser = argparse.ArgumentParser(prog="smw2-src-window-to-txt", formatter_class=argparse.RawDescriptionHelpFormatter, description="Yoshi's Island Source Window Data to Text Art Converter\nBy Mattrizzle - https://github.com/Mattrizzle/smw2-src-window-to-txt\nThis script converts a window table from a Yoshi's Island source code ASM file \nto an 'ASCII art'-style text file. Additionally, it prints this output to the \nterminal window if it fits.", epilog="Examples:\n  smw2-src-window-to-txt.py ys_play.asm.BAK1 CCHGD0\n  smw2-src-window-to-txt.py ys_game.asm.BAK11 CHGDT4 -f O -b _ -o \"boo.txt\"\n  smw2-src-window-to-txt.py ys_koopa.asm KOOPA_WINDOW_DT -f * -i")
parser.add_argument("infile", metavar="<input file>", help="Source file path.")
parser.add_argument("label", metavar="<label>", help="Label of window table to convert in source file.")
parser.add_argument("-o", "--outfile", metavar="<output file>", type=str, help="Destination file path. Default is \"window-to-txt/<input file>-<label>.txt\".")
parser.add_argument("-b", "--blankchar", metavar="<blank character>", type=str, default=" ", help="Character to use for blank spaces. Default is Space.")
parser.add_argument("-f", "--filledchar", metavar="<filled character>", type=str, default="X", help="Character to use for filled pixels. Default is X.")
parser.add_argument("-i", "--no_invert", action='store_true', help="If included, the output will not be flipped vertically. This is needed for certain images to be output correctly.")

args = parser.parse_args()

print("\n" + parser.prog)
print("-" * len(parser.prog))

if len(args.blankchar) > 1:
	print("The blank character argument should only be 1 character in length. Length of \"" + args.blankchar + "\" is " + str(len(args.blankchar)) + ".")
	exit()
if len(args.filledchar) > 1:
	print("The filled character argument should only be 1 character in length. Length of \"" + args.blankchar + "\" is " + str(len(args.filledchar)) + ".")
	exit()

if not args.outfile:
	output_path = "window-to-txt/" + args.infile + "-" + args.label + ".txt"
else:
	output_path = args.outfile

output_path_parts = output_path.replace("\\", "/").split("/")	# Split the entered file path into multiple list items on slashes and backslashes

output_filename = output_path_parts.pop()	# Remove the last entry in the list and populate this variable. This should contain the filename, but not the name of any folders.

if len(output_path_parts) > 0:
	output_directory = '/'.join(output_path_parts)
	Path(output_directory).mkdir(parents=True, exist_ok=True)

src_data = load_file(args.infile)

src_data_text = src_data.decode("shift_jis", "replace")		# Decode from Shift-JIS, replace values that can't be decoded with 0xFFFD

# Pattern for entire block of data associated with the specified window label
pattern = args.label + "[ \\t]{1,}EQU[ \\t]{1,}\\$(?:[ \\t0-9A-Za-z\\u3040-\\u30FF\\u3400-\\u4DBF\\u4E00-\\u9FFF\\.\\;]*)\\n;*[ \\t]{1,}(?:WORD[ \\t]{1,}CIPCHD\\+[0-9A-F]{4}H\\+[0-9A-F]{4}H\\n)*;*[ \\t]{1,}HEX[ \\t]{1,}([0-9A-F]{2})\\n(?:;*[ \\t]{1,}HEX[ \\t]{1,}(?:(?:[0-9A-F]{2}),(?:[0-9A-F]{2})(?:,[ ]{0,1})(?:[0-9A-F]{2}),(?:[0-9A-F]{2})(?:,[ ]{0,1}){0,2}){1,4}(?:[ \\t]{1};\\[(?:[0-9A-F]{2})\\]){0,1}\\n){1,}"
match = re.search(pattern, src_data_text)

if match:
	matched_string = match.group()
	height = int(match.group(1), 16)

	pattern2 = r'([0-9A-F]{2}),([0-9A-F]{2}),[ ]{0,1}([0-9A-F]{2}),([0-9A-F]{2})'	# Pattern for set of hex values defining a single line

	window_rows = re.findall(pattern2, matched_string)

	if height == len(window_rows):
		# Convert list of tuples containing hex values to list of lists containing integers
		# If args.no_invert is not set, the reversed() function will be run is so that rows are buttom to top.
		if args.no_invert:
			window_rows_list = [list(map(lambda x:int(x,16),s)) for s in window_rows]
		else:
			window_rows_list = [list(map(lambda x:int(x,16),s)) for s in reversed(window_rows)]

		min_value = min(chain.from_iterable(window_rows_list))	# Minimum overall value (leftmost coordinate) of all window data associated with the specified label
		max_value = max(chain.from_iterable(window_rows_list))	# Maximum overall value (rightmost coordinate) of all window data associated with the specified label

		terminal_window_width = os.get_terminal_size().columns	# Width of terminal window

		width = max_value + 1 - min_value	# Width of window data associated with the specified label

		# This is to prevent output that is too wide from wrapping to the next line.
		if width > terminal_window_width:
			print("Output is too wide for the terminal window, so it will not be printed.")
			no_print = True
		else:
			no_print = False

		string_buffers = []	# Will be a list of lines that used to build the final output for printing and saving.

		i = 0
		while i < height:						# Add "blank" strings to the list for each line of the output
			string_buffers.append(args.blankchar * width + "\n")	# consisting of blank characters spanning the width of the output followed by a newline.
			i += 1

		for i, s in enumerate(window_rows_list):
			if len(set(s)) == 1:
				continue
			elif s[1] == s[2]:		# If middle two values match, the windows intersect and can be treated as a single continuous one
				pos1 = s[0]-min_value	# Minimum x-coordinate of first window on the line, minus any offset
				pos2 = s[3]-min_value	# Maximum x-coordinate of second window on the line, minus any offset
				length = pos2-pos1+1	# Difference in two positions above, plus one
	
				if pos1 == 0 and pos2 == width-1:	# If image is filled from left to right edge
					string_buffers[i]=(args.filledchar * length)
				elif pos1 == 0:				# If only the left edge is filled
					string_buffers[i]=(args.filledchar * length)+string_buffers[i][pos2:width-1]
				elif pos2 == width-1:			# If only the right edge is filled
					string_buffers[i]=string_buffers[i][0:pos1] + (args.filledchar * length)
				else:					# If neither edge is filled
					string_buffers[i]=string_buffers[i][0:pos1] + (args.filledchar * length) + string_buffers[i][pos2:width-1]
			else:
				pos1 = s[0]-min_value	# Minimum x-coordinate of first window on the line, minus any offset
				pos2 = s[1]-min_value	# Maximum x-coordinate of first window on the line, minus any offset
				pos3 = s[2]-min_value	# Minimum x-coordinate of second window on the line, minus any offset
				pos4 = s[3]-min_value	# Maximum x-coordinate of second window on the line, minus any offset
				length1 = pos2-pos1+1	# Difference in two positions of first window, plus one
				length2 = pos4-pos3+1	# Difference in two positions of second window, plus one

				if pos1 == 0 and pos4 == width-1:	# If image is filled from left to right edge
					string_buffers[i]=(args.filledchar * length1) + string_buffers[i][pos2:pos3-1] + (args.filledchar * length2)
				elif pos1 == 0:				# If only the left edge is filled
					string_buffers[i]=(args.filledchar * length1) + string_buffers[i][pos2:pos3-1] + (args.filledchar * length2) + string_buffers[i][pos4:width-1]
				elif pos4 == width-1:			# If only the right edge  is filled
					string_buffers[i]=string_buffers[i][0:pos1] + (args.filledchar * length1) + string_buffers[i][pos2:pos3-1] + (args.filledchar * length2)
				else:					# If neither edge is filled
					string_buffers[i]=string_buffers[i][0:pos1] + (args.filledchar * length1) + string_buffers[i][pos2:pos3-1] + (args.filledchar * length2) + string_buffers[i][pos4:width-1]
			
			if not no_print:		 # If the output isn't too wide for the terminal window,
				print(string_buffers[i]) # print it.
			
		combined_buffers = '\n'.join(string_buffers).encode('utf-8')	# Combine the list of buffers to make 
		save_file(output_path, 0, combined_buffers)

		file = Path(output_path)
		if file.exists() and file.stat().st_size == len(combined_buffers):
			print("Saved \"" + output_path + "\"")
	else:
		print("Length byte (" + str(height) + ") doesn't match number of rows in the data (" + str(len(window_rows)) + ").")
		exit()
else:
	print("Window table with label " + args.label + " not found in " + args.infile + ", or does not fit the syntax expected by this script.")