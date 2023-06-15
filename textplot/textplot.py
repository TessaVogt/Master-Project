import sys


class StrFnt:
    def __init__(self):
        self.wOff = 0  # Offset of first point
        self.wNum = 0  # Number of points
        self.wWid = 0  # Width of char

sFnt = [StrFnt() for _ in range(256)]

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
def main(fileDef, argv1, argv2, argv3):
    print("TEXTPLOT version 0.1, Copyright (C) 2023 Tessa Vogt, Muenster, Germany")

    if len(sys.argv) != 5: # not enough input arguments
        errorinfo()
        print("Not enough input arguments:")
        print("Please use: ")
        return False
    
    # open Config File Definition
    try:
        with open(fileDef, "r") as fFileDef:
            with open(fileDef, "r") as fFileDef:
                for line in fFileDef:
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

    except IOError:
        errorinfo()
        print("Can't open basic definitions file '%s'" % fileDef)
        return False
    
    
    
    # ....

    return True

# ---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    try:    
        main(sys.argv)
        print("Execution completed successfully.")
    except:
        print("An error occurred during execution.")