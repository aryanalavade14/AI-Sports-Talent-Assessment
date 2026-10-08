import csv
from analyze import analyze_jump

errors = []
with open("results.csv") as f:
    for row in csv.DictReader(f):
        cv_cm = analyze_jump(f"videos/{row['video']}", float(row["height_cm"]))["jump_cm"]
        tape = float(row["tape_cm"])
        err = abs(cv_cm - tape)
        errors.append(err)
        print(f"{row['person']}: tape={tape}  cv={cv_cm}  error={err:.1f}")

print(f"\nAverage error: {sum(errors)/len(errors):.2f} cm")