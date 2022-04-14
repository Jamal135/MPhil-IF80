# Creation Date: 06/03/2022

# Note row values refer to row number in CSV, not in Dataframe.

import pandas
import ast

pandas.options.mode.chained_assignment = None  # default='warn'


def build_dataframe(input_name: str):
    ''' Returns: Built dataframe structure. '''
    return pandas.read_csv(f"verification/{input_name}", usecols=[
        'name', 'industry', 'region', 'size', 'founded',
        'linkedin_url', 'indeed_url', 'indeed_reviews',
        'seek_url', 'seek_reviews', 'total_reviews',
        'correct', 'scores', 'valid_urls'])


def show_data(row: list):
    scores = ast.literal_eval(row["scores"])
    ''' Displays collected row data for verifying. '''
    print(f'Organisation: {row["name"]}\n\
        LinkedIn: https://www.{row["linkedin_url"]}\n\
        Indeed: {row["indeed_url"]} Scores: {scores[0]}\n\
        Seek: {row["seek_url"]} Scores: {scores[1]}')


def user_input(row, index: int):
    ''' Returns valid user command line argument. '''
    show_data(row)
    valid_values = ("0", "1")
    response = ("Incorrect", "Correct")
    websites = ["Indeed", "Seek"]
    responses = []
    for link in range(len(websites)):
        while True:
            correct = input(f"Is {websites[link]} correct: ")
            if correct not in valid_values:
                print(f'Input {correct} is not in {valid_values}')
                continue
            else:
                print(
                    f'Row {index + 2}, {websites[link]} marked: {response[int(correct)]}')
                break
        responses.append(correct)
    print('')
    return responses


def fix_current(dataframe, responses: str, index: int):
    ''' Returns: Dataframe with current value fixed. '''
    data = tuple(["Correct" if x == "1" else "Incorrect" for x in responses])
    dataframe['correct'][index] = str(data)
    return dataframe


def verify_data(input_name: str, start: int = None):
    ''' Returns: Modified CSV with corrected data. '''
    print("Input 0: incorrect, 1: correct\n")
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    dataframe = build_dataframe(input_name)
    if start < 2:
        raise ValueError("Start argument must be two or larger. ")
    try:
        for index, row in dataframe.iterrows():
            while True:
                if index == start - 2:
                    print(f"Row {index + 2} specified start\n")
                elif row['correct'] != "Unknown":
                    print(f"Row {index + 2} already checked\n")
                    break
                responses = user_input(row, index)
                dataframe = fix_current(dataframe, responses, index)
                break
    except KeyboardInterrupt:
        print(f'\nStopping at row {index + 2}')
    dataframe.to_csv(f"verification/{input_name}", index=False)


verify_data("AUS_501+_Checked", start=2)
