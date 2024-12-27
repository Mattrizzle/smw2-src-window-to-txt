# Yoshi's Island Source Window Data to Text Art Converter
This script converts a window table from a Yoshi's Island source code ASM file to an 'ASCII art'-style text file. Additionally, it prints this output to the terminal window if it fits.

Tested with Python 3.8.5 on Windows 7.

### Usage:
smw2-src-window-to-txt \[-h\] \<input file\> \<label\> \[-o \<output file\>\] \[-b \<blank character\>\] \[-f \<filled character\>\] \[-i\]
                              
### Positional arguments:
  \<input file\>        Source file path.
 
  \<label\>             Label of window table to convert in source file.

### Optional arguments:
  -h, --help            Show help message and exit.
  
  -o, \<output file\>, --outfile \<output file\>
    
                        Destination file path. Default is "window-to-txt/\<input file\>-\<label\>.txt".
  
  -b \<blank character\>, --blankchar \<blank character\>

                        Character to use for blank spaces. Default is Space.

  -f \<filled character\>, --filledchar \<filled character\>

                        Character to use for filled pixels. Default is X.

  -i, --no_invert       If included, the output will not be flipped vertically. This is needed for certain images to be output correctly.

  -c, --ignore_commented_out

                        If included, data blocks with at least one semicolon at the start of their lines will be ignored.

### Examples:
  smw2-src-window-to-txt.py ys_play.asm.BAK1 CCHGD0

  smw2-src-window-to-txt.py ys_game.asm.BAK11 CHGDT4 -f O -b _ -o "boo.txt"

  smw2-src-window-to-txt.py ys_koopa.asm KOOPA_WINDOW_DT -f * -i

  smw2-src-window-to-txt.py ys_play.asm.BAK17 CCHGDN -c