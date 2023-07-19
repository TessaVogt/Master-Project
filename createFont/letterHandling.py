from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import math



def getHandwritingCoords(image_path, capital_letter):
    # Open the image
    image = Image.open(image_path)
    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Extract the color channels (Red, Green, Blue, Alpha)
    red_channel = image_array[:, :, 0]
    green_channel = image_array[:, :, 1]
    blue_channel = image_array[:, :, 2]
    alpha_channel = image_array[:, :, 3]

    # Create a binary image by selecting only the black pixels
    binary_image = (red_channel == 0) & (green_channel == 0) & (blue_channel == 0) & (alpha_channel != 0)
    # Flip the image vertically
    flipped_image = np.flipud(binary_image)

    # Extract the x and y coordinates of the letter
    coords = np.argwhere(flipped_image)
    x_coords = coords[:, 1]
    y_coords = coords[:, 0]

    # Apply found coordinate points to my coordinate system of y(-20,60) and x(0,60).
    min_x = float('inf')
    min_y = float('inf')
    max_y = 0

    # Find the rightmost point and the bottom point
    for coord in coords:
        y, x = coord
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y

    # Move and mirror the coordinate points accordingly
    adjusted_coordinates = []
    for coord in coords:
        y, x = coord
        adjusted_x = 5 + (x - min_x)
        adjusted_y = (y - min_y)
        adjusted_coordinates.append((adjusted_x, adjusted_y))

    # enlarge the letter points if necessary
    for coord in adjusted_coordinates:
        x, y = coord
        if y > max_y:
            max_y = y

    if capital_letter == 1:
        max = 58
    else:
        max = 38
    zoom = max / max_y
    zoom = round(zoom, 1)

    adjusted_coordinates_new = []
    for coord in adjusted_coordinates:
        x, y = coord
        adjusted_x = x * zoom
        adjusted_y = y * zoom
        adjusted_coordinates_new.append((round(adjusted_x, 2), round(adjusted_y, 2)))

    return adjusted_coordinates_new




def getImpCoords(handwritingCoords, fontCode):
    
    fontCoords = []
    for coordinate in fontCode:
        if coordinate[0] == 'P' or coordinate[0] == 'L':
            x = coordinate[1]
            y = coordinate[2]
            coords = (x,y)
            fontCoords.append(coords)
    
    impCoords = []
    for perfect_coord in fontCoords:
        closest_coord = None
        min_distance = float('inf')
        
        for coord in handwritingCoords:
            distance = math.sqrt((perfect_coord[0] - coord[0])**2 + (perfect_coord[1] - coord[1])**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_coord = coord
        
        impCoords.append(closest_coord)
    impCoordsCode = [tuple(fontCode[0])] + [(item[0], coord[0], coord[1]) for item, coord in zip(fontCode[1:], impCoords)]
    return impCoordsCode

"""
# for testing
if __name__ == "__main__":
    image_path = "C:\\Users\\tvogt\\OneDrive\\Dokumente\\FH_Dortmund\\Master-Studienarbeit\\BuchstabenInput\\B.png"
    capital_letter = 1
    coordinates = getHandwritingCoords(image_path, capital_letter)
    B = [['C', 66, 50], ['P', 7, 52], ['L', 7, 0], ['P', 7, 52], ['L', 30, 52], ['L', 37, 50], ['L', 40, 47], ['L', 42, 42], ['L', 42, 37], ['L', 40, 32], ['L', 37, 30], ['L', 30, 27], ['P', 7, 27], ['L', 30, 27], ['L', 37, 25], ['L', 40, 22], ['L', 42, 17], ['L', 42, 10], ['L', 40, 5], ['L', 37, 2], ['L', 30, 0], ['L', 7, 0]]
    coordsCode = getImpCoords(coordinates, B)
    print(coordsCode)
    """