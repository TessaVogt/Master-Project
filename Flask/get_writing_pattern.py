import show_db
import get_teststring
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances
from scipy.cluster.hierarchy import linkage, fcluster



def get_writing_pattern(font_name, text_sample):
    teststring = get_teststring.get_teststring(text_sample)
    char_list = []
    for char in teststring:
        char_list.append(char)
    letter = char_list[1]
    data_letters = show_db.get_letterdata_from_db(font_name, 'instance/coords.db')
    new_line_indices_letter, datapoints_letter = show_db.get_data_for_letter(data_letters, letter)
    data_text = show_db.get_sampletextdata_from_db(font_name, 'instance/coords.db')
    new_line_indices_text, datapoints_text = show_db.get_data_for_textsample(data_text, text_sample)
    # change to float and multiply with 2.26 to get the correct scaling
    datapoints_text = (np.round(np.array(datapoints_text, dtype=float) * 2.26)).astype(int)
    words, new_line_indices_words = get_words_from_rows(datapoints_text, new_line_indices_text,threshold=85)
    print(len(new_line_indices_words), len(words))
    # for idx, word in enumerate(words):
    #     plot(new_line_indices_words[idx], word, font_name, text_sample)
    get_letters(words, font_name, text_sample)

def plot(new_line_indices, data_row, font_name, text_sample):
    x_values = [point[0] for point in data_row]
    y_values = [point[1] for point in data_row]

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

    plt.gca().invert_yaxis()  # invert the y-axis
    plt.title(f'font_name = {font_name}, text_sample = {text_sample}')
    plt.ylim(300, -20)
    plt.xlim(0, 2500)
    plt.show()


def get_words_from_rows(datapoints, new_line_indices, threshold=5):
    rows, new_line_indices_rows = get_rows_from_datapoints(datapoints, new_line_indices, row_height=340)
    words = []
    current_word = []
    space_length = []

    for row in rows:
        for point in row:
            if current_word == []:
                current_word.append(point)
            else:
                differences = np.linalg.norm(current_word - np.array(point), axis=1)
                closest_index = np.argmin(differences)
                closest_distance = differences[closest_index]
                if closest_distance < threshold:
                    current_word.append(point)
                else:
                    space_length.append(closest_distance)
                    words.append(np.array(current_word))
                    current_word = []
                    current_word.append(point)
    if current_word:
        words.append(np.array(current_word))
    print(space_length)

    new_line_indices_words = get_indices(words, new_line_indices)     
    return words, new_line_indices_words




def get_rows_from_datapoints(datapoints, new_line_indices, row_height=340):
    new_line_indices_rows = []
    rows = []
    current_row = []
    current_row_index = 1

    for point in datapoints:

        if point[1] >= current_row_index * row_height:
            # get the smallest y value in the current row
            min_y_value = np.min(np.array(current_row)[:, 1])
            # Substarct the smallest y value from all y values in the current row
            current_row = np.array(current_row) - [0, min_y_value]
            rows.append(np.array(current_row))
            current_row = []
            current_row_index += 1
        current_row.append(point)

    # Füge die letzte Zeile zum Array hinzu
    if current_row:
        # get the smallest y value in the current row
        min_y_value = np.min(np.array(current_row)[:, 1])
        # Substract the smallest y value from all y values in the current row
        current_row = np.array(current_row) - [0, min_y_value]
        rows.append(np.array(current_row))

    new_line_indices_rows = get_indices(rows, new_line_indices)
    # for idx, row in enumerate(rows):
    #     plot(new_line_indices_rows[idx], row, font_name, text_sample)
        

    return rows, new_line_indices_rows


def get_indices(array, new_line_indices):
    new_line_indices_array = []
    new_line_current_array = []
    len_all_previous_array = 0

    for point in array:
        len_current_array = len(point)
        len_all_until_this_array = len_current_array + len_all_previous_array
        for indices in new_line_indices:
            # add the found indices to new_line_indices_rows
            if indices < len_all_previous_array:
                continue
            elif indices >= (len_all_until_this_array):
                new_line_indices_array.append(np.array(new_line_current_array))
                new_line_current_array = []
                len_all_previous_array = len_all_until_this_array
                break
        
            else:
                new_line_current_array.append(indices-len_all_previous_array)
            
    # add for last row
    new_line_indices_array.append(np.array(new_line_current_array))
    return new_line_indices_array

def get_letters(words, font_name, text_sample):
    text_sample_snipped = ["D","i","e"]
    word_points = words[0]
    letter = text_sample_snipped[0]
    data = show_db.get_letterdata_from_db(font_name, 'instance/coords.db')
    new_line_indices_letter, letter_points = show_db.get_data_for_letter(data, letter)
    cluster_letters = identify_letters_in_word(word_points, np.array(letter_points))
    return False


def identify_letters_in_word(word_points, letter_points, similarity_threshold=0.8, distance_threshold=50):
    # calculate the distances between letter points
    distances = euclidean_distances(letter_points, letter_points)

    # use hierarchical clustering to group letter points
    Z = linkage(distances, method='average', metric='euclidean')

    # use fcluster to group letter points into clusters
    clusters = fcluster(Z, t=distance_threshold, criterion='distance')

    # iterate over clusters and identify letters
    for cluster_id in np.unique(clusters):
        cluster_indices = np.where(clusters == cluster_id)[0]
        cluster_letters = letter_points[cluster_indices]

        # calculate the average similarity between the word and the cluster
        avg_similarity = calculate_average_similarity(word_points, cluster_letters)

        # identify the letter if the similarity is above the threshold
        if avg_similarity > similarity_threshold:
            # get the letter with the highest similarity
            best_match_index = np.argmax(euclidean_distances(word_points, cluster_letters))
            best_match = cluster_letters[best_match_index]
            print(f"Buchstabe identifiziert: {best_match}")
    return best_match

def calculate_average_similarity(word_points, cluster_letters):
    # get the euclidean distances between all word points and all cluster letters
    return np.mean(euclidean_distances(word_points, cluster_letters))







if __name__ == "__main__":
    font_name = 'Laptop'
    text_sample = 1
    get_writing_pattern(font_name, text_sample)