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
        self.nX = 0    # Coordinate points
        self.nY = 0


def errorinfo():
    print("\n")
    print("Call: textplot def-file font-file text-file gcode-file\n"
          "\tdef-file   -> basic definitions\n"
          "\tfont-file  -> font description\n"
          "\ttext-file  -> ASCII text to plot\n"
          "\tgcode-file -> GCODE file for 3D printer\n")

# --------------------------------------------------------------------------------------------
def main(defFile, fontFile, textFile, gCodeFile):
    print("TEXTPLOT version 0.1, Copyright (C) 2023 Tessa Vogt, Muenster, Germany")

    if sys.gettrace() is None and len(sys.argv) != 5: # not enough input arguments
        print("Not enough input arguments:")
        print("Please use: ")
        errorinfo()
        return False
    settings = config_file_definition(defFile)
    sFnt, sPnt = get_font_data(fontFile)
    generate_gcode_for_text(gCodeFile, textFile, sFnt, sPnt, settings)
    

    return True

def config_file_definition(defFile):    
    # Config File Definition -----------------------------------------------------------------
    # offset
    settings = {
        "wXoff": 0,
        "wYoff": 0,
        "wZoff": 0,
        "wLift": 50,
        "wNextLine": 500,
        "wFontScale": 100,
        "wPlotSpeed": 500,
        "wEmptySpeed": 1000
        }

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

            settings["wXoff"] = int(parts[1])
            settings["wYoff"] = int(parts[2])
            settings["wZoff"] = int(parts[3])
        elif pCmd == "emptylift":
            if len(parts) < 2:
                print("Wrong parameter for definition 'emptylift'")
                break

            settings["wLift"] = int(parts[1])
        elif pCmd == "emptyspeed":
            if len(parts) < 2:
                print("Wrong parameter for definition 'emptyspeed'")
                break

            settings["wEmptySpeed"] = int(parts[1])
        elif pCmd == "plotspeed":
            if len(parts) < 2:
                print("Wrong parameter for definition 'plotspeed'")
                break

            settings["wPlotSpeed"] = int(parts[1])
        elif pCmd == "nextline":
            if len(parts) < 2:
                print("Wrong parameter for definition 'nextline'")
                break

            settings["wNextLine"] = int(parts[1])
        elif pCmd == "fontscale":
            if len(parts) < 2:
                print("Wrong parameter for definition 'fontscale'")
                break

            settings["wFontScale"] = int(parts[1])
        else:
            print("Unknown definition:", pCmd)

    # for testing:
    print(f' wXoff: {settings["wXoff"]}, wYoff: {settings["wYoff"]}, wZoff: {settings["wZoff"]}')
    print(f' wLift: {settings["wLift"]}\n wEmptySpeed: {settings["wEmptySpeed"]}\n wPlotSpeed: {settings["wPlotSpeed"]}\n wNextLine: {settings["wNextLine"]}\n wFontScale: {settings["wFontScale"]}')

    fDefFile.close()
    return settings


def get_font_data(fontFile):
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
    return sFnt, sPnt


def writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings):
    for wI in range(sFnt[bChr].wNum):
        if wI == 0 or sPnt[sFnt[bChr].wOff + wI].bTyp == 'P':
            # First point we always lift!
            fgCodeFile.write("G1 F{:04d} Z{:05.3f}\n".format(settings["wEmptySpeed"], (settings["wZoff"] + settings["wLift"]) / 100.0))
            wPlot += 1
        elif wI > 0 and sPnt[sFnt[bChr].wOff + wI - 1].bTyp == 'P' and sPnt[sFnt[bChr].wOff + wI].bTyp == 'L':
            # Move down if last point is lifted
            fgCodeFile.write("G1 Z{:05.3f} F{:04d}\n".format(settings["wZoff"] / 100.0, settings["wPlotSpeed"]))
            wPlot += 1

        fgCodeFile.write("G1 Y{:05.3f} X{:05.3f}\n".format(fX + sPnt[sFnt[bChr].wOff + wI].nX * settings["wFontScale"] / 100.0,
                                                            fY - sPnt[sFnt[bChr].wOff + wI].nY * settings["wFontScale"] / 100.0))
        wPlot += 1
    fX += sFnt[bChr].wWid * settings["wFontScale"] / 100.0
    return wPlot, fX


def generate_gcode_for_text(gCodeFile, textFile, sFnt, sPnt, settings):
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
    fX = float(settings["wXoff"]) / 100.0
    fY = float(settings["wYoff"]) / 100.0
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
                    wPlot, fX = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)

                # --------------------------------------------------------------------------
                else: # char not defined
                    if bChr == 228: # ä
                        bChr_list = [97, 101] # a, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)
                                
                    elif bChr == 246: # ö
                        bChr_list = [111, 101] # o, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)
                    
                    elif bChr == 252: # ü
                        bChr_list = [117, 101] # u, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot, fX = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)

                    
                    elif bChr == 196: # Ä
                        bChr_list = [65, 101] # A, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)
                    
                    elif bChr == 214: # Ö
                        bChr_list = [79, 101] # O, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)

                    elif bChr == 220: # Ü
                        bChr_list = [85, 101] # U, e
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)

                    elif bChr == 223: # ß
                        bChr_list = [115, 115] # s, s
                        for bChr in bChr_list:
                            if sFnt[bChr].wWid:  # The char is defined
                                wPlot = writeCharInGCode(bChr, sFnt, sPnt, fX, fY, wPlot, fgCodeFile, settings)
                # --------------------------------------------------------------------------
                wChar += 1

                if bChr == 32:
                    wWord += 1
            elif bChr == 10:
                fgCodeFile.write(";linefeed\n")
                wLine += 1
                wWord += 1

                fX = float(settings["wXoff"]) / 100.0
                fY = float(settings["wYoff"]) / 100.0 + settings["wNextLine"] * settings["wFontScale"] / 100.0 * wLine

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
    # differentiate between running in debug mode or not
    if sys.gettrace() is not None:
        # Debug-Modus
        defFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/default.ini'
        # fontFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/test.fnt'
        fontFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/Flask/handwriting_Test.fnt'
        textFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/test.txt'
        gCodeFile = 'c:/Users/tvogt/OneDrive/Dokumente/GitHub/Master-Project/textplot/Test_gCode.gcode'
        main(defFile, fontFile, textFile, gCodeFile)
        
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("defFile", help="Path to the definition file")
        parser.add_argument("fontFile", help="Path to the font file")
        parser.add_argument("textFile", help="Path to the text file")
        parser.add_argument("gCodeFile", help="Path to the output GCode file")
        args = parser.parse_args()
        main(args.defFile, args.fontFile, args.textFile, args.gCodeFile)