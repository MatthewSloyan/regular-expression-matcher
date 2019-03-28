# Matthew Sloyan G00348036
# https://github.com/MatthewSloyan/Graph-Theory-Project

def infixConversion(infix):
    """Shunting Yard Algorithm implementation for converting infix 
    regular expressions to postfix."""
    
    # declare the special operands and their priority. This will be updated down the line to add +- etc.
    specials = {'*': 50, '+': 50, '?': 50, '.': 40, '|': 30}

    pofix, stack = "", ""

    # interate through each character in the infix string
    for c in infix:
        # If and open bracket, push to the stack.
        if c == '(':
            stack = stack + c
        elif c == ')':
            # if the end of round brackets, add what's on the stack till '(' is encountered
            while stack[-1] != '(':
                pofix, stack = pofix + stack[-1], stack[:-1]
            # remove '(' from stack
            stack = stack[:-1]
        elif c in specials:
            # get(c, 0) = value in dictionary or return 0
            # push to stack if priority is lower or equal priority operators from top of stack into output.
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack + c
        else:
            pofix = pofix + c

    # remove rest of elements from stack and print to postfix
    while stack:
        pofix, stack = pofix + stack[-1], stack[:-1]
        
    return pofix

# Thompson's contruction 
# ======================

# Represents a state with two arrows, labelled by label.
# Use None for a label representing 'e' arrows 
class state: 
    # None = no value as of now but will assign
    label, edge1, edge2 = None, None, None

# An NFA is represented by it's initial and accept states
class nfa:
    initial, accept = None, None

    def __init__(self, initial, accept):
        self.initial = initial
        self.accept = accept

def compile(pofix):
    """Thompson's contruction implementation for converting postfix regular expressions 
    into an equivalent nondeterministic finite automaton (NFA)."""

    #initalise the stack
    nfaStack = []

    # interate through each character in the postfix string
    for c in pofix:
        if c == '.':
            # Pop Nfa's off the stack, nfa1 = first on stack
            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            # Connect first NFA's accept state to the second's initial.
            nfa1.accept.edge1 = nfa2.initial
            # Push NFA to the stack.
            nfaStack.append(nfa(nfa1.initial, nfa2.accept))
        elif c == '|':
            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            # Create a new initial state, connect it to initial states
            # of the two NFA's popped from the stack
            initial, accept = state(), state()
            initial.edge1, initial.edge2 = nfa1.initial, nfa2.initial
            # Create a new accept state, connecting the accept states
            # of the two NFA's popped from the stack, to the new state.
            nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
            # Push new NFA to the stack
            nfaStack.append(nfa(initial, accept))
        elif c == '*':
            # Pop single NFA from the stack
            nfa1 = nfaStack.pop() 
            # Create new intial and accepts states.
            initial, accept = state(), state()
            # Join the new intial state to nfa1's initial state and the new accept state.
            initial.edge1, initial.edge2 = nfa1.initial, accept
            #join the old accept state to the new accept state and nfa1's initial state
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
            #push new NFA to the stack.
            nfaStack.append(nfa(initial, accept))
        elif c == '?':
            # Pop single NFA from the stack which will be the one in "Zero or one"
            nfa1 = nfaStack.pop() 
            # Create new intial and accepts states.
            initial, accept = state(), state()
            # Connect inital state to nfa initial, and connnect other edge to accept state
            initial.edge1, initial.edge2 = nfa1.initial, accept
            # Join nfa accept to accept state to complete
            nfa1.accept.edge1 = accept
            # Push new NFA to the stack.
            nfaStack.append(nfa(initial, accept))
        elif c == '+':
            # Pop single NFA from the stack
            nfa1 = nfaStack.pop() 
            # Create new intial and accepts states.
            initial, accept = state(), state()
            # Connect inital state to nfa initial
            initial.edge1 = nfa1.initial
            # Join one edge back to inital to create a loop, and other to accept
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
            # Push NFA to the stack.
            nfaStack.append(nfa(initial, accept))
        else:
            # Create new initial and accept states.
            initial, accept = state(), state()
            # Joing the initial state, the accept state using an arrow labelled c.
            initial.label, initial.edge1 = c, accept
            # Push new NFA to the stack.
            nfaStack.append(nfa(initial, accept)) # combine states

    # nfaStack should only have a single nfa on it at this point
    return nfaStack.pop()

def followEs(state):
    """# Helper function, which returns set of states that can 
    be reached from the state following e arrows."""
    # Create a new set, with state as it's only member.
    states = set()
    states.add(state)

    # Check if state has arrows labelled e from it. (# If state = None, then e arrow)
    # Keep following e arrows as long as you can.
    if state.label is None:
        # Check if edge1 is a state.
        if state.edge1 is not None:
            # If there's an edge1, follow it and use recursion. | = union
            states |= followEs(state.edge1)
        # Check if edge2 is a state.
        if state.edge2 is not None:
            # If there's an edge2, follow it.
            states |= followEs(state.edge2)
    # Return the set of states.
    return states

def match(infix, string):
    """# Shunt and compile the infix regular expression using both 
    Shunting Yard Algorithm and Thompson's contruction functions."""

    postfix = infixConversion(infix)
    # Creates nfa from postfix
    nfa = compile(postfix)

    # The current set of states and the next set of states. Sets are like lists, 
    # however can only contain unique values
    current, nextState = set(), set()

    # Add the initial state to the current set.
    # When used with sets |= is union
    current |= followEs(nfa.initial)

    # Loop through each character in the postfix string
    for s in string:
        # Loop through current set of states.
        for c in current:
            # Check if that state is labelled s.
            if c.label == s:
                #print(c.label)
                # Add the edge 1 state to the next set.
                nextState |= followEs(c.edge1)
        # Set current to next, and clear out next.
        current, nextState = nextState, set()
    # Check if the accept state is in the set of current states.
    return(nfa.accept in current)

# Print out a list of predefined comparsions to test match function
def printPredefinedResults():
    infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c", "a.b.c?", "a.b.c+"]
    strings = ["", "abc", "abbc", "abcc", "abad", "abbbc", "ab"]

    print("\nRESULTS\n=======")
    for i in infixes:
        print()
        for s in strings:
            print("Infix: %-17s String: %-17s Result: %-5s" % (i, s,  match(i, s)))

# Compare a list of user regular expressions infix notation to strings entered.
# def UserEntries():

userAnswer=True
while userAnswer:
    print("1.Print predefined comparisons\n2.Enter your own infix expressions and strings\n3.Read from file")
    userAnswer=input("Please enter a option?")
    if userAnswer=="1":
        printPredefinedResults()
    elif userAnswer=="2":
        print("\nInput") 
    elif userAnswer=="3":
        print("\nFile") 
    elif userAnswer=="4":
        print("\nGoodbye") 
        userAnswer = None
    else:
        print("\nNot Valid Choice Try again")