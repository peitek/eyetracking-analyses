from os.path import join

import _pickle as pickle
import re

from config import PATH_DATA_PREPROCESSED, PARTICIPANTS

# TODO clean up code
# TODO comment/document functions

trial = 0
workaround_for_pilot_zp65 = False


def extract_pupil_dilation_for_participants(participants):
    print("\nParse eyetracking data...")

    global trial

    for participant in participants:
        pupil_dilation = []
        print("Reading file...")
        eyetracking_input_file_path = join("data_raw", participant + ".asc")

        with open(eyetracking_input_file_path) as input_file:
            frames_size_code_counter = 0
            trial_image = ""
            trial_category = ""
            sequence = 0
            d2_task_number = 1
            dec_time_number = 1
            rest_number = 1
            timestamp = 1
            subject = participant
            snippet = ""

            gaze_positions_recognized = 0
            gaze_positions_not_recognized = 0

            rest_condition = 0
            fixation_count = 0

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
                    numbers = re.split(r'\t+', line.rstrip('\t'))
                    gaze_x = numbers[1].lstrip()

                    if is_number(gaze_x):
                        pupil_dilation.append({
                            "trial_category": trial_category,
                            "snippet": snippet,
                            "timestamp": timestamp,
                            "frames": frames_size_code_counter,
                            "gaze_x": gaze_x,
                            "gaze_y": numbers[2].lstrip(),
                            "pupil_dilation": numbers[3].lstrip()
                        })
                        fixation_count += 1

                    frames_size_code_counter += 1
                    timestamp += 1

                elif line[0].isalpha():
                    if "Rest Condition" in line:
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

        print("-> reading file: done!")

        # write fixations to file
        with open(join(PATH_DATA_PREPROCESSED, "full", participant + "_pupil_data_raw.pkl"), 'wb') as output:
            pickle.dump(pupil_dilation, output)

        print("-> writing file: done!")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__": extract_pupil_dilation_for_participants(PARTICIPANTS)
