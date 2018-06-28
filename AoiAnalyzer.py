from os.path import join

import _pickle as pickle

from config import PATH_DATA_PREPROCESSED, PATH_DATA_OUTPUT, PARTICIPANTS

# TODO remove required response log file
# TODO remove required physio log file
# TODO generalize code better (e.g., conditions)
# TODO clean up code
# TODO comment/document functions

# config
snippet_aoi_border_top = 42
snippet_aoi_border_center = 50
snippet_aoi_border_bottom = 92
snippet_aoi_border_vertical_offset_sm = 25
snippet_aoi_border_vertical_offset_lg = 50

snippet_AOI = [
    {
        'snippet_name': 'arrayAverageTD_B.png',
        'algo_name': 'arrayAverage (B)',
        'border_left': 645,
        'border_right': 1018
    },
    {
        'snippet_name': 'grey.png',
        'algo_name': 'BinaryToDecimal',
        'border_left': 737,
        'border_right': 923
    },
    {
        'snippet_name': 'ecnzaqnkKopkzvqnmTD_N.png',
        'algo_name': 'containsSubstring (NB)',
        'border_left': 540,
        'border_right': 1124
    },
    {
        'snippet_name': 'reverseWordTD_U.png',
        'algo_name': 'reverseWord',
        'border_left': 653,
        'border_right': 1012
    },
    {
        'snippet_name': 'powerTD_B.png',
        'algo_name': 'power (B)',
        'border_left': 740,
        'border_right': 922
    },
    {
        'snippet_name': 'pink.png',
        'algo_name': 'Factorial',
        'border_left': 770,
        'border_right': 890
    },
    {
        'snippet_name': 'ecoamKayiEoaikAmKayiEckqmqcaTD_N.png',
        'algo_name': 'countSameChars (NB)',
        'border_left': 385,
        'border_right': 1277
    },
    {
        'snippet_name': 'crossSumTD_U.png',
        'algo_name': 'crossSum',
        'border_left': 724,
        'border_right': 937
    },
    {
        'snippet_name': 'firstAboveTresholdTD_B.png',
        'algo_name': 'firstAboveTreshold (B)',
        'border_left': 575,
        'border_right': 1091
    },
    {
        'snippet_name': 'red.png',
        'algo_name': 'CountVowels',
        'border_left': 685,
        'border_right': 981
    },
    {
        'snippet_name': 'beebtBurebzrTD_N.png',
        'algo_name': 'arrayAverage (NB)',
        'border_left': 641,
        'border_right': 1019
    },
    {
        'snippet_name': 'sumUpTD_U.png',
        'algo_name': 'sumUp',
        'border_left': 762,
        'border_right': 900
    },
    {
        'snippet_name': 'containsSubstringTD_B.png',
        'algo_name': 'containsSubstring (B)',
        'border_left': 523,
        'border_right': 1138
    },
    {
        'snippet_name': 'lightgreen.png',
        'algo_name': 'Maximum',
        'border_left': 627,
        'border_right': 1032
    },
    {
        'snippet_name': 'buycpTD_N.png',
        'algo_name': 'power',
        'border_left': 737,
        'border_right': 924
    },
    {
        'snippet_name': 'isPalindromeTD_U.png',
        'algo_name': 'isPalindrome',
        'border_left': 640,
        'border_right': 1021
    },
    {
        'snippet_name': 'countSameCharsAtSamePositionTD_B.png',
        'algo_name': 'countSameChars (B)',
        'border_left': 412,
        'border_right': 1250
    },
    {
        'snippet_name': 'gold.png',
        'algo_name': 'IntertwineTwoWords',
        'border_left': 650,
        'border_right': 1009
    },
    {
        'snippet_name': 'vsjihAzmfwHjwitmpxTD_N.png',
        'algo_name': 'firstAboveTreshold (NB)',
        'border_left': 569,
        'border_right': 1091
    },
    {
        'snippet_name': 'squareRootsTD_U.png',
        'algo_name': 'squareRoots',
        'border_left': 620,
        'border_right': 1040
    }
]


def run_aoi_analysis(participants):
    analyze_fixations_for_all_participants(participants, False)
    analyze_fixations_for_all_participants(participants, True)

    print_all_fixations(participants, False)
    print_all_fixations(participants, True)


def analyze_fixations_for_all_participants(participants, use_fixation_length=False):
    aoi_fixations_overall = [0, 0, 0]
    aoi_fixations_per_comprehension = [[0, 0, 0] for i in range(20)]
    aoi_fixations_per_participant = [[0, 0, 0] for i in range(len(participants))]

    for participant in participants:
        [aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant] = analyze_fixations(participants, participant, aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, use_fixation_length)

    print("\n#### ANALYSIS")
    print("found in inner AOI: ", aoi_fixations_per_comprehension[0])
    print("found in sm outer AOI: ", aoi_fixations_per_comprehension[1])
    print("found in lg outer AOI: ", aoi_fixations_per_comprehension[2])

    write_comprehension_to_csv_file(aoi_fixations_per_comprehension, use_fixation_length)
    write_comprehension_to_csv_file_bar(participants, aoi_fixations_per_comprehension, use_fixation_length)
    write_participants_to_csv_file(participants, aoi_fixations_per_participant, use_fixation_length)


def print_all_fixations(participants, use_fixation_length=False):
    all_fixations = []

    for participant_id in participants:
        with open(join(PATH_DATA_PREPROCESSED, "fixations", participant_id + ".pkl"), 'rb') as input:
            fixations = pickle.load(input)

            print("\n## " + participant_id)
            participant_pos = participants.index(participant_id)

            for fixation in fixations:
                try:
                    [matching_snippet_aoi_index, matching_snippet_aoi] = next(([index, item] for (index, item) in enumerate(snippet_AOI) if item["snippet_name"] == fixation['snippet']), None)
                except:
                    pass

                if matching_snippet_aoi is not None and fixation['trial_category'] != "D2" and fixation['trial_category'] != "Rest" and fixation['trial_category'] != "DecTime":
                    if "D2_" in str(fixation["snippet"]) or "Rest" in str(fixation["snippet"]) or "DecTime" in str(fixation["snippet"]):
                        print("something is wrong!")
                        continue

                    print("-> found fixation for " + str(fixation["snippet"]) + " after " + str(fixation["frames"]) + " frames, for " + fixation["data"][2] + " msec, at position x=" + fixation["data"][3] + ", y=" + fixation["data"][4])

                    fixation_x = float(fixation["data"][3])
                    fixation_y = float(fixation["data"][4])

                    if matching_snippet_aoi["border_left"] < fixation_x < matching_snippet_aoi["border_right"]:
                        maximum_distance_below = 60
                        maximum_distance_top = 120

                        if snippet_aoi_border_top - maximum_distance_top < fixation_y < snippet_aoi_border_bottom + maximum_distance_below:
                            print("--> found fixation on larger outer AOI of  task function!")
                            import math
                            all_fixations.append({
                                "participant_id": participant_id,
                                "snippet": str(fixation["snippet"]),
                                "frames": str(fixation["frames"]),
                                "fixation_time": math.floor(float(fixation["data"][2])/10),
                                "distance_y": str(math.floor(fixation_y - snippet_aoi_border_center))
                            })

    # print all fixations to CSV file
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if use_fixation_length:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_histogram_time.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_histogram_count.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("participant_id;snippet;frames;distance_y\n")

        for fixation in all_fixations:
            if use_fixation_length:
                for x in range(0, fixation["fixation_time"]):
                    file_write(fixation["participant_id"] + ";" + fixation["snippet"] + ";" + fixation["frames"] + ";" + str(fixation["distance_y"]) + "\n")
            else:
                file_write(fixation["participant_id"] + ";" + fixation["snippet"] + ";" + fixation["frames"] + ";" + str(fixation["distance_y"]) + "\n")

    print("-> saving file: done!")


def analyze_fixations(participants, participant_id, aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, use_fixation_length):
    with open(join(PATH_DATA_PREPROCESSED, "fixations", participant_id + ".pkl"), 'rb') as input:
        fixations = pickle.load(input)

        print("\n## " + participant_id)
        participant_pos = participants.index(participant_id)

        for fixation in fixations:
            try:
                [matching_snippet_aoi_index, matching_snippet_aoi] = next(([index, item] for (index, item) in enumerate(snippet_AOI) if item["snippet_name"] == fixation['snippet']), None)
            except:
                pass

            if matching_snippet_aoi is not None and fixation['trial_category'] != "D2" and fixation['trial_category'] != "Rest" and fixation['trial_category'] != "DecTime":
                if "D2_" in str(fixation["snippet"]) or "Rest" in str(fixation["snippet"]) or "DecTime" in str(fixation["snippet"]):
                    print("something is wrong!")
                    continue

                print("-> found fixation for " + str(fixation["snippet"]) + " after " + str(fixation["frames"]) + " frames, for " + fixation["data"][2] + " msec, at position x=" + fixation["data"][3] + ", y=" + fixation["data"][4])

                fixation_x = float(fixation["data"][3])
                fixation_y = float(fixation["data"][4])

                if matching_snippet_aoi["border_left"] < fixation_x < matching_snippet_aoi["border_right"]:
                    if snippet_aoi_border_top < fixation_y < snippet_aoi_border_bottom:
                        print("--> found fixation on inner AOI of task function!")
                        if use_fixation_length:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 0, float(fixation["data"][2]))
                        else:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 0, 1)

                    if snippet_aoi_border_top - snippet_aoi_border_vertical_offset_sm < fixation_y < snippet_aoi_border_bottom + snippet_aoi_border_vertical_offset_sm:
                        print("--> found fixation on smaller outer AOI of  task function!")
                        if use_fixation_length:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 1, float(fixation["data"][2]))
                        else:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 1, 1)

                    if snippet_aoi_border_top - snippet_aoi_border_vertical_offset_lg < fixation_y < snippet_aoi_border_bottom + snippet_aoi_border_vertical_offset_lg:
                        print("--> found fixation on larger outer AOI of  task function!")
                        if use_fixation_length:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 2, float(fixation["data"][2]))
                        else:
                            set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, 2, 1)

            else:
                pass

    return [aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant]


def set_variables(aoi_fixations_overall, aoi_fixations_per_comprehension, aoi_fixations_per_participant, matching_snippet_aoi_index, participant_pos, array_pos, value=1):
    aoi_fixations_overall[array_pos] += value
    aoi_fixations_per_participant[participant_pos][array_pos] += value
    aoi_fixations_per_comprehension[matching_snippet_aoi_index][array_pos] += value


def write_participants_to_csv_file(participants, aoi_fixations_per_comprehension, use_fixation_length):
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if use_fixation_length:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_participant_time.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_participant_count.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("nr;aoi_inner;aoi_25px;aoi_50px;subject\n")

        for participant_pos, line in enumerate(aoi_fixations_per_comprehension):
                file_write(str(participant_pos+1) + ";" + str(line[0]) + ";" + str(line[1]) + ";" + str(line[2]) + ";P0" + str(participant_pos) + "\n")

    print("-> saving file: done!")


def write_comprehension_to_csv_file_bar(participants, aoi_fixations_per_comprehension, use_fixation_length):
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if use_fixation_length:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_comprehension_time_bar.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_comprehension_count_bar.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("snippet;aoi_inner;aoi_25px;aoi_50px;subject\n")

        for i, line in enumerate(aoi_fixations_per_comprehension):
            file_write(snippet_AOI[i]["algo_name"] + ";" + str(line[0]) + ";" + str(line[1]) + ";" + str(line[2]) + ";average\n")

    print("-> saving file: done!")


def write_comprehension_to_csv_file(aoi_fixations_per_comprehension, use_fixation_length):
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if use_fixation_length:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_comprehension_time.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "aoi_task_comprehension_count.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("time;aoi;value;subject\n")

        for i, line in enumerate(aoi_fixations_per_comprehension):
            file_write(str(i+1) + ";inner;" + str(line[0]) + ";average\n")

        for i, line in enumerate(aoi_fixations_per_comprehension):
            file_write(str(i+1) + ";25px;" + str(line[1]) + ";average\n")

        for i, line in enumerate(aoi_fixations_per_comprehension):
            file_write(str(i+1) + ";50px;" + str(line[2]) + ";average\n")

    print("-> saving file: done!")


if __name__ == "__main__": run_aoi_analysis(PARTICIPANTS)
