import sys
import argparse


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

# offset
wXoff = 0
wYoff = 0
wZoff = 0
wLift = 50          # uplift no print
wNextLine = 500     # next line offset
wFontScale = 100    # font scale
# speed
wPlotSpeed = 500
wEmptySpeed = 1000

def writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile):
    for wI in range(sFnt[bChr].wNum):
        if wI == 0 or sPnt[sFnt[bChr].wOff + wI].bTyp == 'P':
            # First point we always lift!
            fgCodeFile.write("G1 F{:04d} Z{:05.3f}\n".format(wEmptySpeed, (wZoff + wLift) / 100.0))
            wPlot += 1
        elif wI > 0 and sPnt[sFnt[bChr].wOff + wI - 1].bTyp == 'P' and sPnt[sFnt[bChr].wOff + wI].bTyp == 'L':
            # Move down if last point is lifted
            fgCodeFile.write("G1 Z{:05.3f} F{:04d}\n".format(wZoff / 100.0, wPlotSpeed))
            wPlot += 1

        fgCodeFile.write("G1 Y{:05.3f} X{:05.3f}\n".format(fX + sPnt[sFnt[bChr].wOff + wI].nX * wFontScale / 100.0,
                                                            fY - sPnt[sFnt[bChr].wOff + wI].nY * wFontScale / 100.0))
        wPlot += 1
    return wPlot


def errorinfo():
    print("\n")
    print("Call: textplot def-file font-file text-file gcode-file\n"
          "\tdef-file   -> basic definitions\n"
          "\tfont-file  -> font description\n"
          "\ttext-file  -> ASCII text to plot\n"
          "\tgcode-file -> GCODE file for 3D printer\n")

# --------------------------------------------------------------------------------------------
def create_gcode(defFile, fontFile, textFile, gCodeFile):
    print("TEXTPLOT version 0.1, Copyright (C) 2023 Tessa Vogt, Muenster, Germany")
    
    # Config File Definition -----------------------------------------------------------------
    try:
        fDefFile = open(defFile, "r")
    except IOError:
        errorinfo()
        print("Can't open basic definitions file '%s'" % defFile)
        return False
                
    for line in fDefFile:
        line = line.strip()  # delete line skips and empty lines

        if not line:  # skip empty lines
            continue

        parts = line.split()  # split line in seperate parts

        pCmd = parts[0]  # first element is argument name

        if pCmd == "zeropoint":
            if len(parts) < 4:
                print("Wrong parameter for definition 'zeropoint'")
                break

            wXoff = int(parts[1])
            wYoff = int(parts[2])
            wZoff = int(parts[3])
        elif pCmd == "emptylift":
            if len(parts) < 2:
                print("Wrong parameter for definition 'emptylift'")
                break

            wLift = int(parts[1])
        elif pCmd == "emptyspeed":
            if len(parts) < 2:
                print("Wrong parameter for definition 'emptyspeed'")
                break

            wEmptySpeed = int(parts[1])
        elif pCmd == "plotspeed":
            if len(parts) < 2:
                print("Wrong parameter for definition 'plotspeed'")
                break

            wPlotSpeed = int(parts[1])
        elif pCmd == "nextline":
            if len(parts) < 2:
                print("Wrong parameter for definition 'nextline'")
                break

            wNextLine = int(parts[1])
        elif pCmd == "fontscale":
            if len(parts) < 2:
                print("Wrong parameter for definition 'fontscale'")
                break

            wFontScale = int(parts[1])
        else:
            print("Unknown definition:", pCmd)

    # for testing:
    print(f" wXoff: {wXoff}, wYoff: {wYoff}, wZoff: {wZoff}")
    print(f" wLift: {wLift}\n wEmptySpeed: {wEmptySpeed}\n wPlotSpeed: {wPlotSpeed}\n wNextLine: {wNextLine}\n wFontScale: {wFontScale}")

    fDefFile.close()
    
    # Font File Analysis ----------------------------------------------------------------------
    sFnt = [StrFnt() for _ in range(256)]
    sPnt = [StrPnt() for _ in range(10000)]
    wChr = 0
    wPnt = 0

    if sPnt is None:
        sys.stderr.write("Not enough memory !\n")
        sys.exit(1)

    try:
        fFontFile = open(fontFile, "r")
    except FileNotFoundError:
        sys.stderr.write("Can't open font file '{}'\n".format(fontFile))
        sys.exit(1)

    # initialize
    sFnt[0].wOff = 0

    for wI in range(256):
        sFnt[wI].wNum = 0
        sFnt[wI].wWid = 0

    for line in fFontFile:              
        if not line.startswith('!'):
            cFnc, nX, nY = line.strip().split()
            cFnc = cFnc.upper() # converts letter to upper letter if necessary
            # print(f"Line: {line}extracted to:\n\tcFnc: {cFnc}\n\tnX: {nX}\n\tnY:{nY}")

            if cFnc == 'C' or cFnc == 'P' or cFnc == 'L':
                try:
                    nX = int(nX)
                    nY = int(nY)
                except ValueError:
                    sys.stderr.write(f"Invalid data format in font file {fontFile} in line '{line}'\n")
                    sys.exit(1)

                if cFnc == 'C':
                    if nX < 32 or (nX > 127 and nX < 160) or nX > 255:
                        sys.stderr.write("Wrong char '{}' in font file '{}'\n".format(nX, fontFile))
                        sys.exit(1)
                    else:
                        if nY < 0 or nY > 256:
                            sys.stderr.write("Wrong char width '{}' in font file '{}'\n".format(nY, fontFile))
                            sys.exit(1)
                        else:
                            if sFnt[nX].wNum:
                                sys.stderr.write("Double char def '{}' in font file '{}'\n".format(nX, fontFile))
                                sys.exit(1)

                            wChr = nX
                            sFnt[wChr].wOff = wPnt
                            sFnt[wChr].wWid = nY
                else: # if P or L
                    sPnt[wPnt].bTyp = cFnc

                    if nX > 256 or nX < -256 or nY > 256 or nY < -256:
                        sys.stderr.write("Wrong fnt pos for char '{}' in font file '{}'\n".format(wChr, fontFile))
                        sys.exit(1)
                    else:
                        sFnt[wChr].wNum += 1
                        sPnt[wPnt].nX = nX
                        sPnt[wPnt].nY = nY
                        wPnt += 1

                        if wPnt > 9999:
                            sys.stderr.write("Too much points in font file '{}'\n".format(fontFile))
                            sys.exit(1)
                # print(f"wChr: {wChr}, ASCII: {chr(wChr)}")
            else:
                sys.stderr.write("Wrong definition in font file '{}'\n".format(fontFile))
                sys.exit(1)
    fFontFile.close()

    # Generate G-Code from Text File ---------------------------------------------------------------
    try:
        fTextFile = open(textFile, "r", encoding="utf-8")
    except FileNotFoundError:
        sys.stderr.write("Can't open text file '{}'\n".format(textFile))
        sys.exit(1)
    try:
        fgCodeFile = open(gCodeFile, "w")
    except FileNotFoundError:
        sys.stderr.write("Can't open gCode file '{}'\n".format(gCodeFile))
        sys.exit(1)

    fgCodeFile.write("M104 S0 ;no extruder heating\n"
                    "M190 S0 ;no bed heating\n"
                    "M107 ;set the fan off\n"
                    "M204 S2000 ;set starting acceleration ?\n"
                    "M205 X13 Y13 ;set max jerk\n"
                    "G21 ;metric values\n"
                    "G90 ;absolute positioning\n"
                    "G1 F3000 Z50.000 ;move the pen up 50mm for secure\n"
                    "G28 ;homing all axis\n")
    fX = float(wXoff) / 100.0
    fY = float(wYoff) / 100.0
    wChar = 0
    wWord = 0
    wLine = 0
    wPlot = 0
    for line in fTextFile:
        for char in line:
            bChr = ord(char)
            if bChr == 255:  # End of file
                break

            if bChr > 31: # non-printable control characters are skipped
                fgCodeFile.write(";char >{}<\n".format(chr(bChr)))

                if sFnt[bChr].wWid:  # The char is defined
                    for wI in range(sFnt[bChr].wNum):
                        if wI == 0 or sPnt[sFnt[bChr].wOff + wI].bTyp == 'P':
                            # First point we always lift!
                            fgCodeFile.write("G1 F{:04d} Z{:05.3f}\n".format(wEmptySpeed, (wZoff + wLift) / 100.0))
                            wPlot += 1
                        elif wI > 0 and sPnt[sFnt[bChr].wOff + wI - 1].bTyp == 'P' and sPnt[sFnt[bChr].wOff + wI].bTyp == 'L':
                            # Move down if last point is lifted
                            fgCodeFile.write("G1 Z{:05.3f} F{:04d}\n".format(wZoff / 100.0, wPlotSpeed))
                            wPlot += 1

                        fgCodeFile.write("G1 Y{:05.3f} X{:05.3f}\n".format(fX + sPnt[sFnt[bChr].wOff + wI].nX * wFontScale / 100.0,
                                                                            fY - sPnt[sFnt[bChr].wOff + wI].nY * wFontScale / 100.0))
                        wPlot += 1

                    fX += sFnt[bChr].wWid * wFontScale / 100.0
                # --------------------------------------------------------------------------
                else: # char not defined
                    if bChr == 228: # ä
                        bChr_list = [97, 101] # a, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)
                                
                    elif bChr == 246: # ö
                        bChr_list = [111, 101] # o, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)
                    
                    elif bChr == 252: # ü
                        bChr_list = [117, 101] # u, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)
                    
                    elif bChr == 196: # Ä
                        bChr_list = [65, 101] # A, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)
                    
                    elif bChr == 214: # Ö
                        bChr_list = [79, 101] # O, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)

                    elif bChr == 220: # Ü
                        bChr_list = [85, 101] # U, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)

                    elif bChr == 223: # ß
                        bChr_list = [115, 115] # s, s
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile)
                # --------------------------------------------------------------------------
                wChar += 1

                if bChr == 32:
                    wWord += 1
            elif bChr == 10:
                fgCodeFile.write(";linefeed\n")
                wLine += 1
                wWord += 1

                fX = float(wXoff) / 100.0
                fY = float(wYoff) / 100.0 + wNextLine * wFontScale / 100.0 * wLine

    # End sequence
    fgCodeFile.write("G1 F3000 Z50.000 X 0.000 ;move the pen up and move up\n")
    fTextFile.close()
    fgCodeFile.close()
    

    sys.stdout.write("Create gcode output successful for\n"
                 "{:5d} character in\n"
                 "{:5d} words in\n"
                 "{:5d} line(s) that generates\n"
                 "{:5d} plot commands\n".format(wChar, wWord, wLine + 2, wPlot))

    return True

# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # change these according to your needs
    fontname = 'Tessa'
    defFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/default.ini'
    # textFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/text_sample.txt'
    textFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/abstract.txt'	


    # DON'T CHANGE THESE
    # fontFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/test.fnt'
    fontFile = f'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/Flask/fonts/handwriting_{fontname}.fnt'
    gCodeFile = f'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/{fontname}_gCode.gcode'
    create_gcode(defFile, fontFile, textFile, gCodeFile)
    