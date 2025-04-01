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

def pre_complex_fun(example):
    return createAnswerPrompt(example['problem'])

def post_fun(example, reply):
    example['code_answer'] = reply

def main(batch_size=1024,
         n_processes=32,
         start_problem_idx=0):
    
    print("Starting main processing loop.")
    input_path ="D:\Research\Code-Math-Generator\data\math_output_deepseek.json"
    output_path ="D:\Research\Code-Math-Generator\data\code_output.json"
    model="glm-4-plus"
   
    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)
        problems = problems[start_problem_idx:2]

    total_problems = len(problems)
    total_batch = math.ceil(total_problems / batch_size)
    print(f"Loaded {total_problems} problems.")

    output_list = []
    for batch in range(total_batch):
        print(f"Processing batch {batch + 1}/{total_batch}")
        batch_problems = problems[batch * batch_size : (batch + 1) * batch_size]
        try_problems =batch_problems
        print(f"{len(try_problems)} problems to process in this attempt.")

        if not try_problems:
            print("No more problems to process in this batch.")
            break
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
        try_problems = [
             code_check(problem,'code_answer','solution') for problem in tqdm(try_problems)
        ]
        output_list.extend(try_problems)
        with open(output_path, 'w', encoding='utf-8') as output_json:
            json.dump(output_list, output_json, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
