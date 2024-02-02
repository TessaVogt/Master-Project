import sqlite3
from datetime import datetime, timedelta

def get_data_from_db(font_name, db_path):
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Datenpunkte für den angegebenen Buchstaben abrufen
    cursor.execute(f"SELECT letter, created_at, new_line, x, y FROM creating_font WHERE font_name = '{font_name}'")
    data = cursor.fetchall()
    # Verbindung zur Datenbank schließen
    conn.close()
    return data


def get_data_for_letter(data, letter):
    data_letter = [point for point in data if point[0] == letter]
    # extrahiere letzte Eingabe
    created_at_dates = [point[1].split('.')[0] for point in data_letter]
    last_date = max(created_at_dates)
    
    # Filtere alle Punkte mit der gleichen created_at-Zeit (ohne Millisekunden)
    data_last_letter = [point for point in data_letter if point[1].split('.')[0] == last_date]
  
    # entferne die spalten mit letter und created_at
    data_last_letter = [point[2:] for point in data_last_letter]
    return data_last_letter


def remove_double_points(data):
    filtered_data = [data[0]]  # Keep the first point as it is
    for i in range(1, len(data)):
        if data[i] != filtered_data[-1]:
            filtered_data.append(data[i])
    return filtered_data


def scale_letter(data):
    # move to new zero point
    x_values = [point[1] for point in data]
    min_x = min(x_values)
    new_x_values = [point[1] - (min_x -5) for point in data]
    y_values = [point[2] for point in data]
    max_y = max(y_values)
    # invert y-axis
    inverted_y_values = [205 - y for y in y_values]
    # scale data
    # desired_max_y = 50
    # scaling_factor = desired_max_y / 205
    scaling_factor = 0.2439
    scaled_x_values = [round(x * scaling_factor) for x in new_x_values]
    scaled_y_values = [round(y * scaling_factor) for y in inverted_y_values]
    # Overwrite x_values and y_values with scaled values
    for i, point in enumerate(data):
        data[i] = (point[0], scaled_x_values[i], scaled_y_values[i])
    removed_data = remove_double_points(data)
    return removed_data


def create_font_input(data, letter):
    x_values = [point[1] for point in data]
    width = max(x_values) + 5
    first_entry = [("C", ord(letter), width)]
    # P or L depending on where to start new line
    font_input = first_entry + [(("L", "P")[point[0]], point[1], point[2]) for point in data]
    return font_input


def prepare_fontfile(font_name):
    with open("handwriting_" + font_name + ".fnt", "w") as f:
        # delete previous input in file and print space into font file
        f.write("! > <\nC 32 30\n")
    return True


def write_letter_to_file(coordsCode, font_name):
    with open("handwriting_" + font_name + ".fnt", "a+") as f:
        first_entry = coordsCode[0]
        ascii_char = first_entry[1]
        f.write("! >{}<\n".format(chr(ascii_char)))

        for entry in coordsCode:
            command, x, y = entry
            f.write("{} {} {}\n".format(command, x, y))
    return True





if __name__ == "__main__":
    db_path = 'instance/coords.db'
    font_name = "Ipad"
    data = get_data_from_db(font_name, db_path)
    prepare_fontfile(font_name)
    # asciiList = ["a"]
    asciiList = [chr(i) for i in range(33, 36)] + [chr(37), chr(38)] + [chr(i) for i in range(40, 42)] + [chr(i) for i in range(43, 60)] + [chr(i) for i in range(63, 91)] + [chr(95)] + [chr(i) for i in range(97, 123)] + [chr(196), chr(214), chr(220), chr(223), chr(228), chr(246), chr(252)]
    for char in asciiList:
        data_last_letter = get_data_for_letter(data, char)
        scaled_letter = scale_letter(data_last_letter)
        font_input = create_font_input(scaled_letter, char)
        write_letter_to_file(font_input, font_name)
