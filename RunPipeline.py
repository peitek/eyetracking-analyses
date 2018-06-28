import AoiAnalyzer
import BlinkAnalyzer
import BlinkFinder
import FixationFinder
import PupilDilationAnalyzer
import PupilDilationFinder
import ResponseAnalyzer
import RestConditionOffsetAnalyzer

from config import PARTICIPANTS

SKIP_PREPROCESSING = False


def main():
    # First, run all pre-processing (if requested)
    if not SKIP_PREPROCESSING:
        BlinkFinder.find_blinks_for_participants(PARTICIPANTS)
        FixationFinder.find_fixations_for_participants(PARTICIPANTS)
        PupilDilationFinder.extract_pupil_dilation_for_participants(PARTICIPANTS)

    # Second, run eye-tracking analyses
    AoiAnalyzer.run_aoi_analysis(PARTICIPANTS)
    BlinkAnalyzer.analyze_blinks_for_all_participants(PARTICIPANTS)
    PupilDilationAnalyzer.analyze_pupil_dilation_for_all_participants(PARTICIPANTS)
    PupilDilationAnalyzer.analyze_pupil_dilation_movement_for_all_participants(PARTICIPANTS)
    RestConditionOffsetAnalyzer.analyze_rest_condition_offset(PARTICIPANTS)

    # Third, run secondary analyses
    ResponseAnalyzer.analyze_responses()


if __name__ == "__main__": main()
