from os.path import join
import math
import numpy
import _pickle as pickle

from config import PATH_DATA_PREPROCESSED, PATH_DATA_OUTPUT, PARTICIPANTS

# TODO remove participant codes
# TODO remove required response log file
# TODO remove required physio log file
# TODO generalize code better (e.g., conditions)
# TODO clean up code
# TODO comment/document functions


def analyze_pupil_dilation_for_all_participants(participants):
    average_amount_blinks_per_condition = []
    average_amount_blinks_per_snippet_time_participant = []
    average_amount_blinks_per_snippet_time = []
    average_amount_blinks_per_snippet_raw = {}
    average_amount_blinks_per_snippet_processed = []
    average_amount_blinks_over_time = []
    average_amount_blinks_over_time_grouped = {}

    amount_blinks_per_snippet = {}

    for participant in participants:
        amount_blinks_per_condition = {}
        amount_blinks_per_snippet_participant = {}
        amount_blinks_over_time = {}

        [amount_blinks_over_time, amount_blinks_per_condition, amount_blinks_per_snippet_participant, amount_blinks_per_snippet] = analyze_each_blink(participants, participant, amount_blinks_over_time, amount_blinks_per_condition, amount_blinks_per_snippet_participant, amount_blinks_per_snippet)

        print("\n#### ANALYSIS FOR PARTICIPANT")
        for timestamp in sorted(amount_blinks_over_time):
            data = amount_blinks_over_time[timestamp]

            average_amount_blinks_over_time.append({
                "participant": participant,
                "timestamp": timestamp,
                "blink_duration": math.floor(numpy.mean(data))
            })

            if math.floor(timestamp/10/60) not in average_amount_blinks_over_time_grouped:
                average_amount_blinks_over_time_grouped[math.floor(timestamp / 10/60)] = []
            else:
                average_amount_blinks_over_time_grouped[math.floor(timestamp / 10/60)].append(1)

        for condition in sorted(amount_blinks_per_condition):
            for timestamp in sorted(amount_blinks_per_condition[condition]):
                data = amount_blinks_per_condition[condition][timestamp]

                average_amount_blinks_per_condition.append({
                    "participant": participant,
                    "condition": condition,
                    "timestamp": timestamp,
                    "blink_duration": math.floor(numpy.mean(data))
                })

        for condition in sorted(amount_blinks_per_snippet_participant):
            for snippet in sorted(amount_blinks_per_snippet_participant[condition]):
                for timestamp in sorted(amount_blinks_per_snippet_participant[condition][snippet]):
                    data = amount_blinks_per_snippet_participant[condition][snippet][timestamp]

                    average_amount_blinks_per_snippet_time_participant.append({
                        "participant": participant,
                        "condition": condition,
                        "snippet": snippet,
                        "timestamp": timestamp,
                        "blink_duration": math.floor(numpy.mean(data))
                    })

    for condition in sorted(amount_blinks_per_snippet):
        for snippet in sorted(amount_blinks_per_snippet[condition]):
            for timestamp in sorted(amount_blinks_per_snippet[condition][snippet]):
                data = amount_blinks_per_snippet[condition][snippet][timestamp]
                average = math.floor(numpy.mean(data))

                average_amount_blinks_per_snippet_time.append({
                    "condition": condition,
                    "snippet": snippet,
                    "timestamp": timestamp,
                    "blink_duration": average
                })

                if snippet not in average_amount_blinks_per_snippet_raw:
                    average_amount_blinks_per_snippet_raw[snippet] = []

                average_amount_blinks_per_snippet_raw[snippet].append({
                    "condition": condition,
                    "snippet": snippet,
                    "blink_duration": average
                })

    for condition in sorted(amount_blinks_per_snippet):
        for snippet in sorted(amount_blinks_per_snippet[condition]):
            for timestamp in sorted(amount_blinks_per_snippet[condition][snippet]):
                data = amount_blinks_per_snippet[condition][snippet][timestamp]
                average = math.floor(numpy.mean(data))

                average_amount_blinks_per_snippet_processed.append({
                    "condition": condition,
                    "snippet": snippet,
                    "timestamp": timestamp,
                    "blink_duration": average
                })

    print("\n#### WRITE RESULTS TO CSV")

    for minute in sorted(average_amount_blinks_over_time_grouped):
        print(str(minute) + ": " + str(len(average_amount_blinks_over_time_grouped[minute])))

    #write_dilation_over_time(amount_blinks_over_time)
    #write_dilation_per_condition(amount_blinks_per_condition)
    write_blink_rate_per_snippet_participant(average_amount_blinks_per_snippet_time_participant)
    #write_dilation_per_snippet(average_amount_blinks_over_time)

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


def write_dilation_per_snippet(average_blink_rate_per_snippet):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "blink_rate_snippet.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("condition;snippet;time;blink_duration;subject\n")

        for line in average_blink_rate_per_snippet:
            file_write(line["condition"] + ";" + line["snippet"] + ";" + str(line["timestamp"]) + ";" + str(line["blink_duration"]) + ";average\n")


def write_blink_rate_per_snippet_participant(amount_blinks_per_snippet_participant):
    # write objects to file as giant csv
    output_file_path = join(PATH_DATA_OUTPUT, "blink_rate_snippet_participant.csv")
    with open(output_file_path, 'w') as output_file:
        file_write = output_file.write
        file_write("participant;condition;snippet;time;blink_rate\n")

        for line in amount_blinks_per_snippet_participant:
            file_write(line["participant"] + ";" + line["condition"] + ";" + line["snippet"] + ";" + str(line["timestamp"]) + ";" + str(line["blink_duration"]) + "\n")


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


def analyze_each_blink(participants, participant_id, pupil_dilation_over_time, pupil_dilation_per_condition, pupil_dilation_per_snippet_participant, pupil_dilation_per_snippet):
    with open(join(PATH_DATA_PREPROCESSED, "blinks", participant_id + ".pkl"), 'rb') as input:
        blink_data = pickle.load(input)

        print("\n## " + participant_id)
        trial_category = None

        for blink in blink_data:
            if trial_category != blink["trial_category"]:
                #print("switched to " + blink["trial_category"] + " after " + str(blink["timestamp"]))
                trial_category = blink["trial_category"]

            # per condition
            grouped_frame_10 = math.floor(blink["frames"]/10)
            if trial_category not in pupil_dilation_per_condition:
                pupil_dilation_per_condition[trial_category] = {}

            if grouped_frame_10 not in pupil_dilation_per_condition[trial_category]:
                pupil_dilation_per_condition[trial_category][grouped_frame_10] = []

            pupil_dilation_per_condition[trial_category][grouped_frame_10].append(math.floor(float(blink["data"][2])))

            # per snippet
            set_snippet_to_data(blink, pupil_dilation_per_snippet_participant, trial_category)
            set_snippet_to_data(blink, pupil_dilation_per_snippet, trial_category)

            # over time
            grouped_time = math.floor(blink["timestamp"]/100)
            if grouped_time not in pupil_dilation_over_time:
                pupil_dilation_over_time[grouped_time] = []

            pupil_dilation_over_time[grouped_time].append(math.floor(float(blink["data"][2])))

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

        pupil_dilation_dict[trial_category][snippet][grouped_frame_100].append(math.floor(float(et_frame["data"][2])))


if __name__ == "__main__": analyze_pupil_dilation_for_all_participants(PARTICIPANTS)
