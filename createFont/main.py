import sys
import fntFileHandling as fnt
import letterHandling as ltr


if __name__ == "__main__":
    # Beispielaufruf für den Buchstaben 'B' (ASCII: 66)
    font_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\GitHub\\Master-Project\\createFont\\test.fnt"
    sFnt, sPnt = fnt.parse_font_file(font_path)
    letter_coords = fnt.getLetterCoords('B', sFnt, sPnt)
    image_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\FH_Dortmund\\Master-Studienarbeit\\BuchstabenInput\\B.png"
    capital_letter = 1
    coordinates = ltr.getHandwritingCoords(image_path, capital_letter)
    coordsCode = ltr.getImpCoords(coordinates, letter_coords)
    #print(coordsCode)
    fnt.writeLetterCoords(coordsCode)