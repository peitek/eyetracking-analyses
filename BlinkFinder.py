from os.path import join

import _pickle as pickle
import re

from config import PATH_DATA_RAW, PATH_DATA_PREPROCESSED, PARTICIPANTS

# TODO clean up code
# TODO comment/document functions

trial = 0
workaround_for_pilot_zp65 = False


def find_blinks_for_participants(participants):
    for participant in participants:
        find_blinks_for_single_participant(participant)


def find_blinks_for_single_participant(participant_name):
    print("\nParse eyetracking data...")

    eyetracking_input_file_path = join(PATH_DATA_RAW, participant_name + ".asc")

    # read in eyelink file line for line
    all_lines = []

    global trial

    print("Reading file...")
    with open(eyetracking_input_file_path) as input_file:
        frames_size_code_counter = 0
        trial_image = ""
        trial_category = ""
        sequence = 0
        d2_task_number = 1
        dec_time_number = 1
        rest_number = 1
        timestamp = 1
        subject = participant_name
        snippet = ""

        gaze_positions_recognized = 0
        gaze_positions_not_recognized = 0

        rest_condition = 0
        blink_count = 0

        # TODO extract all blink lines to analyze them
        all_blinks = []

        for i, line in enumerate(input_file):
            if (i % 100000) == 0:
                print("-> Read row of eyetracking: ", i)

            if workaround_for_pilot_zp65:
                # if the current one is code
                if not snippet.startswith("D2") and not snippet.startswith("Rest") and not snippet.startswith("DecTime"):
                    if frames_size_code_counter >= 30000:
                        print("--> switching to decision time after frames: ", frames_size_code_counter)
                        snippet = "DecTime" + str(dec_time_number)
                        trial_image = "dec_time_" + str(dec_time_number) + ".png"
                        frames_size_code_counter = 0
                        trial += 1
                        dec_time_number += 1
                elif not snippet.startswith("D2") and not snippet.startswith("Rest"):
                    if frames_size_code_counter >= 2000:
                        print("--> switching to d2 after frames: ", frames_size_code_counter)
                        snippet = "D2_" + str(d2_task_number)
                        trial_image = "attention_task_" + str(d2_task_number) + ".png"
                        frames_size_code_counter = 0
                        trial += 1
                        d2_task_number += 1
                elif not snippet.startswith("D2") and frames_size_code_counter >= 15000:
                    print("--> switching to rest after frames: ", frames_size_code_counter)
                    snippet = "Rest" + str(rest_number)
                    trial_image = "rest_" + str(rest_number) + ".png"
                    frames_size_code_counter = 0
                    trial += 1
                    rest_number += 1

            if line[0].isdigit():
                frames_size_code_counter += 1
                timestamp += 1

            elif line[0].isalpha():
                if "EBLINK L" in line or "EBLINK R" in line:
                    blink_info = re.split(r'\t+', line.rstrip('\t'))
                    print("----> found blink after " + str(frames_size_code_counter) + " frames, for " + blink_info[2] + " msec")
                    all_blinks.append({
                        "trial_category": trial_category,
                        "snippet": snippet,
                        "timestamp": timestamp,
                        "rest_condition": rest_condition,
                        "frames": frames_size_code_counter,
                        "data": blink_info
                    })
                    blink_count += 1

                elif "Rest Condition" in line:
                    snippet = "Rest" + str(rest_number)
                    trial_image = "rest_" + str(rest_number) + ".png"
                    rest_number += 1
                    print("--> found rest condition " + str(rest_condition) + " after frames ", frames_size_code_counter)
                    trial_category = "Rest"
                    rest_condition += 1
                    frames_size_code_counter = 0
                    sequence += 1
                    trial += 1
                elif "Last Response" in line:
                    print("--> switching to decision time after frames: ", frames_size_code_counter)
                    snippet = "DecTime" + str(dec_time_number)
                    trial_image = "dec_time_" + str(dec_time_number) + ".png"
                    trial_category = "DecTime"
                    frames_size_code_counter = 0
                    sequence += 1
                    trial += 1
                    dec_time_number += 1
                elif "D2 Task" in line:
                    print("--> switching to d2 after frames: ", frames_size_code_counter)
                    snippet = "D2_" + str(d2_task_number)
                    trial_image = "attention_task_" + str(d2_task_number) + ".png"
                    trial_category = "D2"
                    frames_size_code_counter = 0
                    sequence += 1
                    trial += 1
                    d2_task_number += 1
                elif "!V IMGLOAD FILL" in line:
                    startpos = line.rfind("\\")
                    snippet = line[startpos+1:].replace('\r', '').replace('\n', '')
                    trial_image = snippet

                    print("--> found snippet " + snippet + " after frames ", frames_size_code_counter)

                    if "TD_B" in snippet:
                        trial_category = "Compr_TD_B"
                    elif "TD_N" in snippet:
                        trial_category = "Compr_TD_N"
                    elif "TD_U" in snippet:
                        trial_category = "Compr_TD_U"
                    elif "SY" in snippet:
                        trial_category = "Syntax"
                    else:
                        trial_category = "Compr_BU"

                    frames_size_code_counter = 0
                    sequence += 1
                    trial += 1
                elif "TRIALID TRIAL" in line:
                    startpos = line.find("TRIALID TRIAL")
                    #carry_over["TrialNumber"] = line[startpos+14:].replace('\r', '').replace('\n', '')
                elif "Subject" in line:
                    startpos = line.find("Subject")
                    subject = line[startpos+8:].replace('\r', '').replace('\n', '')

        print("-> Frames with gaze positions recognized: " + str(gaze_positions_recognized))
        print("-> Frames with gaze positions not recognized: " + str(gaze_positions_not_recognized))
        print("-> Amount of blinks: " + str(blink_count))

    # write fixations to file
    with open(join(PATH_DATA_PREPROCESSED, "blinks", participant_name + ".pkl"), 'wb') as output:
        pickle.dump(all_blinks, output)

    print("-> reading file: done!")

    return all_lines


if __name__ == "__main__": find_blinks_for_participants(PARTICIPANTS)
