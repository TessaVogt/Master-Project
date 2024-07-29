import pandas as pd

def get_teststring(testsample_number):
    # get the excel file path
    excel_file_path = 'static/Testsamples.xlsx'
    df = pd.read_excel(excel_file_path)
    # filter for the number in the first column
    ergebnis_df = df[df['Number'] == testsample_number]
    # extract the teststring from the second column of the result dataframe
    teststring = ergebnis_df['Teststring'].iloc[0]
    return teststring
