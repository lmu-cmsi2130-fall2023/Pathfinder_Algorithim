"""
CMSI 2130 - Homework 1
Author: <Julian Mazzier>

Modify only this file as part of your submission, as it will contain all of the logic
necessary for implementing the A* pathfinder that solves the target practice problem.
"""
from maze_problem import MazeProblem
from dataclasses import *
from typing import *
from queue import PriorityQueue
import math
import queue


@dataclass
class SearchTreeNode:
    player_loc: tuple[int, int]
    action: str
    parent: Optional["SearchTreeNode"]
    cost: int
    targets_shot: set[tuple[int, int]]
    h_cost: int
    targets_left: set[tuple[int, int]]

    def __eq__(self, other: Any) -> bool:
        if other is None: return False
        if not isinstance(other, SearchTreeNode): return False
        return self.player_loc == other.player_loc and self.action == other.action

    def __hash__(self) -> int:
        return hash(self.action)

    def __lt__(self, other: "SearchTreeNode") -> bool: # Evaluates by h(x) + g(x)
        return self.cost + (self.h_cost) < other.cost + (other.h_cost)

def pathfind(problem: "MazeProblem") -> Optional[list[str]]:
    initial_loc: tuple[int, int] = problem.get_initial_loc()
    root_node: "SearchTreeNode" = SearchTreeNode(
        player_loc = initial_loc,
        action = "",
        parent = None,
        cost = 0,
        targets_shot = set(),
        h_cost = 0,
        targets_left = set()
    )

    def heuristic(problem: MazeProblem, node: "SearchTreeNode", targets_left: set[tuple[int, int]]) -> int:
        # Return a heuristic value based on remaining targets, their positions, and the estimated cost to shoot them considering visibility
        total_h_cost: int = 0

        player_loc: tuple[int, int] = node.player_loc

        while targets_left:
            # Find closest target to current location, use lambda instead of a manhattan method
            closest_target = min(targets_left, key=lambda t: abs(t[0] - player_loc[0]) + abs(t[1] - player_loc[1]))

            # Calculate Manhattan distance to closest target
            h_cost = abs(closest_target[0] - player_loc[0]) + abs(closest_target[1] - player_loc[1])
            total_h_cost += h_cost

            player_loc = closest_target # Update the player location
            targets_left.remove(closest_target) # Remove the shot target

        return total_h_cost

    open_set: "queue.PriorityQueue[SearchTreeNode]" = PriorityQueue() # Initalize frontier
    open_set.put(root_node) # Add the root node
    closed_set: set[SearchTreeNode] = set() # Initalize graveyard
    path: list[str] = [] # Path to be returned by pathfind()

    while not open_set.empty(): # Main loop if the open_set isn't empty
        current_node: SearchTreeNode = open_set.get() # Gets lowest value by __lt__
        if(len(problem.get_initial_targets()) - len(current_node.targets_shot)) == 0: # Goal condition
            while current_node.parent is not None:
                path.insert(0, current_node.action) # Insert at index 0
                current_node = current_node.parent # Traces back to path of the solution
            for x in path:
                print(x)
            return path
        if current_node not in closed_set: # If node hasn't been visited, add to graveyard
            closed_set.add(current_node)
            transitions: dict = problem.get_transitions( # Initalize dict with transtitions
                current_node.player_loc,
                problem.get_initial_targets() - current_node.targets_shot
            )

            for action, transition in transitions.items(): # Assign varriables transitions
                next_loc: tuple[int, int] = transition["next_loc"]
                next_cost: int = transition["cost"]
                next_targets_shot: set[tuple[int, int]] = current_node.targets_shot.union(transition["targets_hit"])

                total_cost: int = current_node.cost + next_cost

                child_node: "SearchTreeNode" = SearchTreeNode( # For each action create a child node with transition attributes
                    player_loc = next_loc,
                    action = action,
                    parent = current_node,
                    cost = total_cost,
                    targets_shot = next_targets_shot,
                    h_cost = 0,
                    targets_left = problem.get_initial_targets().difference(next_targets_shot)
                )

                child_node.h_cost = heuristic(problem, child_node, child_node.targets_left) # Call the heuristic method

                if child_node.player_loc not in closed_set:
                    open_set.put(child_node) # If not visited, add to open_set
                    print("Child Node = " + child_node.action)
                    print(" Cost = " + str(child_node.cost) + str(child_node.h_cost))

    return None # If we explore the whole frontier