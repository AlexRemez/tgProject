from db.models import ExerciseResults


def is_better(best_exam: ExerciseResults, current_res: str):
    best_result = best_exam.results
    best_stat = 0
    for i in best_result:
        if i == "✅":
            best_stat += 1
    current_stat = 0
    for i in current_res:
        if i == "✅":
            current_stat += 1

    return current_stat > best_stat
