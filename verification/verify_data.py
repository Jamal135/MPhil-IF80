# Creation Date: 06/03/2022

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


def user_input(row, index: int, allow_n: bool = True):
    ''' Returns valid user command line argument. '''
    show_data(row)
    valid_values = ("0", "1", "n") if allow_n and index != 0 else ("0", "1")
    response = ("Incorrect", "Correct")
    while True:
        correct = input("Is data correct: ")
        if correct not in valid_values:
            print(f'Input {correct} is not in {valid_values}')
            continue
        else:
            if correct != "n":
                print(f'Row {index} marked: {response[int(correct)]}\n')
            break
    return correct


def fix_current(dataframe, correct: str, index: int):
    ''' Returns: Dataframe with current value fixed. '''
    text = "Correct" if bool(int(correct)) else "Incorrect"
    dataframe['correct'][index] = text
    return dataframe


def fix_previous(dataframe, previous: list):
    ''' Returns: Dataframe with previous value fixed. '''
    print(f"Previous marked wrong, revisiting row {previous[1]}")
    correct = user_input(previous[0], previous[1], False)
    text = "Correct" if bool(int(correct)) else "Incorrect"
    dataframe['correct'][previous[1]] = text
    print(f"Row {previous[1]} fixed")
    return dataframe


def verify_data(input_name: str):
    ''' Returns: Modified CSV with corrected data. '''
    print("Input 0: incorrect, 1: correct, n: fix previous\n")
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    dataframe = build_dataframe(input_name)
    previous = None
    try:
        for index, row in dataframe.iterrows():
            while True:
                if row['correct'] != "Unknown":
                    print(f"Row {index} already checked\n")
                    break
                correct = user_input(row, index)
                if correct != "n":
                    dataframe = fix_current(dataframe, correct, index)
                    previous = [row, index]
                    break
                dataframe = fix_previous(dataframe, previous)
    except KeyboardInterrupt:
        print(f'\nStopping at row {index}')
    dataframe.to_csv(f"verification/{input_name}", index=False)


verify_data("AUS_501+_Checked")
