import pandas as pd

def get_teststring(testsample_number):
    # Lese die Excel-Datei ein
    excel_file_path = 'static/Testsamples.xlsx'
    df = pd.read_excel(excel_file_path)
    # Filtere den DataFrame nach der gesuchten Zahl in der ersten Spalte
    ergebnis_df = df[df['Number'] == testsample_number]
    # Erhalte den Teststring aus der zweiten Spalte des Ergebnis-DataFrames
    teststring = ergebnis_df['Teststring'].iloc[0]
    return teststring
