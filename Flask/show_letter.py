import sqlite3
import matplotlib.pyplot as plt
import show_db



def plot_letter(new_line_indices, data_last_letter, letter):
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
            plt.plot(x_values[start:end], y_values[start:end], label=letter)
    else:
        plt.plot(x_values, y_values, label=letter)

    plt.gca().invert_yaxis()  # Hier wird die Y-Achse invertiert
    plt.title(f'{letter}')
    plt.ylim(300, -20)
    plt.xlim(0, 500)
    plt.show()



def show_letter(font_name, letter):
    data = show_db.get_letterdata_from_db(font_name, 'instance/coords.db')
    new_line_indices, data_last_letter = show_db.get_data_for_letter(data, letter)
    plot_letter(new_line_indices, data_last_letter, letter)
    

if __name__ == "__main__":
    font_name = 'Laptop'
    letter = "D"
    show_letter(font_name, letter)
