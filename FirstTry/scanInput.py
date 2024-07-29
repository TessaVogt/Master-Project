import os
import sys
import cv2
from PIL import Image
from pdf2image import convert_from_path


def convert_pdf_to_jpg(pdf_path):
    poppler = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\FH_Dortmund\\Master-Studienarbeit\\poppler-0.68.0\\bin"
    # page = convert_from_path(image_name + ".pdf", poppler_path=poppler)
    page = convert_from_path(pdf_path, poppler_path=poppler)
    image_name = os.path.splitext(os.path.basename(pdf_path))[0]
    jpg_path = image_name + '.jpg'
    page[0].save(jpg_path, 'JPEG')
    return jpg_path

def detect_rectangles(image_path, min_width=80, min_height=100):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rectangles = []
    variance = 10  # Variationswert von ±10

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w >= min_width and h >= min_height:
            # Überprüfung auf bereits vorhandene Rectangles mit ähnlichen x- und y-Werten
            is_duplicate = False
            for rect in rectangles:
                if abs(rect[0] - x) <= variance and abs(rect[1] - y) <= variance:
                    is_duplicate = True
                    break

            # Füge das Rectangle nur hinzu, wenn kein ähnliches Rectangle gefunden wurde
            if not is_duplicate:
                rectangles.append((x, y, w, h))

    return rectangles

def display_valid_rectangles(image_path, rectangles):
    image = cv2.imread(image_path)
    
    for (x, y, w, h) in rectangles:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return image


def extract_rectangle_images(image_path, rectangles, output_dir, padding=5):
    order = [char for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜabcdefghijklmnopqrstuvwxyzäöü"] + ["eszett"] + [char for char in "1234567890"]
    order = order + ["period", "comma", "simicolon", "colon", "question_mark", "exclamation_mark", "and", "percent", "euro", "at_sign", "quotation_marks_above", "close_parenthesis", "open_parenthesis", "hashtag", "hyphen", "plus"] # .,;?!@&%€\'\"()#-
    print(order)

    image = Image.open(image_path)
    image_name = os.path.splitext(os.path.basename(image_path))[0]

    if not os.path.exists(output_dir + "\\" + image_name):
        os.makedirs(output_dir + "\\" + image_name)

    # Sortiere Rechtecke nach y-Wert in aufsteigender Reihenfolge
    sorted_rectangles = sorted(rectangles, key=lambda r: r[1])
    k = 0
    while sorted_rectangles:
        # Finde Rechteck mit kleinstem y-Wert
        min_y_rect = min(sorted_rectangles, key=lambda r: r[1])
        min_y = min_y_rect[1]

        # Filtere Rechtecke mit ähnlichem y-Wert (+-10 Abstand)
        similar_rectangles = [r for r in sorted_rectangles if abs(r[1] - min_y) <= 20]

        # Sortiere ähnliche Rechtecke nach y-Wert in aufsteigender Reihenfolge
        sorted_similar_rectangles = sorted(similar_rectangles, key=lambda r: r[0])

        for i, (x, y, w, h) in enumerate(sorted_similar_rectangles):
            x += padding
            y += padding
            w -= 2 * padding
            h -= 2 * padding

            cropped_image = image.crop((x, y, x+w, y+h))
            if len(sorted_similar_rectangles) != len(sorted_rectangles):
                line_length = len(sorted_similar_rectangles)
            letter = order[(k*line_length) + i]
            if letter.isalpha():
                if len(letter)==1:
                    if letter.isupper():
                        letter_addition = "_uc_"    # uppercase letter
                    else:
                        letter_addition = "_lc_"    # lowercase letter
                else:
                    letter_addition = "_pm_"        # punctuation mark
            elif letter.isdigit():
                letter_addition = "_digit_"           # digits
            else:
                letter_addition = "_pm_"        # punctuation mark
            letter_name = "letter" + letter_addition + letter + ".png"
            cropped_image.save(os.path.join(output_dir, image_name, letter_name))

        # Entferne die verarbeiteten Rechtecke aus der Liste
        sorted_rectangles = [r for r in sorted_rectangles if r not in similar_rectangles]

        # Sortiere die verbleibenden Rechtecke nach x-Wert (für den nächsten Durchlauf)
        sorted_rectangles = sorted(sorted_rectangles, key=lambda r: r[0])
        k += 1


                           
def substractLettersFromScan(input_file, output_dir):
    # Überprüfen, ob die Datei bereits eine JPG-Datei ist
    if input_file.lower().endswith(".png"):
        image_path = input_file
    else:
        # Wenn nicht, PDF in JPG konvertieren
        image_path = convert_pdf_to_jpg(input_file)
    rectangles = detect_rectangles(image_path)
    image_with_rectangles = display_valid_rectangles(image_path, rectangles)
    picsLetter_path = output_dir + "\\" + os.path.splitext(os.path.basename(image_path))[0]
    cv2.imwrite(picsLetter_path + "Scan" + ".png", image_with_rectangles)
    extract_rectangle_images(image_path, rectangles, output_dir)

    return picsLetter_path


if __name__ == "__main__":
    # Eingabedatei
    current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    print("current path: ", current_path)
    input_file_name = 'Buchstaben2.pdf'
    input_file = current_path + "\\" + input_file_name
    # Überprüfen, ob die Datei existiert
    print("path to pdf file: ", input_file)
    if not os.path.exists(input_file):
        print("PDF-file was NOT found.")
    # Ausgabeverzeichnis für JPEG-Dateien
    output_dir = 'handwirting\\picsLetter'

    picsLetter_path = substractLettersFromScan(input_file, output_dir)
    print(picsLetter_path)