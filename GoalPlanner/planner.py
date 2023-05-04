from constants import *
from utils import *
import copy
from functools import reduce

from statesactions import *

# Author: Pranav Manjunath
# Collaborators: Srajan Dube
# Collaboration: Srajan and I didn't share code, but we collaborated mostly on a general approach. For example, Srajan mentioned
# some pseudocode for A* in the notes that was helpful. So we just compiled all the information from the notes together and approached
# the problem similarly.

############################
## HELPERS

### Return true if the given state object is a goal. Goal is a State object too.
def is_goal(state, goal):
  return len(goal.propositions.difference(state.propositions)) == 0

### Return true if the given state is in a set of states.
def state_in_set(state, set_of_states):
  for s in set_of_states:
    if s.propositions == state.propositions:
      return True
  return False

### For debugging, print each state in a list of states
def print_states(states):
  for s in states:
    ca = None
    if s.causing_action is not None:
      ca = s.causing_action.name
    print(s.id, s.propositions, ca, s.get_g(), s.get_h(), s.get_f())


############################
### Planner 
###
### The planner knows how to generate a plan using a-star and heuristic search planning.
### It also knows how to execute plans in a continuous, time environment.
class Planner():

  def __init__(self):
    self.running = False              # is the planner running?
    self.world = None                 # pointer back to the world
    self.the_plan = []                # the plan (when generated)
    self.initial_state = None         # Initial state (State object)
    self.goal_state = None            # Goal state (State object)
    self.actions = []                 # list of actions (Action objects)

  ### Start running
  def start(self):
    self.running = True
    
  ### Stop running
  def stop(self):
    self.running = False

  ### Called every tick. Executes the plan if there is one
  def update(self, delta = 0):
    result = False # default return value
    if self.running and len(self.the_plan) > 0:
      # I have a plan, so execute the first action in the plan
      self.the_plan[0].agent = self
      result = self.the_plan[0].execute(delta)
      if result == False:
        # action failed
        print("AGENT FAILED")
        self.the_plan = []
      elif result == True:
        # action succeeded
        done_action = self.the_plan.pop(0)
        print("ACTION", done_action.name, "SUCCEEDED")
        done_action.reset()
    # If the result is None, the action is still executing
    return result

  ### Call back from Action class. Pass through to world
  def check_preconditions(self, preconds):
    if self.world is not None:
      return self.world.check_preconditions(preconds)
    return False

  ### Call back from Action class. Pass through to world
  def get_x_y_for_label(self, label):
    if self.world is not None:
      return self.world.get_x_y_for_label(label)
    return None

  ### Call back from Action class. Pass through to world
  def trigger(self, action):
    if self.world is not None:
      return self.world.trigger(action)
    return False

  ### Generate a plan. Init and goal are State objects. Actions is a list of Action objects
  ### Return the plan and the closed list
  def astar(self, init: State, goal: State, actions: "list[Action]"):
      plan = []    # the final plan
      open = []    # the open list (priority queue) holding State objects
      closed = []  # the closed list (already visited states). Holds state objects
      ### YOUR CODE GOES HERE
      open.append(init)
      cur_state = init
      while not is_goal(cur_state, goal) and len(open) != 0:
        cur_state = min(open, key = State.get_f)
        closed.append(cur_state)
        open.remove(cur_state)
        if is_goal(cur_state, goal):
          break
        for action in actions:
          if action.preconditions.issubset(cur_state.propositions):
            updated_propositions = (cur_state.propositions.difference(action.delete_list)).union(action.add_list)
            successor_state = State(updated_propositions)
            if successor_state in closed:
              break
            successor_state.parent = cur_state
            successor_state.causing_action = action
            successor_state.g = cur_state.g + action.cost
            successor_state.h = self.compute_heuristic(successor_state, goal, actions)
            open.append(successor_state)
      while cur_state.parent is not None:
        plan.insert(0, cur_state.causing_action)
        cur_state = cur_state.parent
      ### CODE ABOVE:
      return plan, closed

  # Helper method for compute_heuristic that constructs the graph
  def build_graph(self, current_state: State, goal_state: State, actions: "list[Action]"):
    dummy_start = Action('dummy_start', preconditions = [], add_list = current_state.propositions, delete_list = [], cost = 0)
    dummy_goal = Action('dummy_goal', preconditions = goal_state.propositions, add_list = [], delete_list = [], cost = 1)
    
    vertices = copy.deepcopy(actions)
    edges = []
    vertices.append(dummy_start)
    vertices.append(dummy_goal)
    
    for vertex in vertices:
      for second_vertex in vertices:
        if vertex != second_vertex:
          for postcondition in vertex.add_list:
            if postcondition in second_vertex.preconditions:
              edges.append((vertex, second_vertex, postcondition))
              
    return dummy_start, dummy_goal, vertices, edges

  ### Compute the heuristic value of the current state using the HSP technique.
  ### Current_state and goal_state are State objects.
  def compute_heuristic(self, current_state: State, goal_state: State, actions: "list[Action]"):
    actions = copy.deepcopy(actions)  # Make a deep copy just in case
    h = 0                             # heuristic value to return
    ### YOUR CODE BELOW
    dummy_start, dummy_goal, vertices, edges = self.build_graph(current_state, goal_state, actions)
    queue = []
    queue.append(dummy_start)
    visited = set()
    dists = {}
    cur_prop = set()
    
    while len(queue) != 0:
      cur_action = queue.pop()
      visited.add(cur_action)
      cur_prop = cur_prop.union(cur_action.add_list)
    
      for edge in edges:
        if edge[0] in visited and edge[1] not in visited:
          dist = 0
          if edge[0].preconditions is not None:
            for precondition in edge[0].preconditions:
              if precondition in dists and dists[precondition] > dist:
                dist = dists[precondition]
          dist = dist + edge[0].cost
          if (edge[2] in dists and dist > dists[edge[2]]) or edge[2] not in dists:
            dists[edge[2]] = dist
          if edge[1].preconditions.issubset(cur_prop):
            queue.append(edge[1])
    for precondition in dummy_goal.preconditions:
      if precondition in dists and dists[precondition] > h:
        h = dists[precondition]
    ### YOUR CODE ABOVE
    return h

