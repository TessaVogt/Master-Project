import sqlite3
import matplotlib.pyplot as plt



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
    created_at_dates = [point[1] for point in data_letter]
    last_date = max(created_at_dates)
    data_last_letter = [point for point in data_letter if point[1] == last_date]
    # new_line-Werte ausgeben 
    new_line_indices = [i for i, point in enumerate(data_last_letter) if point[2] == True]
    # entferne die spalten mit letter und created_at und new_line
    data_last_letter = [point[3:] for point in data_last_letter]
    return new_line_indices, data_last_letter


def plot_subplot(ax, new_line_indices, data_last_letter, letter):
    x_values = [point[0] for point in data_last_letter]
    y_values = [point[1] for point in data_last_letter]
    num_lines = len(new_line_indices)
    if num_lines != 0:
        for i in range(num_lines):
            start = new_line_indices[i]
            if i == (num_lines - 1):
                end = len(x_values)
            else:
                end = new_line_indices[i+1] - 1
            ax.plot(x_values[start:end], y_values[start:end], label=letter)
    else:
        ax.plot(x_values, y_values, label=letter)

    ax.invert_yaxis()  # Hier wird die Y-Achse invertiert
    # ax.set_xlabel('X-Koordinate')
    # ax.set_ylabel('Y-Koordinate')
    # ax.set_title(f'Koordinatenpunkte für Buchstabe {letter}')
    ax.set_title(f'{letter}')
    ax.set_ylim(300, -20)
    ax.set_xlim(0, 500)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)



def show_db(font_name):
    data = get_data_from_db(font_name, 'instance/coords.db')
    asciiList = [chr(i) for i in range(33, 36)] + [chr(37), chr(38)] + [chr(i) for i in range(40, 42)] + [chr(i) for i in range(43, 60)] + [chr(i) for i in range(63, 91)] + [chr(95)] + [chr(i) for i in range(97, 123)] + [chr(196), chr(214), chr(220), chr(223), chr(228), chr(246), chr(252)]
    fig, axs = plt.subplots(10, 9, figsize=(10, 10))
    for i, char in enumerate(asciiList):
        new_line_indices, data_last_letter = get_data_for_letter(data, char)
        plot_subplot(axs[i//9, i%9], new_line_indices, data_last_letter, char)

    # Platz zwischen den Plots hinzufügen, falls gewünscht
    plt.tight_layout()

    # save Plot
    plt.savefig(f'static\images\{font_name}_plot.png')

    # Zeige den Subplot
    plt.show()

if __name__ == "__main__":
    font_name = 'Test'
    show_db(font_name)
