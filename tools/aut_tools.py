#!/usr/bin/env python
import re
import sys, getopt


def parse_aut(file_aut,state_variables,action_variables):
    """
    Reads in an aut file and stores the data in a more workable form.
    
    INPUTS
    ------
    file: 
        .aut file
    state_variables: 
        list of which variables are environmental variables
    action_variables: 
        list of which variables are input variables
        
    OUTPUTS
    -------
    state_def: 
        dict of states and true variables
    next_states: 
        dict of states and valid action and what states come next
    rank:
        dict of rank of the states
    """
    state_def = {}
    next_states = {}
    rank = {}
    fid = open(file_aut,'r')
    lines = fid.readlines()

    # Finds out which variables are true in each state and which actions can be taken from each state
    state = 0
    for idx, line in enumerate(lines):
        if (idx%2) == 0:
            state_m = re.findall('State\s(\d+)',line)
            state = state_m[0]
            variables_true = get_true_variables(line,state_variables)
            action_true = get_true_variables(line,action_variables)
            rank[state] = get_rank(line)
            if not action_true:
                action_true = [' ']
            state_def[state] = variables_true
            next_states[state] = action_true
        else:
            successors = get_successors(line)
            next_states[state].append(successors)

    return state_def, next_states, rank


def parse_spec(file_spec):
    """
    Reads in a spec file and extracts the system and environment variables.
    
    INPUTS
    ------
    file_spec: 
        .structuredslugs file
        
    OUTPUTS
    -------
    env_variables: 
        list of environment variables
    sys_variables: 
        list of system variables
    
    """
    sys_variables = []
    env_variables = []
    fid = open(file_spec,'r')
    lines = fid.readlines()

    line_input = lines.index('[INPUT]\n')
    line_output = lines.index('[OUTPUT]\n')
    line_env_init = lines.index('[ENV_INIT]\n')
    
    for idx in range(line_input+1,line_output):
        state = re.findall('(.*)\n',lines[idx])
        if state[0]:
            env_variables.append(state[0])

    for idx in range(line_output+1,line_env_init):
        act = re.findall('(.*)\n',lines[idx])
        if act[0]:
            sys_variables.append(act[0])
    return env_variables,sys_variables
    

def get_state_variables(line):
    """
    Gets the state variables from the first line of the automata.
    
    INPUT
    -----
    line: 
        1st line (or any state def line) of aut file
    
    OUTPUT
    ------
    state_variables: 
        list of state variables
    """
    p = re.compile('<|,\s(.*?):')
    m = p.findall(line)
    if m[0] == '':
        m = m[1:]

    return m


def get_rank(line):
    """
    Gets the rank of the state.
    """
    p = re.compile('rank\s(.*?)\s->')
    m = p.findall(line)
    if m[0][0] == '(':
        m = m[0][1:-1]
    else:
        m = m[0]
    return m


def get_true_variables(line,state_variables):
    """
    Gets the variables that are true.
    """
    states = '|'.join(state_variables)
    pre_p = '(' + states + ')' + ':1'
    p = re.compile(pre_p)
    m = p.findall(line)
    return m


def get_successors(line):
    """
    Gets the successors to a state.
    """
    p = re.compile('\s(\d+)')
    m = p.findall(line)
    return m


def get_repeated_states(state_def):
    """
    Find out which states are repeated and remap the numbering to them.
    """
    same_state = {}
    state_list = state_def.items()
    for ii,(state,variables) in enumerate(state_list):
        for (state_comp,variables_comp) in state_list[(ii+1):]:
            if variables == variables_comp and not state_comp in same_state.keys():
                same_state[state_comp] = state

    return same_state


def write_graphviz(file_gviz,state_def,next_states,rank):
    """
    Writes the automata to a graphviz file.
    """
    # Opens the file, write appropriate heading
    # For each state in the definitions, writes the state to the file
    # Writes the next valid transitions
    # For each of these checks if the state is repeated and changes the number
    # if necessary
    fid = open(file_gviz,'w')
    fid.write('digraph G {\n')
    for state in state_def.keys():
        variables = state_def[state]
        state_write = 'state' + state
        action,next_state_list = next_states[state]
        for next_state in next_state_list:
            next_state_write = 'state' + next_state
            fid.write("\t %s -> %s [label=\"%s\"];\n"%(state_write,next_state_write,action))

    # Writes the next definition of what the states are
    for state in state_def.keys():
        variables = state_def[state]
        state_write = 'state' + str(state)
        variables_write = '\\n'.join(variables)
        variables_write = 'State ' + str(state) + '\\n' + variables_write + '\\n' + 'rank: ' + rank[state]
        fid.write("\t %s [label=\"%s\"];\n"%(state_write,variables_write))

    fid.write('}')
    fid.close()

    # Removes lines that are the same
    fid = open(file_gviz, 'r')
    lines = fid.readlines()
    fid.close()

    lines_seen = set()
    fid = open(file_gviz, 'w')
    for line in lines:
        if line not in lines_seen:
            fid.write(line)
            lines_seen.add(line)
    fid.close()


def main(argv):
    file_aut = ''
    file_spec = ''
    file_gviz = ''
    try:
        opts,args = getopt.getopt(argv,"ha:s:g::", ["autfile=","specfile=","gvizfile="])
    except e:
        print("aut_tools.py -a <autfile> -s <specfile> -g <graphvizfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('aut_tools.py -a <autfile> -s <specfile> -g <graphvizfile>')
            sys.exit()
        elif opt in ("-a", "--autfile"):
            file_aut = arg
        elif opt in ("-s", "--specfile"):
            file_spec = arg
        elif opt in ("-g", "--gvizfile"):
            file_gviz = arg
        
    state_variables,action_variables = parse_spec(file_spec)
    state_def,next_states,rank = parse_aut(file_aut,state_variables,action_variables)
    write_graphviz(file_gviz,state_def,next_states,rank)
#    repeated_states = get_repeated_states(state_def)
    
#    print  "Create graph by running:\ndot -Tpdf %s -o file.pdf"%(file_gviz)
#    print repeated_states
#    print state_def


if __name__ == '__main__':
    main(sys.argv[1:])
