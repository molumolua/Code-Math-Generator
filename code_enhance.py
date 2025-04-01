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
from prompt.prompt_design import createComplexPrompt

def pre_complex_fun(example, prompt_type):
    example['prompt_type'] = prompt_type
    return createComplexPrompt(example['problem'], prompt_type)

def post_fun(example, reply):
    example['reply'] = reply

def calculate(examples):
    ret=[]
    correct_num=0
    for example in examples:
        if(example["eval_score"]=="0"):
            ground_truth= 1-int(example['test_score'])
        else:
            ground_truth =int(example['test_score'])
        test=int(example['new_test']>=(example['test_times']/2))
        if test==ground_truth:
            correct_num+=1
        else:
            ret.append(example)
    print(f"Correct: {correct_num}/{len(examples)}")
    return ret
def pre_process(example):
    example['new_test']=0
    example['test_times']=0
    return example
def main(batch_size=1024,
         max_iteration=5,
         max_try=1,
         n_processes=32,
         start_iteration=0,
         start_problem_idx=0):
    
    # 移除 setup_logger()，并用 print 替换所有 logger.info/debug/error
    
    print("Starting main processing loop.")
    input_path ="D:\Research\Benchmark\\test_evaluate_backup.json"
    output_path ="D:\Research\Benchmark\\new_test_result.json"
    total_path ="D:\Research\Benchmark\\total_test_result.json"
    model="glm-4-plus"
    # 映射function
    number_complex_function=partial(
        createComplexPrompt, prompt_type="Number")
    logic_complex_function=partial(
        createComplexPrompt, prompt_type="Logic")
    loop_complex_function=partial(
        createComplexPrompt, prompt_type="Loop")
    calculation_complex_function=partial(
        createComplexPrompt, prompt_type="Calculation")
    increase_complex_function=partial(
        createComplexPrompt, prompt_type="Increase")
    complex_functions=[
        number_complex_function,logic_complex_function,
        loop_complex_function,calculation_complex_function,increase_complex_function]
    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)
        problems = problems[start_problem_idx:]
        problems = [pre_process(problem) for problem in problems]


    for iteration in range(start_iteration, max_iteration):
        try:
            total_problems = len(problems)
            total_batch = math.ceil(total_problems / batch_size)
            print(f"Loaded {total_problems} problems.")

            output_list = []
            for batch in range(total_batch):
                print(f"Processing batch {batch + 1}/{total_batch}")
                done_keys = []
                batch_problems = problems[batch * batch_size : (batch + 1) * batch_size]

                for attempt in range(max_try):
                    print(f"Attempt {attempt + 1}/{max_try} for batch {batch + 1}")
                    try_problems = [
                        problem for problem in batch_problems
                        if problem['problem'] not in done_keys
                    ]
                    print(f"{len(try_problems)} problems to process in this attempt.")

                    if not try_problems:
                        print("No more problems to process in this batch.")
                        break

                    print(f"Batch {batch + 1}, Attempt {attempt + 1}/{max_try}, Starting complex process.")
                    batch_get_chat_api(
                        examples=try_problems,
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
                    incorrect_problems=calculate(try_problems)
                    with open(output_path, 'w', encoding='utf-8') as output_json:
                        json.dump(incorrect_problems, output_json, ensure_ascii=False, indent=4)
            with open(total_path, 'w', encoding='utf-8') as output_json:
                json.dump(problems, output_json, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error during iteration {iteration + 1}: {e}")

    print("Main processing loop completed.")

if __name__ == "__main__":
    main()
