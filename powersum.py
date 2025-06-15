from flask import session
import projects

def process_powersum_log_row(log_row, project_id):

    project = projects.get_project(project_id)
    user_id = session["user_id"]

    if log_row.startswith(project["name"]):
        try:
            content = int(log_row.split()[2])
            projects.mark_task_done(content, user_id, project_id)
            return True
        except Exception as e:
            print(f"Error processing row '{log_row}': {e}")

    elif  difference_between_sides(log_row) == 0:
        projects.add_solution(log_row, user_id, project_id)
    else:
        return False

    return True

def difference_between_sides(row: str):
    try:

        row = row.strip()
        main_part =  row.rsplit("Residue:", 1)[0].strip()
        metadata_part, equation_part = main_part.strip().split(" ", 1)

        exponent = int(metadata_part.strip("()").split(",")[0])

        left_str, right_str = equation_part.split("=")


        left_nums = [int(x) for x in left_str.split("+")]
        right_nums = [int(x) for x in right_str.split("+")]

        left_sum = sum(x ** exponent for x in left_nums)
        right_sum = sum(x ** exponent for x in right_nums)

        return abs(left_sum - right_sum)

    except Exception as e:
        print(f"Error processing row '{row}': {e}")
        return -1