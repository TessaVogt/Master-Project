import sys

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



def getLetterCoords(letter, sFnt, sPnt):
    ascii_num = ord(letter)
    letter_coords = []

    if ascii_num < 32 or (ascii_num > 127 and ascii_num < 160) or ascii_num > 255:
        sys.stderr.write("Invalid character '{}'\n".format(letter))
        return letter_coords

    if sFnt[ascii_num].wNum == 0:
        sys.stderr.write("Character '{}' not found\n".format(letter))
        return letter_coords

    width = sFnt[ascii_num].wWid

    # First Entry in List: ['C', asciizahl, wWid]
    letter_coords.append(['C', ascii_num, width])

    start_offset = sFnt[ascii_num].wOff

    for i in range(start_offset, start_offset + sFnt[ascii_num].wNum):
        point = sPnt[i]
        letter_coords.append([point.bTyp, point.nX, point.nY])

    return letter_coords


def writeLetterCoords(coordsCode):
    with open("handwriting.fnt", "w") as f:
        first_entry = coordsCode[0]
        ascii_char = first_entry[1]
        f.write("! >{}<\n".format(chr(ascii_char)))

        for entry in coordsCode:
            letter, x, y = entry
            f.write("{} {} {}\n".format(letter, x, y))