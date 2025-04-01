base_answer_prompt="""
You are a helpful python programmer.
You will write python program to solve math problems.
You must define the function named "solution" in the program and return the result.
You should only write code blocks.
Here are two examples how to do it.
Question:The sphere with radius 1 and center $(0,0,1)$ rests on the $xy$-plane.  A light source is at $P = (0,-1,2).$  Then the boundary of the shadow of the sphere can be expressed in the form $y = f(x),$ for some function $f(x).$  Find the function $f(x).$
```
import sympy as sp
def solution():
    # Define the symbols
    x, y = sp.symbols('x y')

    # Equation for the boundary of the shadow
    lhs = y + 3
    rhs = sp.sqrt(x**2 + (y + 1)**2 + 4)

    # Solve the equation y + 3 = sqrt(x^2 + (y + 1)^2 + 4)
    equation = sp.Eq(lhs, rhs)
    result = sp.solve(equation, y)

    return result
```
Question:The fifth term of a geometric sequence of positive numbers is $11$ and the eleventh term is $5$. What is the eighth term of the sequence? Express your answer in simplest radical form.
```
import math
def solution()
    # Given values
    a_5 = 11  # fifth term
    a_11 = 5  # eleventh term

    # Calculate r^6
    r_squared = a_11 / a_5
    r_squared = r_squared  # r^6 = 5/11

    # r^3 is the square root of r^6
    r_cubed = math.sqrt(r_squared)

    # The eighth term is 11 * r^3
    result = a_5 * r_cubed

    return result

```
How about this Question?
Question:

{Question}
"""


def createCodeAnswerPrompt(question):
    return base_answer_prompt.format(Question=question)


base_reverse_prompt="""" \
"You are a Mathematics Expert in the field of question reconstruction.
You target is to reconstruct the question based on corresponding python program solution.
You should fill the quesion part using following method:
You should mainly follow the relationship between variables and true value of variable symbols to reconstruct the question.
You MUST check the information in the program detailedly and make sure we can solve the question with the program.
You can add side infomation about real situation to make the problem semantically coherent. 
Here are three examples how to do it.
```
def solution():
    money_initial = 23
    bagels = 5
    bagel_cost = 3
    money_spent = bagels * bagel_cost
    money_left = money_initial - money_spent
    result = money_left
    return result
```
Question: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?

```
def solution():
    golf_balls_initial = 58
    golf_balls_lost_tuesday = 23
    golf_balls_lost_wednesday = 2
    golf_balls_left = golf_balls_initial - golf_balls_lost_tuesday - golf_balls_lost_wednesday
    result = golf_balls_left
    return result
```
Question: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?

```
def solution():
    computers_initial = 9
    computers_per_day = 5
    num_days = 4  # 4 days between monday and thursday
    computers_added = computers_per_day * num_days
    computers_total = computers_initial + computers_added
    result = computers_total
    return result
```
Question: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?

How about this python program?

{Code}
"""

def createReversePrompt(code):
    return base_reverse_prompt.format(Code=code)

base_number_complex_prompt="""
"You are a Programming Expert in the field of rewriting python program.
You target is to rewrite one python program to make it evolve into a bit more difficult one for AI systems to handle.
The python program aims to solve one mathematical question, and the variable names indicate their actual meaning.
You should fill the #Rewritten Program# part using following method:
You should rewrite the #Given Program# and evolve it by enhancing its initial numerical values.
The enhanced values should make sure the generated result is difficult to  guess.
You should make sure the enhanced values ​​are consistent with common sense and logically reasonable.
You are NOT allowed to add new variable.
You should only write code blocks.
#Given Program#:

{Code}
#Rewritten Program#:
"""

base_logic_complex_prompt="""
You are a Programming Expert in the field of rewriting python program.
You target is to rewrite one python program to make it evolve into a bit more difficult one for AI systems to handle.
The python program aims to solve one mathematical question, and the variable names indicate their actual meaning.
You should fill the #Rewritten Program# part using following method:
You should rewrite the #Given Program# and evolve it by enhancing the logical judgment conditions in the way of adding constraints.
The added constraints MUST correspond to mathematical conception.
You should make sure the enhanced logical judgment ​​are consistent with common sense and logically reasonable.
Using added constraints to make validations, checks, raising errors is FORBIDDEN in #Rewritten Program#. 
You are allowed to add new variables to make the whole program solution coherent and faithful.
Try your best to make sure the enhanced program aims to solve one definite question.
You should only write code blocks.
#Given Program#:
{Code}
#Rewritten Program#:
"""

base_loop_complex_prompt="""
You are a Programming Expert in the field of rewriting python program.
You target is to rewrite one python program to make it evolve into a bit more difficult one for AI systems to handle.
The python program aims to solve one mathematical question, and the variable names indicate their actual meaning.
You should fill the #Rewritten Program# part using following method:
You should rewrite the #Given Program# and evolve it by  increasing the number of loop layers in the program to add one new dimension.
The increasement of the layer SHOULD ONLY be ONE.
You should make sure the enhanced loops ​​are consistent with common sense and logically reasonable.
The enhanced result MUST correspond to ONE mathematical explainable conception.
Try your best to make sure the enhanced program aims to solve one definite math question.
You should only write code blocks.
#Given Program#:
{Code}
#Rewritten Program#:
"""

base_calculation_complex_prompt="""
You are a Programming Expert in the field of rewriting python program.
You target is to rewrite one python program to make it evolve into a bit more difficult one for AI systems to handle.
The python program aims to solve one mathematical question, and the variable names indicate their actual meaning.
You should fill the #Rewritten Program# part using following method:
You should rewrite the #Given Program# and evolve it by applying a bit more advanced math techniques in the calculation process of the program.
You should make sure the enhanced calculation consistent with common sense and logically reasonable.
MUST Make sure the numerical value of every calculated intermediate variable are STRICTLY follow the type constraint and actual meaning.
You should only write code blocks.
Try your best to make sure we can reconstruct one meaningful question based on the solution of #Rewritten Program#.
#Given Program#:
{Code}
#Rewritten Program#:
"""

base_increase_complex_prompt="""
You are a Programming Expert in the field of rewriting python program.
You target is to rewrite one python program to make it evolve into a bit more difficult one for AI systems to handle.
The python program aims to solve one mathematical question, and the variable names indicate their actual meaning.
You should fill the #Rewritten Program# part using following method:
You should rewrite the #Given Program# and evolve it by continuing writing the program a bit further and regrading the "result" as intermediate variable.
The continuing writing should correspond to ONLY ONE step.
You should make sure the enhanced program and the final return value are consistent with common sense and logically reasonable.
You should only write code blocks.
Try your best to make sure we can reconstruct one meaningful question based on the solution of #Rewritten Program#.
#Given Program#:
{Code}
#Rewritten Program#:
"""

def createComplexPrompt(code, prompt_type):
    if prompt_type == "Number":
        return base_number_complex_prompt.format(Code=code)
    elif prompt_type == "Logic":
        return base_logic_complex_prompt.format(Code=code)
    elif prompt_type == "Loop":
        return base_loop_complex_prompt.format(Code=code)
    elif prompt_type == "Calculation":
        return base_calculation_complex_prompt.format(Code=code)
    elif prompt_type == "Increase":
        return base_increase_complex_prompt.format(Code=code)
    else:
        raise KeyError( "Invalid prompt type.")
    
def createAnswerPrompt(question):
    return base_answer_prompt.format(Question=question)