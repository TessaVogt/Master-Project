import sys
import os

class StrFnt:
    def __init__(self):
        self.wOff = 0  # Offset of first point
        self.wNum = 0  # Number of points
        self.wWid = 0  # Width of char

class StrPnt:
    def __init__(self):
        self.bTyp = 0  # Plottype
        self.nX = 0    # Offset points
        self.nY = 0


def parse_font_file(font_path):
    sFnt = [StrFnt() for _ in range(256)]
    sPnt = [StrPnt() for _ in range(10000)]
    wChr = 0
    wPnt = 0

    if sPnt is None:
        sys.stderr.write("Not enough memory!\n")
        sys.exit(1)

    try:
        fPerfectFontFile = open(font_path, "r")
    except FileNotFoundError:
        sys.stderr.write("Can't open font file '{}'\n".format(font_path))
        sys.exit(1)

    # initialize
    sFnt[0].wOff = 0

    for wI in range(256):
        sFnt[wI].wNum = 0
        sFnt[wI].wWid = 0

    for line in fPerfectFontFile:
        if not line.startswith('!'):
            cFnc, nX, nY = line.strip().split()
            cFnc = cFnc.upper()  # converts letter to upper letter if necessary
            # print(f"Line: {line}extracted to:\n\tcFnc: {cFnc}\n\tnX: {nX}\n\tnY:{nY}")

            if cFnc == 'C' or cFnc == 'P' or cFnc == 'L':
                try:
                    nX = int(nX)
                    nY = int(nY)
                except ValueError:
                    sys.stderr.write(f"Invalid data format in font file {font_path} in line '{line}'\n")
                    sys.exit(1)

                if cFnc == 'C':
                    if nX < 32 or (nX > 127 and nX < 160) or nX > 255:
                        sys.stderr.write("Wrong char '{}' in font file '{}'\n".format(nX, font_path))
                        sys.exit(1)
                    else:
                        if nY < 0 or nY > 256:
                            sys.stderr.write("Wrong char width '{}' in font file '{}'\n".format(nY, font_path))
                            sys.exit(1)
                        else:
                            if sFnt[nX].wNum:
                                sys.stderr.write("Double char def '{}' in font file '{}'\n".format(nX, font_path))
                                sys.exit(1)

                            wChr = nX
                            sFnt[wChr].wOff = wPnt
                            sFnt[wChr].wWid = nY
                else:  # if P or L
                    sPnt[wPnt].bTyp = cFnc

                    if nX > 256 or nX < -256 or nY > 256 or nY < -256:
                        sys.stderr.write(
                            "Wrong fnt pos for char '{}' in font file '{}'\n".format(wChr, font_path))
                        sys.exit(1)
                    else:
                        sFnt[wChr].wNum += 1
                        sPnt[wPnt].nX = nX
                        sPnt[wPnt].nY = nY
                        wPnt += 1

                        if wPnt > 9999:
                            sys.stderr.write("Too much points in font file '{}'\n".format(font_path))
                            sys.exit(1)
                # print(f"wChr: {wChr}, ASCII: {chr(wChr)}")
            else:
                sys.stderr.write("Wrong definition in font file '{}'\n".format(font_path))
                sys.exit(1)
    fPerfectFontFile.close()

    return sFnt, sPnt



def getLetterCoords(ascii_num, sFnt, sPnt):
    letter_coords = []

    if ascii_num < 32 or (ascii_num > 127 and ascii_num < 160) or ascii_num > 255:
        sys.stderr.write("Invalid character '{}'\n".format(ascii_num))
        return letter_coords

    if sFnt[ascii_num].wNum == 0:
        sys.stderr.write("Character '{}' not found\n".format(ascii_num))
        return letter_coords

    width = sFnt[ascii_num].wWid

    # First Entry in List: ['C', asciizahl, wWid]
    letter_coords.append(['C', ascii_num, width])

    start_offset = sFnt[ascii_num].wOff

    for i in range(start_offset, start_offset + sFnt[ascii_num].wNum):
        point = sPnt[i]
        letter_coords.append([point.bTyp, point.nX, point.nY])

    return letter_coords


def writeLetterCoords(coordsCode, folder_name):
    with open("handwriting_" + folder_name + ".fnt", "a+") as f:
        first_entry = coordsCode[0]
        ascii_char = first_entry[1]
        f.write("! >{}<\n".format(chr(ascii_char)))

        for entry in coordsCode:
            letter, x, y = entry
            f.write("{} {} {}\n".format(letter, x, y))
    return True



def extract_file_info(folder_path, folder_name):
    # Create the path to the folder
    subfolder_path = os.path.join(folder_path, folder_name)

    file_info_list = []

    # Browse all files in the folder
    for file in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file)

        # Check if it is a file
        if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpeg', '.jpg')):
            # Check which abbreviation is present in the file name
            capital_letter = False
            if "_uc_" in file:
                category = "_uc_"
                capital_letter = True
            elif "_lc_" in file:
                category = "_lc_"
            elif "_pm_" in file:
                category = "_pm_"
            elif "_digit_" in file:
                category = "_digit_"
            else:
                raise ValueError("No Category Found")

            # Extract the letter
            file_name = os.path.splitext(file)[0]  # Filename without extension
            if category in file_name:
                letter = file_name.split(category, 1)[1]
                try:
                    letter_ascii = ord(letter)
                except:
                    if letter == "and":
                        letter_ascii = 38
                    elif letter == "hashtag":
                        letter_ascii = 35
                    elif letter == "hyphen":
                        letter_ascii = 45
                    elif letter == "open_parenthesis":
                        letter_ascii = 40
                    elif letter == "close_parenthesis":
                        letter_ascii = 41
                    elif letter == "euro":
                        letter_ascii = 8364
                    elif letter == "quotation_marks_above":
                        letter_ascii = 34
                    elif letter == "quotation_marks_below":
                        letter_ascii = 44              # not existing
                    elif letter == "at_sign":
                        letter_ascii = 64
                    elif letter == "exclamation_mark":
                        letter_ascii = 33
                    elif letter == "percent":
                        letter_ascii = 37
                    elif letter == "comma":
                        letter_ascii = 44
                    elif letter == "period":
                        letter_ascii = 46
                    elif letter == "question_mark":
                        letter_ascii = 63
                    elif letter == "simicolon":
                        letter_ascii = 59
                    elif letter == "colon":
                        letter_ascii = 58

                file_info = {
                    "file": file,
                    "letter": letter_ascii,
                    "category": category,
                    "capital_letter": capital_letter
                }
                file_info_list.append(file_info)
            else:
                raise ValueError("Category was not found in Filename")

    return file_info_list