import AoiAnalyzer
import BlinkAnalyzer
import BlinkFinder
import FixationFinder

from config import PARTICIPANTS

SKIP_PREPROCESSING = True


def main():
    # First, run all pre-processing (if requested)
    if not SKIP_PREPROCESSING:
        BlinkFinder.find_blinks_for_participants(PARTICIPANTS)
        FixationFinder.find_fixations_for_participants(PARTICIPANTS)

    # Second, run analyses
    AoiAnalyzer.run_aoi_analysis(PARTICIPANTS)
    BlinkAnalyzer.analyze_pupil_dilation_for_all_participants(PARTICIPANTS)


if __name__ == "__main__": main()
