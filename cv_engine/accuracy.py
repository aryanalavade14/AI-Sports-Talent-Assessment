import csv
from analyze import analyze_jump

errors = []
with open("results.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        res = analyze_jump(f"videos/{row['video']}", float(row["height_cm"]))
        if res["status"] != "ok":
            print(f"{row['person']}: ERROR - {res['message']}")
            continue
        cv_cm = res["jump_cm"]
        tape = float(row["tape_cm"])
        err = cv_cm - tape
        errors.append(abs(err))
        print(f"{row['person']}: tape={tape}  cv={cv_cm}  error={err:+.1f}")

if errors:
    print(f"\nAverage error: {sum(errors)/len(errors):.2f} cm")
