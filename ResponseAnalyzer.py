import copy
from os.path import join, isfile
import math
import os

from config import PATH_DATA_RAW, PATH_DATA_OUTPUT

# TODO move this file into a separate project
# TODO remove hard-coded conditions
# TODO extract d2 conditions?


def analyze_responses():
    # read all files from input directory and loop through them
    only_files = [f for f in os.listdir(join(PATH_DATA_RAW)) if isfile(join(PATH_DATA_RAW, f))]

    comprehension_results = []
    d2_results = []

    for file_name in only_files:
        if "response.log" in file_name or "ProgCode3_Eyetracking.log" in file_name:
            participant_id = file_name[:4]

            all_stimuli = parse_response_data(participant_id, file_name)
            all_stimuli = move_d2_clicks_to_late_response(all_stimuli)
            [top_down_beacon, top_down_no_beacon, top_down_untrained, bottom_up, syntax, d2] = analyze_data(all_stimuli)
            comprehension_results.append({
                "participant_id": participant_id,
                "top_down_beacon": top_down_beacon,
                "top_down_no_beacon": top_down_no_beacon,
                "top_down_untrained": top_down_untrained,
                "bottom_up": bottom_up,
                "syntax": syntax
            })

            d2 = analyze_d2(d2)
            d2_results.append({
                "participant_id": participant_id,
                "d2": d2
            })

    write_csv_file_comprehension(comprehension_results)
    write_csv_file_d2(d2_results)


def parse_response_data(participant_id, file_name):
    print("\nParse response data...")

    response_input_file_path = join("data_raw", file_name)

    all_stimuli = []

    with open(response_input_file_path) as input_file:
        start = False
        late_response = False
        initial_timestampMs = 0
        current_stimulus = None

        for i, line in enumerate(input_file):
            if (i % 100) == 0:
                print("-> Read row of response log: ", i)

            elements = line.split("\t")

            if not start and i == 9:
                initial_timestampMs = int(elements[4])
                start = True

            if start and elements[2] == "Picture":
                if elements[3] == "LastResponseCondition":
                    late_response = True
                    continue

                late_response = False

                if current_stimulus is not None:
                    all_stimuli.append(current_stimulus)

                current_stimulus = {
                    "name": elements[3],
                    "timestamp": math.floor((int(elements[4]) - initial_timestampMs) / 10),
                    "responses": [],
                    "late_responses": []
                }

            if start and elements[2] == "Response":
                timestampMs = math.floor((int(elements[4]) - initial_timestampMs) / 10)

                try:
                    if late_response:
                        current_stimulus["late_responses"].append({
                            "timestamp": timestampMs,
                            "response": elements[3],
                            "stimulus": current_stimulus["name"],
                            "response_time": timestampMs - current_stimulus["timestamp"]
                        })
                    else:
                        current_stimulus["responses"].append({
                            "timestamp": timestampMs,
                            "response": elements[3],
                            "stimulus": current_stimulus["name"],
                            "response_time": timestampMs - current_stimulus["timestamp"]
                        })
                except:
                    print("Exception: this shouldn't happen...")
                    break

    return all_stimuli


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def analyze_data(all_stimuli):
    print("#############")
    print("Summarizing and analyzing data now...")

    d2 = {
        "count": 0,
        "responded": 0,
        "overall_clicks": 0,

        "correct": 0,
        "incorrect": 0,

        "runs": []
    }

    for i, line in enumerate(all_stimuli):
        if "TD_B" in line["name"]:
            analyze_comprehension_stimulus(line, "TD_B")
        elif "TD_N" in line["name"]:
            analyze_comprehension_stimulus(line, "TD_N")
        elif "TD_U" in line["name"]:
            analyze_comprehension_stimulus(line, "TD_U")
        elif "BinaryToDecimal" in line["name"] or "Factorial" in line["name"] or "CountVowels" in line["name"] or "Maximum" in line["name"] or "IntertwineTwoWords" in line["name"]:
            analyze_comprehension_stimulus(line, "BU")

        elif "SY" in line["name"]:
            analyze_comprehension_stimulus(line, "SY")

        elif "D2" in line["name"]:
            line["condition"] = "D2"
            analyze_d2_stimulus(line, d2)

        elif "RestCondition" in line["name"]:
            if len(line["responses"]) > 0:
                print('click in rest condition o.O')
            continue

        else:
            print('unknown stimulus (' + line["name"] + ') ' + str(i))

    return finalize_comprehension_summary(all_stimuli, d2)


def finalize_comprehension_summary(all_stimuli, d2):
    for stimuli in all_stimuli:
        if "D2" not in stimuli["name"] and "Rest" not in stimuli["name"]:
            stimuli["summary"]["not_responded"] = 1 - stimuli["summary"]["responded"]

    top_down_beacon = []
    top_down_no_beacon = []
    top_down_untrained = []
    bottom_up = []
    syntax = []

    for i, line in enumerate(all_stimuli):
        if "TD_B" in line["name"]:
            top_down_beacon.append(line)
        elif "TD_N" in line["name"]:
            top_down_no_beacon.append(line)
        elif "TD_U" in line["name"]:
            top_down_untrained.append(line)
        elif "BinaryToDecimal" in line["name"] or "Factorial" in line["name"] or "CountVowels" in line["name"] or "Maximum" in line["name"] or "IntertwineTwoWords" in line["name"]:
            bottom_up.append(line)
        elif "SY" in line["name"]:
            syntax.append(line)

    return [top_down_beacon, top_down_no_beacon, top_down_untrained, bottom_up, syntax, d2]


def analyze_d2_stimulus(line, stimulus_summary):
    stimulus_summary["count"] += 1
    stimulus_summary["overall_clicks"] += len(line["responses"])/2

    clicks = []

    if len(line["responses"]) > 0:
        stimulus_summary["responded"] += 1

        current_click = None
        current_time = None
        for i, response in enumerate(line["responses"]):
            if current_click is None:
                current_click = response["response"] == '3'
                current_time = response["response_time"]
            else:
                clicks.append({
                    "choice": current_click,
                    "response_time": response["response_time"],
                    "click_time": response["response_time"] - current_time,
                })
                current_click = None

    stimulus_summary["runs"].append({
        "name": line["name"],
        "i": stimulus_summary["count"] - 1,
        "clicks": clicks
    })


def analyze_d2_click(resp, stimulus_summary):
    response = resp[len(resp) - 2]

    if response["response"] == '3':
        stimulus_summary["correct"] += 1
    else:
        stimulus_summary["incorrect"] += 1

    stimulus_summary["response_times"].append(response["response_time"])
    stimulus_summary["click_times"].append(resp[len(resp) - 1]["response_time"] - response["response_time"])


def is_click_d2(run, click):

    should_be_d2 = {
        0: [8, 10, 11, 12, 15, 16],
        1: [2, 6, 7, 17],
        2: [5, 6, 8, 13, 20],
        3: [3, 4, 14, 16, 17],
        4: [4, 7, 15, 16],
        5: [5, 16, 17, 19],
        6: [1, 3, 4, 6, 8, 10, 13, 15, 18, 20],
        7: [11, 12, 20],
        8: [1, 10, 13, 20],
        9: [2, 11, 13, 17],
        10: [11, 13],
        11: [6, 8, 11, 12, 14, 17, 19],
        12: [14],
        13: [1, 5, 15, 18],
        14: [5, 8, 12],
        15: [1, 2, 7, 14],
        16: [1, 5, 8],
        17: [3, 4, 10, 12],
        18: [3],
        19: [1, 4, 7, 13, 20],
        20: [8, 15, 17],
        21: [13, 14, 17, 18],
        22: [3, 5, 9, 13, 14, 18],
        23: [7, 8, 10, 17],
        24: [4, 6, 10]
    }.get(run, [])

    return (click+1) in should_be_d2


def analyze_d2(d2):
    for run in d2["runs"]:
        d2_overall = 0
        d2_recognized = 0
        d2_missed = 0
        d2_incorrect = 0
        p_correct = 0

        for i, click in enumerate(run["clicks"]):
            choice = click["choice"]
            is_d2 = is_click_d2(run["i"], i)

            if is_d2:
                d2_overall += 1

                if choice:
                    d2_recognized += 1
                else:
                    d2_missed += 1
            else:
                if choice:
                    d2_incorrect += 1
                else:
                    p_correct += 1

        run["d2_overall"] = d2_overall
        run["d2_recognized"] = d2_recognized
        run["d2_missed"] = d2_missed
        run["d2_incorrect"] = d2_incorrect
        run["p_correct"] = p_correct

    return d2


def move_d2_clicks_to_late_response(all_stimuli):
    # move early d2 clicks (within 500 ms to late click of the previous condition)
    for i, line in enumerate(all_stimuli):
        if line["name"].startswith('D2') and len(line["responses"]) > 0:
            response = line["responses"][0]

            if response["response_time"] < 500:
                response["response_time"] += 32000
                all_stimuli[i - 1]["late_responses"].append(response)
                line["responses"].pop(0)

                # move the matching button-up event as well
                if response['response'] == 7 or  response['response'] == 4:
                    all_stimuli[i - 1]["late_responses"].append(response)
                    line["responses"].pop(0)

    return all_stimuli


def analyze_comprehension_stimulus(line, condition):
    result_line = {
        "count": 0,
        "responded": 0,
        "not_responded": 0,

        "correct": 0,
        "incorrect": 0,

        "late_responses": 0,
        "multi_clicks": 0,
        "overall_clicks": 0,
        "response_times": [],
        "click_times": [],
    }

    line["condition"] = condition
    result_line["count"] += 1
    result_line["overall_clicks"] += math.ceil(len(line["responses"])/2 + len(line["late_responses"])/2)

    if len(line["late_responses"]) > 0:
        result_line["responded"] += 1
        result_line["late_responses"] += 1
        analyze_last_click_comprehension(line["late_responses"], result_line)

        if len(line["responses"]) > 0:
            result_line["multi_clicks"] += 1

    else:
        if len(line["responses"]) > 0:
            result_line["responded"] += 1
            analyze_last_click_comprehension(line["responses"], result_line)

        if len(line["responses"]) > 2:
            result_line["multi_clicks"] += 1

    line["summary"] = result_line


def analyze_last_click_comprehension(resp, stimulus_summary):
    response = resp[len(resp) - 2]

    if response["response"] == '3':
        stimulus_summary["correct"] += 1
    else:
        stimulus_summary["incorrect"] += 1

    stimulus_summary["response_times"].append(response["response_time"])

    click_time = resp[len(resp) - 1]["response_time"] - response["response_time"]

    if click_time < 0 and "D2" not in response["stimulus"]:
        # approximate fix for the broken click time
        click_time = (32000 - response["response_time"]) + resp[len(resp) - 1]["response_time"]

    stimulus_summary["click_times"].append(click_time)


def write_csv_file_d2(d2):
    print("\n====================\n")

    # write objects to file as one csv for all participants
    output_file_path = join(PATH_DATA_OUTPUT, "all_participant_d2.csv")
    with open(output_file_path, 'w') as output_file:
        output_file.write("Participant")
        output_file.write(';')
        output_file.write("Condition")
        output_file.write(';')
        output_file.write("Run")
        output_file.write(';')
        output_file.write("Count")
        output_file.write(';')
        output_file.write("D2 Overall")
        output_file.write(';')
        output_file.write("D2 Recognized")
        output_file.write(';')
        output_file.write("D2 Missed")
        output_file.write(';')
        output_file.write("D2 Incorrect")
        output_file.write(';')
        output_file.write("P Correct")
        output_file.write(';')
        output_file.write("ResponseTime1")
        output_file.write(';')
        output_file.write("ResponseTime2")
        output_file.write(';')
        output_file.write("ResponseTime3")
        output_file.write(';')
        output_file.write("ResponseTime4")
        output_file.write(';')
        output_file.write("ResponseTime5")
        output_file.write(';')
        output_file.write("ResponseTime6")
        output_file.write(';')
        output_file.write("ResponseTime7")
        output_file.write(';')
        output_file.write("ResponseTime8")
        output_file.write(';')
        output_file.write("ResponseTime9")
        output_file.write(';')
        output_file.write("ResponseTime10")
        output_file.write(';')
        output_file.write("ResponseTime11")
        output_file.write(';')
        output_file.write("ResponseTime12")
        output_file.write(';')
        output_file.write("ResponseTime13")
        output_file.write(';')
        output_file.write("ResponseTime14")
        output_file.write(';')
        output_file.write("ResponseTime15")
        output_file.write(';')
        output_file.write("ResponseTime16")
        output_file.write(';')
        output_file.write("ResponseTime17")
        output_file.write(';')
        output_file.write("ResponseTime18")
        output_file.write(';')
        output_file.write("ResponseTime19")
        output_file.write(';')
        output_file.write("ResponseTime20")
        output_file.write(';')
        output_file.write("ClickTime1")
        output_file.write(';')
        output_file.write("ClickTime2")
        output_file.write(';')
        output_file.write("ClickTime3")
        output_file.write(';')
        output_file.write("ClickTime4")
        output_file.write(';')
        output_file.write("ClickTime5")
        output_file.write(';')
        output_file.write("ClickTime6")
        output_file.write(';')
        output_file.write("ClickTime7")
        output_file.write(';')
        output_file.write("ClickTime8")
        output_file.write(';')
        output_file.write("ClickTime9")
        output_file.write(';')
        output_file.write("ClickTime10")
        output_file.write(';')
        output_file.write("ClickTime11")
        output_file.write(';')
        output_file.write("ClickTime12")
        output_file.write(';')
        output_file.write("ClickTime13")
        output_file.write(';')
        output_file.write("ClickTime14")
        output_file.write(';')
        output_file.write("ClickTime15")
        output_file.write(';')
        output_file.write("ClickTime16")
        output_file.write(';')
        output_file.write("ClickTime17")
        output_file.write(';')
        output_file.write("ClickTime18")
        output_file.write(';')
        output_file.write("ClickTime19")
        output_file.write(';')
        output_file.write("ClickTime20")

        for participant in d2:
            participant_name = participant["participant_id"]

            print("Write comprehension result to a csv file for ...", participant_name)
            for run in participant["d2"]["runs"]:
                output_file.write("\n")
                output_file.write(participant_name)
                output_file.write(';')
                output_file.write(run["name"])
                output_file.write(';')
                output_file.write(str(run["i"]))
                output_file.write(';')
                output_file.write(str(len(run["clicks"])))
                output_file.write(';')
                output_file.write(str(run["d2_overall"]))
                output_file.write(';')
                output_file.write(str(run["d2_recognized"]))
                output_file.write(';')
                output_file.write(str(run["d2_missed"]))
                output_file.write(';')
                output_file.write(str(run["d2_incorrect"]))
                output_file.write(';')
                output_file.write(str(run["p_correct"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) == 0 else str(run["clicks"][0]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 2 else str(run["clicks"][1]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 3 else str(run["clicks"][2]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 4 else str(run["clicks"][3]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 5 else str(run["clicks"][4]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 6 else str(run["clicks"][5]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 7 else str(run["clicks"][6]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 8 else str(run["clicks"][7]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 9 else str(run["clicks"][8]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 10 else str(run["clicks"][9]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 11 else str(run["clicks"][10]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 12 else str(run["clicks"][11]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 13 else str(run["clicks"][12]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 14 else str(run["clicks"][13]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 15 else str(run["clicks"][14]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 16 else str(run["clicks"][15]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 17 else str(run["clicks"][16]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 18 else str(run["clicks"][17]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 19 else str(run["clicks"][18]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 20 else str(run["clicks"][19]["response_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) == 0 else str(run["clicks"][0]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 2 else str(run["clicks"][1]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 3 else str(run["clicks"][2]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 4 else str(run["clicks"][3]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 5 else str(run["clicks"][4]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 6 else str(run["clicks"][5]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 7 else str(run["clicks"][6]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 8 else str(run["clicks"][7]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 9 else str(run["clicks"][8]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 10 else str(run["clicks"][9]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 11 else str(run["clicks"][10]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 12 else str(run["clicks"][11]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 13 else str(run["clicks"][12]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 14 else str(run["clicks"][13]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 15 else str(run["clicks"][14]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 16 else str(run["clicks"][15]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 17 else str(run["clicks"][16]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 18 else str(run["clicks"][17]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 19 else str(run["clicks"][18]["click_time"]))
                output_file.write(';')
                output_file.write("" if len(run["clicks"]) < 20 else str(run["clicks"][19]["click_time"]))

    print("-> saving file: done!")


def write_csv_file_comprehension(comprehension_results):
    print("\n====================\n")

    # write objects to file as one csv for all participants
    output_file_path = join(PATH_DATA_OUTPUT, "all_participant_responses.csv")
    with open(output_file_path, 'w') as output_file:
        output_file.write("Participant")
        output_file.write(';')
        output_file.write("Condition")
        output_file.write(';')
        output_file.write("Snippet")
        output_file.write(';')
        output_file.write("Count")
        output_file.write(';')
        output_file.write("Responded")
        output_file.write(';')
        output_file.write("Not Responded")
        output_file.write(';')
        output_file.write("Correct")
        output_file.write(';')
        output_file.write("Incorrect")
        output_file.write(';')
        output_file.write("Late Responded")
        output_file.write(';')
        output_file.write("MultiClicks")
        output_file.write(';')
        output_file.write("OverallClicks")
        output_file.write(';')
        output_file.write("ResponseTime1")
        output_file.write(';')
        output_file.write("ResponseTime2")
        output_file.write(';')
        output_file.write("ResponseTime3")
        output_file.write(';')
        output_file.write("ResponseTime4")
        output_file.write(';')
        output_file.write("ResponseTime5")
        output_file.write(';')
        output_file.write("ClickTime1")
        output_file.write(';')
        output_file.write("ClickTime2")
        output_file.write(';')
        output_file.write("ClickTime3")
        output_file.write(';')
        output_file.write("ClickTime4")
        output_file.write(';')
        output_file.write("ClickTime5")

        for participant in comprehension_results:
            participant_name = participant["participant_id"]

            print("Write comprehension result to a csv file for ...", participant_name)

            write_line_for_condition(output_file, participant_name, participant["top_down_beacon"], "TD_B")
            write_line_for_condition(output_file, participant_name, participant["top_down_no_beacon"], "TD_N")
            write_line_for_condition(output_file, participant_name, participant["top_down_untrained"], "TD_U")
            write_line_for_condition(output_file, participant_name, participant["bottom_up"], "BU")
            write_line_for_condition(output_file, participant_name, participant["syntax"], "SY")

    print("-> saving file: done!")


def write_line_for_condition(output_file, participant_name, conditions, name):
    for line in conditions:
        summary = line["summary"]

        output_file.write('\n')
        output_file.write(participant_name)
        output_file.write(';')
        output_file.write(name)
        output_file.write(';')
        output_file.write(line["name"])
        output_file.write(';')
        output_file.write(str(summary["count"]))
        output_file.write(';')
        output_file.write(str(summary["responded"]))
        output_file.write(';')
        output_file.write(str(summary["not_responded"]))
        output_file.write(';')
        output_file.write(str(summary["correct"]))
        output_file.write(';')
        output_file.write(str(summary["incorrect"]))
        output_file.write(';')
        output_file.write(str(summary["late_responses"]))
        output_file.write(';')
        output_file.write(str(summary["multi_clicks"]))
        output_file.write(';')
        output_file.write(str(summary["overall_clicks"]))
        output_file.write(';')
        output_file.write("" if len(summary["response_times"]) == 0 else str(summary["response_times"][0]))
        output_file.write(';')
        output_file.write("" if len(summary["response_times"]) < 2 else str(summary["response_times"][1]))
        output_file.write(';')
        output_file.write("" if len(summary["response_times"]) < 3 else str(summary["response_times"][2]))
        output_file.write(';')
        output_file.write("" if len(summary["response_times"]) < 4 else str(summary["response_times"][3]))
        output_file.write(';')
        output_file.write("" if len(summary["response_times"]) < 5 else str(summary["response_times"][4]))
        output_file.write(';')
        output_file.write("" if len(summary["click_times"]) == 0 else str(summary["click_times"][0]))
        output_file.write(';')
        output_file.write("" if len(summary["click_times"]) < 2 else str(summary["click_times"][1]))
        output_file.write(';')
        output_file.write("" if len(summary["click_times"]) < 3 else str(summary["click_times"][2]))
        output_file.write(';')
        output_file.write("" if len(summary["click_times"]) < 4 else str(summary["click_times"][3]))
        output_file.write(';')
        output_file.write("" if len(summary["click_times"]) < 5 else str(summary["click_times"][4]))


if __name__ == "__main__": analyze_responses()
