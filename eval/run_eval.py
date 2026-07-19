import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from app import analyze_resume


def load_eval_set(path="eval/eval_set.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_eval(eval_set_path="eval/eval_set.json"):
    cases = load_eval_set(eval_set_path)
    results = []

    for case in cases:
        try:
            result = analyze_resume(case["resume_excerpt"], case["job_description"])
            ai_score = result["match_score"]
        except Exception as e:
            print(f"[{case['id']}] ERROR: {e}")
            continue

        human_score = case["human_score"]
        diff = abs(ai_score - human_score)
        results.append(diff)
        print(f"[{case['id']}] AI: {ai_score:>3} | Human: {human_score:>3} | Diff: {diff:>3}")

    if not results:
        print("\nNo cases evaluated. Check eval_set.json and imports.")
        return

    mean_abs_error = sum(results) / len(results)
    max_error = max(results)

    print("\n--- Summary ---")
    print(f"Cases evaluated: {len(results)}")
    print(f"Mean absolute error: {mean_abs_error:.1f} points")
    print(f"Max error: {max_error} points")
    print("\nPaste these numbers into the README Evaluation section.")


if __name__ == "__main__":
    run_eval()

