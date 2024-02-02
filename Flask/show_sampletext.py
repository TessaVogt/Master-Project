import sqlite3
import matplotlib.pyplot as plt
import show_db



def plot_sampletext(new_line_indices, data_last, text_sample):
    x_values = [point[0] for point in data_last]
    y_values = [point[1] for point in data_last]
    num_lines = len(new_line_indices)
    if num_lines != 0:
        for i in range(num_lines):
            start = new_line_indices[i]
            if i == (num_lines - 1):
                end = len(x_values)
            else:
                end = new_line_indices[i+1] - 1
            plt.plot(x_values[start:end], y_values[start:end], label=text_sample)
    else:
        plt.plot(x_values, y_values, label=text_sample)

    plt.gca().invert_yaxis()  # Hier wird die Y-Achse invertiert
    plt.title(f'{text_sample}')
    plt.ylim(900, -20)
    plt.xlim(0, 1200)
    plt.show()



def show_sampletext(font_name, text_sample):
    data = show_db.get_sampletextdata_from_db(font_name, 'instance/coords.db')
    new_line_indices, data_last = show_db.get_data_for_textsample(data, text_sample)
    plot_sampletext(new_line_indices, data_last, text_sample)
    

if __name__ == "__main__":
    font_name = 'Laptop'
    text_sample = 1
    show_sampletext(font_name, text_sample)
