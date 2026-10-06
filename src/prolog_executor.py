import os
import shutil
import subprocess
import tempfile


def validate_with_swipl(prolog_text: str) -> dict:
    """
    Validate generated Prolog by checking whether SWI-Prolog can load it.

    This is stronger than surface-level syntax validation because it uses a real
    Prolog interpreter. If SWI-Prolog is not installed, the function reports that
    execution-based validation is unavailable.
    """

    swipl_path = shutil.which("swipl")

    if swipl_path is None:
        return {
            "swipl_available": False,
            "swipl_valid": False,
            "swipl_error": "SWI-Prolog executable 'swipl' was not found.",
        }

    if prolog_text is None or not str(prolog_text).strip():
        return {
            "swipl_available": True,
            "swipl_valid": False,
            "swipl_error": "Empty Prolog output.",
        }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".pl",
        delete=False,
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(str(prolog_text).strip())
        temp_path = temp_file.name

    try:
        result = subprocess.run(
            [swipl_path, "-q", "-t", "halt", "-s", temp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return {
            "swipl_available": True,
            "swipl_valid": result.returncode == 0,
            "swipl_error": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "swipl_available": True,
            "swipl_valid": False,
            "swipl_error": "SWI-Prolog validation timed out.",
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)