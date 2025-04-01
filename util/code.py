from transformers.utils.import_utils import _is_package_available
import re
import json
from .util import math_equal,extract_answer
# Use same as transformers.utils.import_utils
_e2b_available = _is_package_available("e2b")

def is_e2b_available() -> bool:
    return _e2b_available


if is_e2b_available():
    from dotenv import load_dotenv
    from e2b_code_interpreter import Sandbox

    load_dotenv()

def extract_code(completion: str) -> str:
    pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
    matches = pattern.findall(completion)
    extracted_answer = matches[-1] if len(matches) >= 1 else ""
    return extracted_answer
def code_check(problem,code_section,solution_section) -> list[float]:
    if not is_e2b_available():
        raise ImportError(
            "E2B is not available and required for this reward function. Please install E2B with "
            "`pip install e2b-code-interpreter` and add an API key to a `.env` file."
        )
    try:
        evaluate_template ='''
        import ast

        def call_first_function_in_code(source_code, *args, **kwargs):
            """
            解析 source_code 中的第一个函数定义，执行后并用传入的参数 *args, **kwargs 调用该函数。
            返回该函数的返回值（若函数没有 return，则返回 None）。
            """
            # 1. 用 ast 解析，找第一个函数名
            tree = ast.parse(source_code)
            fn_name = None
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    fn_name = node.name
                    break
            if not fn_name:
                raise ValueError("在代码中未找到任何函数定义！")

            # 2. 在一个独立的字典上下文中执行代码
            context = {{}}
            exec(source_code, context)

            # 3. 调用解析到的函数，并返回结果
            return context[fn_name](*args, **kwargs)


        # 测试一下
        code = """
        {code}
        """

        value = call_first_function_in_code(code) '''
        code_snippet =extract_code(problem[code_section])

        eval_code = evaluate_template.format(code=code_snippet)
        problem['answer']=extract_answer(problem[solution_section],data_name="math")
        with Sandbox(api_key="e2b_84e2358a5c9c2a0897ade99a93432aee03e4285e",timeout=30, request_timeout=3) as sbx:
            execution = sbx.run_code(eval_code, language="python")
            print(f"Code snippet: {eval_code}")
            print(f"Execution result: {execution}")
            problem['execution_result']=execution.text
            try:
                math_correct=math_equal(execution.text,problem['answer'])
                problem['code_check']=math_correct
            except (TypeError, ValueError):
                problem['code_check']=0
    except Exception as e:
        print(f"Error from E2B executor: {e}")
    problem['code_check']=0
    return problem
