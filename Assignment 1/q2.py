"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for i, row in enumerate(self.grid):
            for j, ele in enumerate(row):
                if ele=='G':
                    self.goals.append([i,j])
                elif ele == 'B':
                    self.boxes.append([i,j])
                elif ele == 'P':
                    self.player_start = [i,j]

        pass

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme

        return  10000 + 1000*x + 100*y + t

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme

        return 200000 + 10000*b + 1000*x + 100*y + t



    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions

        # initial position of the player (at t=0)
        self.cnf.append([self.var_player(self.player_start[0], self.player_start[1], 0)])

        # initial positions of the boxes (at t=0)
        for b in range(0,len(self.boxes)):
            self.cnf.append([self.var_box(b, self.boxes[b][0], self.boxes[b][1], 0)])
 
        # The player or the boxes cannot be in two cells at the same time
        for t in range(0, self.T + 1):
            for i in range(0, self.N):
                for j in range(0, self.M):
                    for m in range(0, self.N):
                        for n in range(0, self.M):
                            if not(i==m and j==n):
                                # for player
                                self.cnf.append([-1*self.var_player(i, j, t),-1*self.var_player(m, n, t)])
                                # for box
                                for b in range(0, len(self.boxes)):
                                    self.cnf.append([-1*self.var_box(b, i, j, t),-1*self.var_box(b, m, n, t)])
                    
        # at t=T every box is in a goal (goal condition)
        for b in range(0, len(self.boxes)):
            bg=[]
            for g in self.goals:
                bg.append(self.var_box(b, g[0], g[1], self.T))
            self.cnf.append(bg)

        # no two boxes in the same cell
        for t in range(0,self.T +1):
            for i in range(0,self.N):
                for j in range(0,self.M):
                    for l in range(0, len(self.boxes)):
                        for m in range(l+1, len(self.boxes)):
                            self.cnf.append([-1*self.var_box(l, i, j, t), -1*self.var_box(m, i, j, t)])

        # player and box cannot be in the same cell
        for t in range(0, self.T+1):
            for i in range(0,self.N):
                for j in range(0, self.M):
                    for b in range(0, len(self.boxes)):
                        self.cnf.append([-1*self.var_player(i, j, t), -1*self.var_box(b, i, j, t)])

        # the player or the boxes can not be present inside a cell having walls
        for t in range(0, self.T +1):
            for i in range(0,self.N):
                for j in range(0, self.M):
                    if self.grid[i][j] == '#':
                        self.cnf.append([-1*self.var_player(i, j, t)])
                        for b in range(0, len(self.boxes)):
                            self.cnf.append([-1*self.var_box(b, i, j, t)]) 

        # movement of the player (can only move to adjacent cells or not move at all)
        for t in range(0, self.T):
            for i in range(0,self.N):
                for j in range(0, self.M):
                    mov=[]
                    mov.append(-1*self.var_player(i, j, t))
                    mov.append(self.var_player(i, j, t+1))
                    if i<self.N-1 and self.grid[i+1][j]!='#':
                        mov.append(self.var_player(i+1, j, t+1))
                    if j<self.M-1 and self.grid[i][j+1]!='#':
                        mov.append(self.var_player(i, j+1, t+1))
                    if i>0 and self.grid[i-1][j]!='#':
                        mov.append(self.var_player(i-1, j, t+1))
                    if j>0 and self.grid[i][j-1]!='#':
                        mov.append(self.var_player(i, j-1, t+1))
                    self.cnf.append(mov)

        # boxes cannot be at a position at t+1 if they were not at surrounding positions at t (ensuring the box does not teleport)
        for t in range(0,self.T):
            for b in range(0, len(self.boxes)):
                for i in range(0,self.N):
                    for j in range(0,self.M):
                        if self.grid[i][j]!='#':
                            pb=[]
                            if i > 0 and self.grid[i-1][j] != '#':
                                pb.append(self.var_box(b, i-1, j, t))
                            if i < self.N-1 and self.grid[i+1][j] != '#':
                                pb.append(self.var_box(b, i+1, j, t))
                            if j > 0 and self.grid[i][j-1] != '#':
                                pb.append(self.var_box(b, i, j-1, t))
                            if j < self.M-1 and self.grid[i][j+1] != '#':
                                pb.append(self.var_box(b, i, j+1, t))
                        
                            pb.append(self.var_box(b, i, j, t))
                            pb.append(-1*self.var_box(b, i, j, t+1))
                            self.cnf.append(pb)

        # a box can not be bounded from two sides if they are not opposite (otherwise it cannot be moved)
        for t in range(0, self.T):
            for b in range(0, len(self.boxes)):
                self.cnf.append([-1*self.var_box(b, 0, 0, t)])
                self.cnf.append([-1*self.var_box(b, 0, self.M-1, t)])
                self.cnf.append([-1*self.var_box(b,self.N-1, 0, t)])
                self.cnf.append([-1*self.var_box(b,self.N-1, self.M-1, t)])
                for i in range(0,self.N):
                    for j in range(0, self.M):
                        if i <self.N-1 and j >0:
                            if self.grid[i+1][j] == '#' and self.grid[i][j-1] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])
                        if i <self.N-1 and j <self.M-1:
                            if self.grid[i+1][j] == '#' and self.grid[i][j+1] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])
                        if i >0 and j >0:
                            if self.grid[i-1][j] == '#' and self.grid[i][j-1] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])
                        if i >0 and j <self.M-1:
                            if self.grid[i-1][j] == '#' and self.grid[i][j+1] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])

                        if (i==0 or i==self.N-1) and j>0 and j<self.M-1:
                            if self.grid[i][j-1] == '#' or self.grid[i][j+1] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])
                        if (j==0 or j==self.M-1) and i>0 and i<self.N-1:
                            if self.grid[i-1][j] == '#' or self.grid[i+1][j] == '#':
                                self.cnf.append([-1*self.var_box(b, i, j, t)])

        # if a box moved it was moved by a player
        for t in range(0, self.T):
            for i in range(0,self.N):
                for j in range(0, self.M):
                    for b in range(0, len(self.boxes)):
                        if i<self.N -1 and i>0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i+1, j, t+1), self.var_player(i-1, j, t)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i+1, j, t+1), self.var_player(i, j, t+1)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i-1, j, t+1), self.var_player(i+1, j, t)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i-1, j, t+1), self.var_player(i, j, t+1)])
                        if j<self.M -1 and j>0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j+1, t+1), self.var_player(i, j-1, t)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j+1, t+1), self.var_player(i, j, t+1)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j-1, t+1), self.var_player(i, j+1, t)])
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j-1, t+1), self.var_player(i, j, t+1)])

        # if a box did not move the player was not able to move it
        for t in range(0, self.T):
            for i in range(0,self.N):
                for j in range(0, self.M):
                    for b in range(0, len(self.boxes)):
                        if i > 0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j, t+1), -1*self.var_player(i-1, j, t), -1*self.var_player(i, j, t+1)])
                        if i==0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i+1, j, t+1)])
                        if i < self.N -1:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j, t+1), -1*self.var_player(i+1, j, t), -1*self.var_player(i, j, t+1)])
                        if i==self.N-1:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i-1, j, t+1)])
                        if j > 0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j, t+1), -1*self.var_player(i, j-1, t), -1*self.var_player(i, j, t+1)])
                        if j==0:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j+1, t+1)])
                        if j < self.M -1:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j, t+1), -1*self.var_player(i, j+1, t), -1*self.var_player(i, j, t+1)])
                        if j==self.M-1:
                            self.cnf.append([-1*self.var_box(b, i, j, t), -1*self.var_box(b, i, j-1, t+1)])

        return self.cnf


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    # TODO: Map player positions at each timestep to movement directions

    pos=[0 for _ in range(T+1)]
    dir=[]
    for ele in model:
        if ele<100000 and ele>0:
            x = (ele // 1000) %10
            y = (ele // 100) % 10
            t = ele % 100
            pos[t]=[x,y]
    
    for i in range(0,T):
        tmp = (pos[i+1][0]-pos[i][0],pos[i+1][1]-pos[i][1])
        for key, value in DIRS.items():
            if value == tmp:
                dir.append(key)
    return dir


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)
