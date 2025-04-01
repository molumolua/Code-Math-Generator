from transformers.utils.import_utils import _is_package_available
import re
import json
from .util import math_equal,extract_answer



def extract_code(completion: str) -> str:
    pattern = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)
    matches = pattern.findall(completion)
    return matches[-1].strip() if matches else ""

def get_code(content) -> str:
    code_snippet =extract_code(content)
    context = {}
    exec(code_snippet, context)
    result = str(context["solution"]())
    return result

def code_check(problem,code_section,solution_section) -> list[float]:
    try:
        problem['answer']=extract_answer(problem[solution_section],data_name="math")
        result = get_code(problem[code_section])
        try:
            problem['code_result']=result
            math_correct=math_equal(problem['code_result'],problem['answer'])
            problem['code_check']=math_correct
        except (TypeError, ValueError):
            problem['code_check']=0
    except Exception as e:
        print(f"Error from code exec: {e}")
        problem['code_check']=0
    return problem

