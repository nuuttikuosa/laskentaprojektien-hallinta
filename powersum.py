from flask import session, flash
import projects


def process_log_file(log_file, project_id):

    rows = [line for line in log_file.splitlines() if line.strip()]
    if len(rows) == 0:
        flash("Log file is empty.", "error")
        return None
    results = []

    for row in rows:
        is_valid = process_powersum_log_row(row, project_id)
        result = {
            "row": row,
            "status": "OK : " if is_valid else "Validation failed : "
        }
        results.append(result)

    success_count = sum(1 for r in results if "OK" in r["status"])
    fail_count = len(results) - success_count
    flash(
        f"Validation complete: {success_count} passed, {fail_count} failed.", "info")

    return results


def process_powersum_log_row(log_row, project_id):

    project = projects.get_project(project_id)
    user_id = session["user_id"]

    if log_row.startswith(project["name"]):
        try:
            content = int(log_row.split()[2])
            projects.mark_task_done(content, user_id, project_id)
            return True
        except (ValueError, IndexError) as e:
            print(f"Error processing row '{log_row}': {e}")
            return False

    diff = difference_between_sides(log_row)
    if diff == 0:
        projects.add_solution(log_row, user_id, project_id)
        return True

    if diff > 0:
        return False

    print(f"Skipping invalid row: {log_row}")
    return False


def difference_between_sides(row: str):
    try:

        row = row.strip()
        main_part = row.rsplit("Residue:", 1)[0].strip()
        metadata_part, equation_part = main_part.strip().split(" ", 1)

        exponent = int(metadata_part.strip("()").split(",")[0])

        left_str, right_str = equation_part.split("=")

        left_nums = [int(x) for x in left_str.split("+")]
        right_nums = [int(x) for x in right_str.split("+")]

        left_sum = sum(x ** exponent for x in left_nums)
        right_sum = sum(x ** exponent for x in right_nums)

        return abs(left_sum - right_sum)

    except (ValueError, IndexError) as e:
        print(f"Error processing row '{row}': {e}")
        return -1
