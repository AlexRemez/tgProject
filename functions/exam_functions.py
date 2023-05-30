from db.models import ExerciseResults, Exercises, Tags


def int_result(result: str):
    res = 0
    for i in result:
        if i == "✅":
            res += 1
    return res


async def calculate_points(exam_id: int):
    exam = await ExerciseResults.get(id=exam_id)
    current_res = int_result(exam.results)
    ex: Exercises = exam.exercise
    exam_level: Tags = await ex.get_level()
    exam_level = exam_level.tag_name
    multiplier = int(exam_level.split("-")[-1])
    current_points = current_res * multiplier
    return current_points
