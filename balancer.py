import re # To identify elements and their number in the string
import sympy # To solve simultaneous equations
import periodictable # To check if the element is valid
from math import gcd # To convert fraction coefficients to whole numbers

# Function to convert number to subscript
def subscript(string: str):
    # Dictionary of subscripts
    subscripts = {'1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉', '0': '₀'}
    for char in string:
        try:
            # Replacing the number with its subscript
            string = string.replace(char, subscripts[char]) 
        # If the character is letter it returns a KeyError which is handled here
        except KeyError: 
            pass
    return string

def convertWhole(results: list[str]):
    denominators = [] # The list of denominators
    lcm = 1 # lcm is the least common multiple of the denominators
    for r in results:
        if int(r) != r: # When there is a denominator it is not an integer anymore
            # Splitting the / and getting the denominator
            denominators.append(int(str(r).split('/')[1]))
        else:
            # When the coefficient is a whole number then the denominator is 1
            denominators.append(1)

    for d in denominators:
        lcm = lcm*d//gcd(lcm, d) # Change the lcm in order to get rid of denominators
    return [result*lcm for result in results] # Return the results with 

def count_elements(side, compound, bracket_pat, typ, element_pat, equation_elements):
    saved_compound = compound # Save the old compound
    bracket_part = re.findall(bracket_pat, compound) # The part of compound where there is a bracket
    bracket_part_element = None # The element(s) which will be identified in the bracket
    modified = [] # This is the list for all identified elements in the bracket of the compound

    # If there are no brackets bracket_part will be empty so it would not run the for loop
    for i in bracket_part:

        i = list(i) # Convert i to a list since i will be a differnet object_type and it is not subscriptable
        compound = compound.replace(f"({i[0]}){i[1]}", '') # Remove the bracket
        # Use the element pattern to find the elements in the bracket
        bracket_part_element = re.findall(element_pat, i[0]) 

        # Getting the subscript of the bracket
        if not i[1]: i[1] = 1 
        else: i[1] = int(i[1])

        for e in bracket_part_element:
            e = list(e) # Convert e to a list since e will be a differnet object_type and it is not subscriptable
            # Getting the subscript of the element in the bracket 
            if not e[1]: e[1] = 1
            else: e[1] = int(e[1])
            # multiplying the element subscript to bracket subscript because thats how compounds are written in chemistry
            e[1] *= i[1] 
            modified.append(e)
    
    elements = re.findall(element_pat, compound) # get all the element info outside the bracket of the compound
    # Add the bracket element information to elements list
    if bracket_part_element: elements += modified 

    for e in elements:

        e = list(e) # Convert e to a list since e will be a differnet object_type and it is not subscriptable
        if not e[1]: e[1] = 1
        # Store all the element infomation in a dictionary
        dictionary = {
            'number': int(e[1]), 
            'compound': side.index(saved_compound), 
            'type': typ
        }
        # equation_elements has keys as the element_symbol and their value is a list where there will multiple dictionars of occurences of element in the chemical equation
        # However we need define the list before append any new dictionaries so a try and except would solve this problem
        try: equation_elements[e[0]].append(dictionary)
        except KeyError: 
            equation_elements[e[0]] = [dictionary]
    
    return equation_elements
#
def parse(equation: str):

    # Dictionary to store element information of the chemical equation
    equation_elements = {}
    """
    Example of equation_elements dict after processing from the reaction Al + O2 -> Al2O3:
    Compound Number:       0    1       0 (product)
    { 
        'Al': [
            {'number': 1, 'compound': 0, 'type': 'reactant'},
            {'number': 2, 'compound': 0, 'type': 'product'}
        ],
        'O': [
            {'number': 2, 'compound': 1, 'type': 'reactant'}
            {'number': 3, 'compound': 0, 'type': 'product'}
        ]
    }
    """

    equation = equation.replace(' ', '') # Remove spaces
    splitted = re.split(r"(->|=|→)", equation) # Split the equation by eqaual to sign or arrow

    # Store the sides into lhs and rhs
    lhs = splitted[0].split('+')
    rhs = splitted[2].split('+')

    # Generate symbols for reactants and products which are later used to solve the equation
    r = sympy.symbols(f"r:{len(lhs)}")
    p = sympy.symbols(f"p:{len(rhs)}")

    # Regex Patterns to indentify seperate elements and also identify elements which are in brackets
    element_pat = re.compile(r"([A-Z][a-z]?)(\d*)")
    bracket_pat = re.compile(r"\((.*)\)(\d+)")

    # for this code below check count_elements function which is Code snippet #6
    for compound in lhs:
        equation_elements = count_elements(lhs, compound, bracket_pat, 'reactant', element_pat, equation_elements)
    for compound in rhs:
        equation_elements = count_elements(rhs, compound, bracket_pat, 'product', element_pat, equation_elements)

    return equation_elements, r, p, lhs, rhs

def balance(equation: str):

    element_equations = [] # The list to store simulataneous equations of each element
    
    # For this line of code check the code snippet #5
    equation_elements, r, p, reactants, products = parse(equation)
    
    if len(equation_elements) < 2: return "You have only one element in the reaction"
    
    # Looping through all element information of the chemical equation
    for e in equation_elements:

        # If element is not an element in the periodic table the function breaks and returns the following statement:
        if not e in all_elements:
            return "You have entered invalid elements"
        
        # Strings of the two sides of the simulataneous equation created.
        equation_lhs = ""
        equation_rhs = ""

        # Creating simultaneous equation
        for i in equation_elements[e]:
            # r and p are the letters used as variables in simultaneous equation
            # r stands for reactants and p stands for products
            if i['type'] == 'reactant':
                # The number of the compound is attached to the letter variable r
                equation_lhs += f"r[{i['compound']}]*{i['number']}+"
            else:
                # The number of the compound is attached to the letter variable p
                equation_rhs += f"p[{i['compound']}]*{i['number']}+"
        
        # Removing the last character of lhs and rhs which is a '+'
        equation_lhs = equation_lhs[:-1]
        equation_rhs = equation_rhs[:-1]

        # Substitutes the first reactant's coefficient as 1
        equation = sympy.Eq(eval(equation_lhs), eval(equation_rhs)).subs(r[0], 1)
        # Puts all of the equations together into element_equations variable
        element_equations.append(equation)
    
    # Since the first reactant is substituted, we already add 1 to results
    results = [1] 
    d = sympy.solve(element_equations, r[1:] + p) # Solves the equation

    results += d.values()
    results = convertWhole(results)

    # Replacing coefficient 1 as empty string for all compounds
    for result in range(len(results)):
        if results[result] == 1: 
            results[result] = ''
    
    # splitting the lhs and rhs of the results using the length of reactants and products
    lhs_coeffs = results[:len(reactants)]
    rhs_coeffs = results[len(reactants):]

    # Put all of the information together in the balanced_equation string
    balanced_equation = ""
    for rc in range(len(reactants)):
        balanced_equation += f"{lhs_coeffs[rc]}{subscript(reactants[rc])} + "
    balanced_equation = balanced_equation[:-3] + ' -> '
    for pc in range(len(products)):
        balanced_equation += f"{rhs_coeffs[pc]}{subscript(products[pc])} + "
    
    # Revome the last three characters of the balanced equation since the last three would be " + "
    return balanced_equation[:-3]

all_elements = [e.symbol for e in periodictable.elements] 
all_elements.pop(0)

while True:
    inp = input("Enter Chemical Equation: ")
    print("Balanced Equation: " + balance(inp))
    if input("Press s and enter to Stop program").lower() == 's':
        break