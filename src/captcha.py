import hashlib
import time
import json
import base64
from typing import Tuple, Optional


def solve_challenge(data: dict) -> Tuple[Optional[dict], str]:
    """
    Brute-force solve a SHA-256 captcha challenge.
    Returns (solution_dict, base64_encoded_solution) or (None, error_string).
    """
    challenge = data["challenge"]
    salt = data["salt"]
    max_number = data.get("maxnumber", 1000000)

    start_time = time.time()

    for number in range(max_number + 1):
        attempt = f"{salt}{number}"
        result_hash = hashlib.sha256(attempt.encode()).hexdigest()

        if result_hash == challenge:
            took = int((time.time() - start_time) * 1000)

            solution = {
                "algorithm": data["algorithm"],
                "challenge": challenge,
                "number": number,
                "salt": salt,
                "signature": data["signature"],
                "took": took,
            }

            json_str = json.dumps(solution, separators=(",", ":"))
            b64_result = base64.b64encode(json_str.encode()).decode()
            return solution, b64_result

    return None, "No solution found within maxnumber."
