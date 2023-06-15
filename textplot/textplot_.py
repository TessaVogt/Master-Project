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

    if len(sys.argv) != 5: # not enough input arguments
        errorinfo()
        print("Not enough input arguments:")
        print("Please use: ")
        return False
    
    # Config File Definition -----------------------------------------------------------------
    try:
        with open(defFile, "r") as fDefFile:
            with open(defFile, "r") as fDefFile:
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

    except IOError:
        errorinfo()
        print("Can't open basic definitions file '%s'" % defFile)
        return False
    
    # Font File Analysis ----------------------------------------------------------------------
    sFnt = [StrFnt() for _ in range(256)]
    sPnt = [StrPnt() for _ in range(10000)]
    wChr = 0
    wPnt = 0

    if sPnt is None:
        sys.stderr.write("Not enough memory !\n")
        sys.exit(1)

    try:
        with open(fontFile, "r") as fFontFile:
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

    except FileNotFoundError:
        sys.stderr.write("Can't open font file '{}'\n".format(fontFile))
        sys.exit(1)

    # Text File -------------------------------------------------------------------------------
    
    # ....

    return True

# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # try:
    parser = argparse.ArgumentParser()
    parser.add_argument("defFile", help="Path to the definition file")
    parser.add_argument("fontFile", help="Path to the font file")
    parser.add_argument("textFile", help="Path to the text file")
    parser.add_argument("gCodeFile", help="Path to the output GCode file")
    args = parser.parse_args()
    main(args.defFile, args.fontFile, args.textFile, args.gCodeFile)
    print("Execution completed successfully.")
    # except:
    #     print("An error occurred during execution.")