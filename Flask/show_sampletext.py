import sqlite3
import matplotlib.pyplot as plt
import show_db
import numpy as np



def plot_sampletext(new_line_indices, data_last, font_name, text_sample, scale=1, save=False):
    if scale != 1:
        # Umwandlung in float und Skalierung
        data_last = np.array(data_last, dtype=float) * scale
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
    plt.title(f'font_name = {font_name}, text_sample = {text_sample}, scale = {scale}')
    plt.ylim(900*scale, -20)
    plt.xlim(0, 1200*scale)
    plt.show()

    if save is True:
        # Speichern des Plots
        plt.savefig(f'static/figures/plot_{font_name}_{text_sample}.png')
        plt.close()  # Schließe das Plot-Fenster nach dem Speichern





def show_sampletext(font_name, text_sample):
    data = show_db.get_sampletextdata_from_db(font_name, 'instance/coords.db')
    new_line_indices, data_last = show_db.get_data_for_textsample(data, text_sample)
    plot_sampletext(new_line_indices, data_last, font_name, text_sample, scale=2.26, save=False)
    

if __name__ == "__main__":
    font_name = 'Laptop'
    text_sample = 1
    show_sampletext(font_name, text_sample)
