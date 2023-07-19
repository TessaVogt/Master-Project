import sys
import fntFileHandling as fnt
import letterHandling as ltr
import os


if __name__ == "__main__":
    # Example call for the letter 'B' (ASCII: 66)
    # font_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\GitHub\\Master-Project\\createFont\\test.fnt"
    # sFnt, sPnt = fnt.parse_font_file(font_path)
    # letter_coords = fnt.getLetterCoords('C', sFnt, sPnt)
    # image_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\FH_Dortmund\\Master-Studienarbeit\\BuchstabenInput\\B.png"
    # image_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\GitHub\\Master-Project\\handwirting\\picsLetter\\Buchstaben1\\letter_uc_C.png"

    
    # capital_letter = 1
    # coordinates = ltr.getHandwritingCoords(image_path, capital_letter)
    # coordsCode = ltr.getImpCoords(coordinates, letter_coords)
    # #print(coordsCode)
    # fnt.writeLetterCoords(coordsCode)
    font_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\GitHub\\Master-Project\\createFont\\test.fnt"
    sFnt, sPnt = fnt.parse_font_file(font_path)
    folder_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\GitHub\\Master-Project\\handwirting\\picsLetter\\"
    folder_name = "Buchstaben1"
    file_info_list = fnt.extract_file_info(folder_path, folder_name)

    # Iteration over the list and output of the information
    for file_info in file_info_list:
        file = file_info["file"]
        letter = file_info["letter"]
        category = file_info["category"]
        capital_letter = file_info["capital_letter"]
        
        print("File:", file)
        print("Letter:", chr(letter), " ASCII:", letter)
        print("Category:", category)
        print("Capital letter?", capital_letter)

        if letter != 8364:
            letter_coords = fnt.getLetterCoords(letter, sFnt, sPnt)
            image_path = folder_path + folder_name + "\\" + file
            coordinates = ltr.getHandwritingCoords(image_path, capital_letter)
            coordsCode = ltr.getImpCoords(coordinates, letter_coords)
            #print(coordsCode)
            added = fnt.writeLetterCoords(coordsCode, folder_name)
            if added is True:
                print("Added successfully to Fontfile\n")
            