"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT

    cnf = CNF()

    # the propositional variable is represented by a three digit number where the first digit is the row number,
    # the second digit is the column number and the third digit is the number in that cell

    # numbers already present in the grid should be there
    # each row must have all the numbers
    # each column must have all the numbers
    for i in range(1,10):
        for n in range(1,10):
            orRowList = []
            orColList = []
            if grid[i-1][n-1] != 0:
                # i represents the row and n represents the column
                cnf.append([100*i + 10*n + grid[i-1][n-1]])
            for j in range(1,10):
                # for orRowList i =row and j =column
                orRowList.append(100*i + 10*j + n)
                # for orColList i =column and j =row
                orColList.append(100*j + 10*i + n)
            cnf.append(orRowList)
            cnf.append(orColList)

    # each 3x3 block must have all the numbers
    for m in range(1,4):
        for n in range(1,10):
            orBlock1List = []
            orBlock2List = []
            orBlock3List = []
            for i in range(1,4): 
                for j in range(1,4):
                    orBlock1List.append(100*(i + (m-1)*3) + 10*j + n)
                    orBlock2List.append(100*(i + (m-1)*3) + 10*(j+3) + n)
                    orBlock3List.append(100*(i + (m-1)*3) + 10*(j+6) + n)
            cnf.append(orBlock1List)
            cnf.append(orBlock2List)
            cnf.append(orBlock3List)

    # a cell is not filled with more than one number
    for i in range(1,10):
        for j in range(1,10):
            for n in range(1,10):
                for k in range(n+1,10):
                    cnf.append([-1*(100*i + 10*j + n), -1*(100*i + 10*j + k)])


    # initialising a nested list for storing the solved sudoku
    solved = [[0 for _ in range(9)] for _ in range(9)]

    # calling the solver
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            # storing the values in solved
            for e in model:
                if e>0:
                    solved[e//100 -1][(e//10)%10 -1] = e%10
        else:
            print("UNSAT")
    
    return solved