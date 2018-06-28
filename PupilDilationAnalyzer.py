from os.path import join
import math
import numpy
import _pickle as pickle

from config import PATH_DATA_RAW, PATH_DATA_PREPROCESSED, PATH_DATA_OUTPUT

# TODO remove participant codes
# TODO remove required response log file
# TODO remove required physio log file
# TODO generalize code better (e.g., conditions)
# TODO clean up code
# TODO comment/document functions


def main():
    #participants = ["bo23", "ea65", "ia67", "ks01", "mk55", "on85", "qe90", "qw51", "qv57", "zp65"]
    participants = ["bo23", "ea65", "ia67", "ks01", "mk55", "qe90", "qw51", "zp65"]
    #participants = ["ks01"]

    analyze_pupil_dilation_for_all_participants(participants)
    #analyze_pupil_dilation_movement_for_all_participants(participants)


def analyze_pupil_dilation_movement_for_all_participants(participants):
    average_dilation_gaze_pos_over_time = []

    for participant in participants:
        pupil_dilation_over_time = {}

        pupil_dilation_over_time = analyze_each_frame_movement(participants, participant, pupil_dilation_over_time)

        print("\n#### ANALYSIS FOR PARTICIPANT")
        for timestamp in sorted(pupil_dilation_over_time):
            data = pupil_dilation_over_time[timestamp]

            average_dilation_gaze_pos_over_time.append({
                "participant": participant,
                "timestamp": timestamp,
                "average_dilation": math.floor(numpy.mean([item['pupil_dilation'] for item in data])),
                "gaze_x": math.floor(numpy.mean([item['gaze_x'] for item in data])),
                "gaze_y": math.floor(numpy.mean([item['gaze_y'] for item in data])),
            })

    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "pupil_dilation_gaze_pos_time_sec.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("time;gaze_x;gaze_y;pupil_dilation;subject\n")

        for line in average_dilation_gaze_pos_over_time:
            file_write(str(line["timestamp"]) + ";" + str(line["gaze_x"]) + ";"+ str(line["gaze_y"]) + ";"+ str(line["average_dilation"]) + ";" + line["participant"] + "\n")


def analyze_pupil_dilation_for_all_participants(participants):
    average_dilation_per_condition = []
    average_dilation_per_snippet_time_participant = []
    average_dilation_per_snippet_time = []
    average_dilation_per_snippet_raw = {}
    average_dilation_per_snippet_processed = []
    average_dilation_over_time = []

    pupil_dilation_per_snippet = {}

    for participant in participants:
        pupil_dilation_per_condition = {}
        pupil_dilation_per_snippet_participant = {}
        pupil_dilation_over_time = {}

        [pupil_dilation_over_time, pupil_dilation_per_condition, pupil_dilation_per_snippet_participant, pupil_dilation_per_snippet] = analyze_each_frame(participants, participant, pupil_dilation_over_time, pupil_dilation_per_condition, pupil_dilation_per_snippet_participant, pupil_dilation_per_snippet)

        print("\n#### ANALYSIS FOR PARTICIPANT")
        for timestamp in sorted(pupil_dilation_over_time):
            data = pupil_dilation_over_time[timestamp]

            average_dilation_over_time.append({
                "participant": participant,
                "timestamp": timestamp,
                "average_dilation": math.floor(numpy.mean(data))
            })

        for condition in sorted(pupil_dilation_per_condition):
            for timestamp in sorted(pupil_dilation_per_condition[condition]):
                data = pupil_dilation_per_condition[condition][timestamp]

                average_dilation_per_condition.append({
                    "participant": participant,
                    "condition": condition,
                    "timestamp": timestamp,
                    "average_dilation": math.floor(numpy.mean(data))
                })

        for condition in sorted(pupil_dilation_per_snippet_participant):
            for snippet in sorted(pupil_dilation_per_snippet_participant[condition]):
                for timestamp in sorted(pupil_dilation_per_snippet_participant[condition][snippet]):
                    data = pupil_dilation_per_snippet_participant[condition][snippet][timestamp]

                    average_dilation_per_snippet_time_participant.append({
                        "participant": participant,
                        "condition": condition,
                        "snippet": snippet,
                        "timestamp": timestamp,
                        "average_dilation": math.floor(numpy.mean(data))
                    })

    for condition in sorted(pupil_dilation_per_snippet):
        for snippet in sorted(pupil_dilation_per_snippet[condition]):
            for timestamp in sorted(pupil_dilation_per_snippet[condition][snippet]):
                data = pupil_dilation_per_snippet[condition][snippet][timestamp]
                average = math.floor(numpy.mean(data))

                average_dilation_per_snippet_time.append({
                    "condition": condition,
                    "snippet": snippet,
                    "timestamp": timestamp,
                    "average_dilation": average
                })

                if snippet not in average_dilation_per_snippet_raw:
                    average_dilation_per_snippet_raw[snippet] = []

                average_dilation_per_snippet_raw[snippet].append({
                    "condition": condition,
                    "snippet": snippet,
                    "average_dilation": average
                })

    for condition in sorted(pupil_dilation_per_snippet):
        for snippet in sorted(pupil_dilation_per_snippet[condition]):
            for timestamp in sorted(pupil_dilation_per_snippet[condition][snippet]):
                data = pupil_dilation_per_snippet[condition][snippet][timestamp]
                average = math.floor(numpy.mean(data))

                average_dilation_per_snippet_processed.append({
                    "condition": condition,
                    "snippet": snippet,
                    "timestamp": timestamp,
                    "average_dilation": average
                })

    print("\n#### WRITE RESULTS TO CSV")

    write_dilation_over_time(average_dilation_over_time)
    write_dilation_per_condition(average_dilation_per_condition)
    write_dilation_per_snippet_participant(average_dilation_per_snippet_time_participant)
    write_dilation_per_snippet(average_dilation_per_snippet_time)

    print("-> saving file: done!")


def write_dilation_over_time(average_dilation_over_time):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "pupil_dilation_time_sec.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("time;pupil_dilation;subject\n")

        for line in average_dilation_over_time:
            file_write(str(line["timestamp"]) + ";" + str(line["average_dilation"]) + ";" + line["participant"] + "\n")


def write_dilation_per_condition(average_dilation_per_condition):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "pupil_dilation_condition.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("condition;time;pupil_dilation;subject\n")

        for line in average_dilation_per_condition:
            file_write(line["condition"] + ";" + str(line["timestamp"]) + ";" + str(line["average_dilation"]) + ";" + line["participant"] + "\n")


def write_dilation_per_snippet(average_dilation_per_snippet):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "pupil_dilation_snippet.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("condition;snippet;time;pupil_dilation;subject\n")

        for line in average_dilation_per_snippet:
            file_write(line["condition"] + ";" + line["snippet"] + ";" + str(line["timestamp"]) + ";" + str(line["average_dilation"]) + ";average\n")


def write_dilation_per_snippet_participant(average_dilation_per_snippet_participant):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "pupil_dilation_snippet_participant.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("condition;snippet;time;pupil_dilation;subject\n")

        for line in average_dilation_per_snippet_participant:
            file_write(line["condition"] + ";" + line["snippet"] + ";" + str(line["timestamp"]) + ";" + str(line["average_dilation"]) + ";" + line["participant"] + "\n")


def analyze_each_frame_movement(participants, participant_id, pupil_dilation_over_time):
    with open(join(PATH_DATA_PREPROCESSED, "fixations", participant_id + "_pupil_data_raw.pkl"), 'rb') as input:
        eyetracking_data = pickle.load(input)

        print("\n## " + participant_id)

        for et_frame in eyetracking_data:
            # over time
            grouped_time = math.floor(et_frame["timestamp"]/100)
            if grouped_time not in pupil_dilation_over_time:
                pupil_dilation_over_time[grouped_time] = []

            pupil_dilation_over_time[grouped_time].append({
                "pupil_dilation": math.floor(float(et_frame["pupil_dilation"])),
                "gaze_x": math.floor(float(et_frame["gaze_x"])),
                "gaze_y": math.floor(float(et_frame["gaze_y"])),
            })

    return pupil_dilation_over_time


def analyze_each_frame(participants, participant_id, pupil_dilation_over_time, pupil_dilation_per_condition, pupil_dilation_per_snippet_participant, pupil_dilation_per_snippet):
    with open(join(PATH_DATA_PREPROCESSED, "fixations", participant_id + "_pupil_data_raw.pkl"), 'rb') as input:
        eyetracking_data = pickle.load(input)

        print("\n## " + participant_id)
        trial_category = None

        for et_frame in eyetracking_data:
            #print("-> found frame for " + str(et_frame["snippet"]) + " after " + str(et_frame["frames"]) + " frames, pupil dilation: " + et_frame["pupil_dilation"])

            if trial_category != et_frame["trial_category"]:
                #print("switched to " + et_frame["trial_category"] + " after " + str(et_frame["timestamp"]))
                trial_category = et_frame["trial_category"]

            # per condition
            grouped_frame_10 = math.floor(et_frame["frames"]/10)
            if trial_category not in pupil_dilation_per_condition:
                pupil_dilation_per_condition[trial_category] = {}

            if grouped_frame_10 not in pupil_dilation_per_condition[trial_category]:
                pupil_dilation_per_condition[trial_category][grouped_frame_10] = []

            pupil_dilation_per_condition[trial_category][grouped_frame_10].append(math.floor(float(et_frame["pupil_dilation"])))

            # per snippet
            set_snippet_to_data(et_frame, pupil_dilation_per_snippet_participant, trial_category)
            set_snippet_to_data(et_frame, pupil_dilation_per_snippet, trial_category)

            # over time
            grouped_time = math.floor(et_frame["timestamp"]/100)
            if grouped_time not in pupil_dilation_over_time:
                pupil_dilation_over_time[grouped_time] = []

            pupil_dilation_over_time[grouped_time].append(math.floor(float(et_frame["pupil_dilation"])))

    return [pupil_dilation_over_time, pupil_dilation_per_condition, pupil_dilation_per_snippet_participant, pupil_dilation_per_snippet]


def set_snippet_to_data(et_frame, pupil_dilation_dict, trial_category):
    grouped_frame_100 = math.floor(et_frame["frames"] / 100)
    if trial_category not in pupil_dilation_dict:
        pupil_dilation_dict[trial_category] = {}
    snippet = et_frame["snippet"]
    if snippet not in pupil_dilation_dict[trial_category]:
        pupil_dilation_dict[trial_category][snippet] = {}
    if grouped_frame_100 not in pupil_dilation_dict[trial_category][snippet]:
        pupil_dilation_dict[trial_category][snippet][grouped_frame_100] = []

        pupil_dilation_dict[trial_category][snippet][grouped_frame_100].append(math.floor(float(et_frame["pupil_dilation"])))


main()
