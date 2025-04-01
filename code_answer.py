import os
import time
import json
import re
from datetime import datetime
from functools import partial
from multiprocessing import Pool
import multiprocessing 
from tqdm import tqdm
import math
from prompt.openai_access import batch_get_chat_api, get_oai_completion
import re
from prompt.prompt_design import createComplexPrompt,createAnswerPrompt
from util.code import code_check
from util.util import math_equal,extract_answer
import multiprocessing

def process_code_check(problem, section, response, timeout=10):
    """
    在单独的进程中执行代码检查相关的操作，
    如果超过设定的超时时间（默认为10秒），直接杀死子进程并返回False
    """

    # 这个内部函数里放需要执行的逻辑，比如调用 code_check 及其子函数
    def _worker_func(return_dict, problem, section, response):
        try:
            if problem and problem.get(section) and response:
                # 如果你还需要传 logger 或其它参数，也可一并加入
                result = code_check(problem, section, response)
                return_dict['result'] = result
            else:
                print("Missing data for code check.")
                return_dict['result'] = False
        except Exception as e:
            print(f"Error in code_check: {e}")
            return_dict['result'] = False

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # 创建子进程
    p = multiprocessing.Process(
        target=_worker_func,
        args=(return_dict, problem, section, response)
    )

    try:
        # 启动子进程
        p.start()
        # 设置最大等待时间
        p.join(timeout=timeout)

        # 如果子进程还存活，说明超时
        if p.is_alive():
            print(f"process_code_check exceeded the timeout limit of {timeout} seconds.")
            p.terminate()   # 终止子进程
            p.join()        # 回收子进程
            problem['code_check']=0
            return problem

        # 如果没超时就获取执行结果
        result = return_dict.get('result', False)
        return result

    except Exception as e:
        print(f"Exception in process_code_check: {e}")
        if p.is_alive():
            p.terminate()
            p.join()
        problem['code_check']=0
        return problem

def pre_complex_fun(example):
    return createAnswerPrompt(example['problem'])

def post_fun(example, reply):
    example['code_answer'] = reply

def main(batch_size=1024,
         n_processes=32,
         start_problem_idx=0,
         max_try=3):
    
    print("Starting main processing loop.")
    input_path ="D:\Research\Code-Math-Generator\data\math_output_deepseek.json"
    output_path ="D:\Research\Code-Math-Generator\data\code_output.json"
    correct_output_path="D:\Research\Code-Math-Generator\data\correct_code_output.json"
    model="glm-4-plus"
   
    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)
        problems = problems[start_problem_idx:2]

    total_problems = len(problems)
    total_batch = math.ceil(total_problems / batch_size)
    print(f"Loaded {total_problems} problems.")

    output_list = []
    correct_list= []
    todo_problems = problems

    for ty in range(max_try):
        try_problems = todo_problems
        todo_problems = []
        for batch in range(total_batch):
            print(f"Processing batch {batch + 1}/{total_batch}")
            batch_problems = try_problems[batch * batch_size : (batch + 1) * batch_size]
            print(f"{len(batch_problems)} problems to process in this attempt.")

            if not batch_problems:
                print("No more problems to process in this batch.")
                break
            batch_get_chat_api(
                examples=batch_problems,
                eng=model,
                pre_fun=pre_complex_fun,  # 注意此处依然调用原 pre_complex_fun
                post_fun=post_fun,
                # logger=logger,  # 移除 logger
                n_processes=n_processes,
                temperature=0.5,
                top_p=0.3,
                timeout=20,
                max_try=3,
                think=False
            )
            output_problems = [
                process_code_check(problem,'code_answer','solution') for problem in tqdm(batch_problems)
            ]
            for problem in output_problems:
                if problem['code_check'] == 0:
                    todo_problems.append(problem)
                elif problem['code_check'] == 1:
                    correct_list.append(problem)

            output_list.extend(output_problems)
            with open(output_path, 'w', encoding='utf-8') as output_json:
                json.dump(output_list, output_json, ensure_ascii=False, indent=4)
            
            with open(correct_output_path, 'w', encoding='utf-8') as correct_json:
                json.dump(correct_list, correct_json, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
