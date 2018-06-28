from os.path import join

import _pickle as pickle

from config import PATH_DATA_PREPROCESSED, PATH_DATA_OUTPUT, PARTICIPANTS

# TODO remove required response log file
# TODO remove required physio log file
# TODO generalize code better (e.g., conditions)
# TODO clean up code
# TODO comment/document functions

fixation_cross_x = 640
fixation_cross_y = 514


def analyze_rest_condition_offset(participants):
    # TODO this is hardcoded to the amount of participants --> make it dynamic
    all_fixations_x_per_rest_condition = [[[],[],[],[],[],[],[],[],[]] for i in range(26)]
    all_fixations_y_per_rest_condition = [[[],[],[],[],[],[],[],[],[]] for i in range(26)]

    for participant in participants:
        [all_fixations_x_per_rest_condition, all_fixations_y_per_rest_condition] = analyze_fixations(participants, participant, all_fixations_x_per_rest_condition, all_fixations_y_per_rest_condition)

    print("\n#### ANAlYSIS")

    all_fixations_x_per_rest_condition.pop(0)
    all_fixations_y_per_rest_condition.pop(0)

    [condition_results_x, participant_results_x] = summarize_fixations_per_participant_and_rest(participants, all_fixations_x_per_rest_condition, "x", False)
    [condition_results_y, participant_results_y] = summarize_fixations_per_participant_and_rest(participants, all_fixations_y_per_rest_condition, "y", False)

    [condition_results_x_wt, participant_results_x_wt] = summarize_fixations_per_participant_and_rest(participants, all_fixations_x_per_rest_condition, "x", True)
    [condition_results_y_wt, participant_results_y_wt] = summarize_fixations_per_participant_and_rest(participants, all_fixations_y_per_rest_condition, "y", True)

    write_averages_to_csv_file(condition_results_x, condition_results_y, False)
    write_averages_to_csv_file(condition_results_x_wt, condition_results_y_wt, True)

    write_participants_to_csv_file(participants, participant_results_x, participant_results_y, False)
    write_participants_to_csv_file(participants, participant_results_x_wt, participant_results_y_wt, True)


def summarize_fixations_per_participant_and_rest(participants, all_fixations_x_per_rest_condition, axis, weighted):
    summarized_conditions_results = []
    # TODO this is hardcoded to the amount of participants -> make dynamic
    summarized_participants_results = [[None, None, None, None, None, None, None, None, None] for i in range(26)]

    for i, rest_condition in enumerate(all_fixations_x_per_rest_condition):
        print("\n##### Rest Condition: ", i + 1)

        distance_axis_amount = 0
        distance_axis_amount_wt = 0

        for participant in rest_condition:
            if len(participant) > 0:
                print("\nParticipant: ", participant[0]["participant"])

                part_distance_axis_amount = 0
                part_distance_axis_count = 0

                part_distance_axis_amount_wt = 0
                part_distance_axis_count_wt = 0

                for fixation in participant:
                    part_distance_axis_amount += fixation["fixation_distance"]
                    part_distance_axis_count += 1

                    part_distance_axis_amount_wt += fixation["fixation_length"] * fixation["fixation_distance"]
                    part_distance_axis_count_wt += fixation["fixation_length"]

                part_average_offset_axis = part_distance_axis_amount / part_distance_axis_count
                part_average_offset_axis_wt = part_distance_axis_amount_wt / part_distance_axis_count_wt
                distance_axis_amount += part_average_offset_axis
                distance_axis_amount_wt += part_average_offset_axis_wt
                print("part average offset " + axis + ": ", part_average_offset_axis)
                print("part average offset " + axis + " wt: ", part_average_offset_axis_wt)

                if weighted:
                    summarized_participants_results[i][participants.index(participant[0]["participant"])] = part_average_offset_axis_wt
                else:
                    summarized_participants_results[i][participants.index(participant[0]["participant"])] = part_average_offset_axis

        print("\n##Results for Rest Condition: ", i + 1)
        print("average offset " + axis + ": ", distance_axis_amount / len(rest_condition))
        print("average offset " + axis + " wt: ", distance_axis_amount_wt / len(rest_condition))

        if weighted:
            summarized_conditions_results.append(distance_axis_amount_wt / len(rest_condition))
        else:
            summarized_conditions_results.append(distance_axis_amount / len(rest_condition))

    return [summarized_conditions_results, summarized_participants_results]


def analyze_fixations(participants, participant_id, all_fixations_x_per_rest_condition, all_fixations_y_per_rest_condition):
    with open(join(PATH_DATA_PREPROCESSED, "fixations", participant_id + ".pkl"), 'rb') as input:
        fixations = pickle.load(input)

        print("\n## " + participant_id)

        current_rest_condition = 0

        distance_amount_all = [0, 0]
        distance_count_all = [0, 0]
        distance_amount_filtered = [0, 0]
        distance_count_filtered = [0, 0]
        distance_amount_filtered_weighted = [0, 0]
        distance_count_filtered_weighted = [0, 0]

        for fixation in fixations:
            if fixation["trial_category"] == "Rest":
                if fixation["rest_condition"] != current_rest_condition:
                    current_rest_condition = fixation["rest_condition"]
                    #print("\n\n\n")
                    #print("new rest condition! ", current_rest_condition)

                # print("-> found fixation after " + str(fixation["frames"]) + " frames, for " + fixation["data"][2] + " msec, at position x=" + fixation["data"][3] + ", y=" + fixation["data"][4])

                distance_x = float(fixation["data"][3]) - fixation_cross_x
                distance_y = float(fixation["data"][4]) - fixation_cross_y

                distance_amount_all[0] += abs(distance_x)
                distance_count_all[0] += 1

                distance_amount_all[1] += abs(distance_y)
                distance_count_all[1] += 1

                # ignore fixations withint the first 500ms
                if fixation["frames"] > 500:
                    if 0 < float(fixation["data"][4]) < 1000:
                        if abs(distance_y) < 300:
                            distance_amount_filtered[1] += abs(distance_y)
                            distance_count_filtered[1] += 1

                            distance_amount_filtered_weighted[1] += float(fixation["data"][2]) * abs(distance_y)
                            distance_count_filtered_weighted[1] += float(fixation["data"][2])

                            participant_pos = participants.index(participant_id)
                            all_fixations_y_per_rest_condition[current_rest_condition][participant_pos].append({
                                "participant": participant_id,
                                "rest_condition": current_rest_condition,
                                "fixation_distance": abs(distance_y),
                                "fixation_length": abs(float(fixation["data"][2]))
                            })

                    if 0 < float(fixation["data"][3]) < 1200:
                        if abs(distance_x) < 300:
                            distance_amount_filtered[0] += abs(distance_x)
                            distance_count_filtered[0] += 1

                            distance_amount_filtered_weighted[0] += float(fixation["data"][2]) * abs(distance_x)
                            distance_count_filtered_weighted[0] += float(fixation["data"][2])

                            participant_pos = participants.index(participant_id)
                            all_fixations_x_per_rest_condition[current_rest_condition][participant_pos].append({
                                "participant": participant_id,
                                "rest_condition": current_rest_condition,
                                "fixation_distance": abs(distance_x),
                                "fixation_length": abs(float(fixation["data"][2]))
                            })

        print("average offset x all: ", distance_amount_all[0] / distance_count_all[0])
        print("average offset x filtered: ", distance_amount_filtered[0]/distance_count_filtered[0])
        print("average offset x filt + wt: ", distance_amount_filtered_weighted[0] / distance_count_filtered_weighted[0])
        print("")
        print("average offset y all: ", distance_amount_all[1] / distance_count_all[1])
        print("average offset y filtered: ", distance_amount_filtered[1]/distance_count_filtered[1])
        print("average offset y filt + wt: ", distance_amount_filtered_weighted[1] / distance_count_filtered_weighted[1])

    return [all_fixations_x_per_rest_condition, all_fixations_y_per_rest_condition]


def write_participants_to_csv_file(participants, results_x, results_y, weighted):
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if weighted:
        output_file_path = join(PATH_DATA_OUTPUT, "average_offset_participant_weighted.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "average_offset_participant.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("time;axis;value;subject\n")

        extract_and_write_lines(file_write, participants, results_x, "x")
        extract_and_write_lines(file_write, participants, results_y, "y")

    print("-> saving file: done!")


def extract_and_write_lines(file_write, participants, results, axis):
    for i, line in enumerate(results):
        for participant_pos, line in enumerate(line):
            if line is not None:
                file_write(str(i + 1) + ";" + axis + ";" + str(round(line, 2)) + ";" + participants[participant_pos] + "\n")
            else:
                # have to fill in blanks, otherwise Seaborn won't draw correctly
                fallback = results[i-1][participant_pos]
                if fallback is None:
                    fallback = 50
                file_write(str(i + 1) + ";" + axis + ";" + str(round(fallback, 2)) + ";" + participants[participant_pos] + "\n")


def write_averages_to_csv_file(results_x, results_y, weighted):
    print("\n====================\n")
    print("Final step: write everything to a csv file...")

    # write objects to file as giant csv
    if weighted:
        output_file_path = join(PATH_DATA_OUTPUT, "average_offset_condition_weighted.csv")
    else:
        output_file_path = join(PATH_DATA_OUTPUT, "average_offset_condition.csv")

    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("time;axis;value;subject\n")

        for i, line in enumerate(results_x):
            file_write(str(i+1) + ";x;" + str(round(line, 2)) + ";average\n")

        for i, line in enumerate(results_y):
            file_write(str(i+1) + ";y;" + str(round(line, 2)) + ";average\n")

    print("-> saving file: done!")


if __name__ == "__main__": analyze_rest_condition_offset(PARTICIPANTS)
