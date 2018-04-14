from string import ascii_lowercase
from typing import Set, Any

operators = ['=', '>', '&|^', '~']  # list of lists of operators with the same priority, sorted by priority
variables: str = ascii_lowercase


def check_expression_syntax(expr):
    """
    :param: expr: (str) Expression to be tested
    :return: bool: True if all signs are valid, False otherwise
    """

    operator_list = ''.join(operators)
    for sign in expr:
        if not ((sign in variables + '(01)') or (sign in operator_list)):
            return False
    return True


def get_variables(expr):
    """
    :param: expr: (str) Expression to get variables from
    :return: List: Sorted list of variables from expression without repetitions
    """

    set_of_variables: Set[str] = set()
    for sign in expr:
        if sign in variables:
            set_of_variables.add(sign)
    return sorted(set_of_variables)


def check_expression(expr):
    """
    :param expr: (str) Expression to be tested
    :return: bool: True if expression is valid, False otherwise
    """
    oper = operators[:]
    oper.remove('~')
    operator_list = ''.join(oper)
    variable_list = get_variables(expr)
    if not (check_expression_syntax(expr)):
        return False
    number_of_brackets = 0
    expects_expression = True  # next sign must be a variable or an opening bracket '('
    for sign in expr:
        if sign == '(':
            number_of_brackets += 1
        elif sign == ')':
            number_of_brackets -= 1
        if number_of_brackets < 0:
            return False
        if expects_expression:
            if sign in variable_list + ['0', '1']:
                expects_expression = False
            elif sign in operator_list + ')':
                return False
            elif sign == '~':
                pass
        else:
            if sign in operator_list:
                expects_expression = True
            elif sign in variable_list + ['(', '0', '1', '~']:
                return False
    if number_of_brackets != 0:
        return False
    return not expects_expression


def partition(expr, dividers):
    """
    :param expr: (srt) Expression to be divided
    :param dividers: (str) List of possible chars to divide the expression
    :return: int: Position of the first not nested operator or -1 if expression cannot be divided
    """

    number_of_brackets = 0
    for i in range(len(expr)):
        if expr[i] == '(':
            number_of_brackets += 1
        elif expr[i] == ')':
            number_of_brackets -= 1
        if number_of_brackets == 0 and expr[i] in dividers:
            return i
    return -1


def convert_to_rpn(expr):
    """
    :param expr: (str) Expression in infix notation
    :return: str: Expression in Reverse Polish Notation (postfix)
    """
    while expr[0] == '(' and expr[-1] == ')' and check_expression(expr[1:-1]):
        expr = expr[1:-1]
    for operator_group in operators:
        pos = partition(expr, operator_group)
        if pos > 0:
            return convert_to_rpn(expr[:pos]) + convert_to_rpn(expr[pos + 1:]) + expr[pos]
        elif pos == 0:
            return convert_to_rpn(expr[pos + 1:]) + expr[pos]
    return expr


def variables_to_logic_values(expr, value):
    """
    :param expr: (str) Expression to convert
    :param value: (str) String with only ones and zeros, representing future values of variables
    :return: (str) Expression with specific values inserted
    """

    vars = get_variables(expr)
    tokens = list(expr)
    for sign, iter in zip(expr, range(len(expr))):
        if sign in vars:
            pos = vars.index(sign)
            tokens[iter] = value[pos]
    return ''.join(tokens)


def evaluate(expr, value):
    """
    :param expr: (str) Expression to convert in Reverse Polish Notation (postfix)
    :param value: (str) String with only ones and zeros, representing future values of variables
    :return: (int) 1 if expression is True, 0 otherwise
    """

    expr = variables_to_logic_values(expr, value)
    stack = []
    for sign in expr:
        if sign in '01':
            stack.append(int(sign))
        elif sign == '&':
            val1 = stack.pop()
            val2 = stack.pop()
            stack.append((val1 and val2))
        elif sign == '|':
            val1 = stack.pop()
            val2 = stack.pop()
            stack.append(val1 or val2)
        elif sign == '>':
            val1 = stack.pop()
            val2 = stack.pop()
            stack.append(val1 or 1 - val2)
        elif sign == '^':
            val1 = stack.pop()
            val2 = stack.pop()
            stack.append((val1 and not val2) or (not val1 and val2))
        elif sign == '=':
            val1 = stack.pop()
            val2 = stack.pop()
            stack.append((val1 and val2) or (not val1 and not val2))
        elif sign == '~':
            val1 = stack.pop()
            stack.append(1 - val1)
    return stack.pop()


def generate_values(length):
    """
    :param length: (int) Number of signs in binary representation of generated value 
    :return: (str) String representation of binary value
    """

    for i in range(2 ** length):
        yield bin(i)[2:].rjust(length, '0');


def full_evaluation(expr):
    """
    :param expr: (str) Expression in Reverse Polish Notation
    :return: List[(str, int)]: List of tuples containing states of variables and the evaluated value
    """

    return [(values, evaluate(expr, values)) for values in generate_values(len(get_variables(expr)))]


def is_always_true(values):
    """
    :param values: List[(str, int)]: Result of full_evaluation
    :return: (bool): True if expression is always true, False otherwise
    """

    return all(val == 1 for (_, val) in values)


def is_always_false(values):
    """
    :param values: List[(str, int)]: Result of full_evaluation
    :return: (bool): True if expression is always false, False otherwise
    """

    return all(val == 0 for (_, val) in values)


def merge(val1, val2):
    counter = 0
    result = ""
    for num1, num2 in zip(val1, val2):
        if num1 == num2:
            result += num1
        else:
            counter += 1
            result += '-'
    if counter == 1:
        return result
    return False


def reduce(values):
    result = set()
    merge_flag = False
    for elem1 in values:
        flag = False
        for elem2 in values:
            merged = merge(elem1, elem2)
            if merged:
                result.add(merged)
                flag = merge_flag = True
        if not flag:
            result.add(elem1)
    if merge_flag:
        return reduce(result)
    return result


def delete_unused(val_base, val_reduced):
    best = [bin(2 ** len(val_reduced) - 1)[2:], len(val_reduced)]
    for n in generate_values(len(val_reduced)):
        buf_list = [0 for _ in val_base]
        for red, i in zip(val_reduced, list(n)):
            if i == '1':
                for base, j in zip(val_base, range(len(val_base))):
                    if all(e1 == e2 or e1 == '-' for e1, e2 in zip(red, base)):
                        buf_list[j] = 1
        if best[1] > len([1 for x in n if x == '1']) and all(e == 1 for e in buf_list):
            best[1] = len([1 for x in n if x == '1'])
            best[0] = n
    return [s for s in [r if i == '1' else '' for r, i in zip(list(val_reduced), best[0])] if s != '']


def format_result(s):
    main_result = ""
    for e1 in s:
        result = ""
        for i in range(len(e1)):
            if e1[i] == '-':
                continue
            if e1[i] == '0':
                result += '~'
            result += variables[i] + ' & '
        main_result += "(" + result[:-3] + ") | "
    return main_result[:-3]


def simplify(expr):
    expr = expr.replace(" ", "")
    if not check_expression(expr):
        return "Syntax error"
    values = full_evaluation(convert_to_rpn(expr))
    if is_always_false(values):
        print('False')
        return
    if is_always_true(values):
        print('True')
        return
    true_values = [str for (str, val) in values if val == 1]
    print(format_result(reduce(true_values)))
