import sys
from typing import List
from typing import Set
from typing import Dict
from typing import Tuple
from copy import deepcopy


class Sudoku(object):
    def __init__(self, sudoku_seed: List[List[Set[str]]] = None, sudoku_seed_text: List[str] = None):
        if sudoku_seed is None:
            # sudoku_seed_text must not be none if sudoku_seed is None
            self.sudoku = Sudoku.parse_sudoku_text(sudoku_seed_text)

    @classmethod
    def find_neighbors(cls, row: int, col: int):
        """Maps a coordinate in a Sudoku grid to that coordinate's neighbors.

        Neighbors are the squares in the grid that are in the same row, same column, or same block as a specified square
        """
        neighbors = set()
        # first set is the same-row neighborhood
        # second set is the same-column neighborhood
        # third set is the same-block neighborhood
        neighborhoods = [set(), set(), set()]
        for i in range(9):
            if i != col:
                # add neighbors in the same row
                neighbors.add((row, i))
                neighborhoods[0].add((row, i))
            if i != row:
                # add neighbors in the same column
                neighbors.add((i, col))
                neighborhoods[1].add((i, col))
        # find the bounds of the 3x3 block neighborhood
        row_low_limit = (row // 3) * 3
        col_low_limit = (col // 3) * 3
        for i in range(row_low_limit, row_low_limit + 3):
            for j in range(col_low_limit, col_low_limit + 3):
                if (i, j) != (row, col):
                    neighborhoods[2].add((i, j))
                    neighbors.add((i, j))
        return neighbors, neighborhoods

    all_row_col_combinations = [(row, col) for row in range(9) for col in range(9)]

    @classmethod
    def generate_possibilities(cls) -> List[List[Set[str]]]:
        all_possibilities = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
        possibilities = [[] for _ in range(9)]
        for row_index in range(9):
            for col_index in range(9):
                possibilities[row_index].append(all_possibilities.copy())
        return possibilities

    @classmethod
    def parse_sudoku_text(cls, sudoku_text: List[str]) -> Dict[Tuple, str]:
        """Parses a textual representation of a sudoku grid into this class's canonical representation"""
        sudoku = {}
        for row_index in range(9):
            row = sudoku_text[row_index].rstrip()
            for col_index in range(9):
                if row[col_index] != "0":
                    sudoku[(row_index, col_index)] = row[col_index]
        return sudoku



    def print_sudoku(self, solution=None):
        if solution is None:
            solution = self.sudoku
        for row in range(9):
            for col in range(9):
                if (row, col) not in solution:
                    print("0", end="")
                else:
                    print(solution[(row, col)], end="")
            print()

    @classmethod
    def is_solved(cls, solution):
        if len(solution) > 81:
            for row in range(9):
                for col in range(9):
                    if (row, col) not in solution:
                        print("0", end="")
                    else:
                        print(solution[(row, col)], end="")

        return len(solution) >= 81

    @classmethod
    def search(cls, possibilities, solution: Dict[Tuple, str]):
        """Enumerate the possibilities of the Sudoku until a successful solution is found"""
        if cls.is_solved(solution):
            return solution

        most_deducted_square = cls.get_square_with_least_possibilities(possibilities, solution)
        # for each possibility for this square
        for possibility in most_deducted_square[2]:
            try:
                # and eliminate the other possibilities
                solution_copy = deepcopy(solution)
                possibilities_copy = deepcopy(possibilities)

                cls.assign(most_deducted_square[0], most_deducted_square[1], possibility, possibilities_copy,
                           solution_copy)

                return cls.search(possibilities_copy, solution_copy)
            except ValueError:
                continue
        raise ValueError

    @classmethod
    def assign(cls, row, col, element, possibilities: List[List[Set[str]]], solution: Dict[Tuple, str]):
        """Assign element to the solution at the specified row and col and eliminate other possibilities."""
        # assign the digit as the solution
        solution[(row, col)] = element
        # eliminate the rest of the digits from possibilities
        digits_to_discard = possibilities[row][col].difference({element})
        for digit in digits_to_discard:
            cls.eliminate(row, col, digit, possibilities, solution)

    def solve(self):
        possibilities = self.generate_possibilities()
        keys = set(self.sudoku.keys())
        for square in keys:
            self.assign(square[0], square[1], self.sudoku[square], possibilities, self.sudoku)

        if not self.is_solved(self.sudoku):
            # get square with least possibilities greater than 1
            self.sudoku = self.search(possibilities, self.sudoku)

    @classmethod
    def get_square_with_least_possibilities(cls, possibilities, solution: Dict[Tuple, str]):
        square_least_possibilities = tuple()
        least_possibilities = 10
        for row in range(9):
            for col in range(9):
                if (row, col) not in solution and len(possibilities[row][col]) < least_possibilities:
                    square_least_possibilities = (row, col, possibilities[row][col].copy())
                    least_possibilities = len(possibilities[row][col])
        return square_least_possibilities

    @classmethod
    def eliminate(cls, row, col, element, possibilities, solution):
        """Eliminate the specified digit from the specified square in the sudoku.

        This method also propagates the effect of eliminating this digit from the possibilities in the square"""
        # element was already discarded from possibilities[row][col
        if element not in possibilities[row][col]:
            return

        possibilities[row][col].discard(element)

        # A contradiction occurred if the last possibility is no longer possible
        if len(possibilities[row][col]) == 0:
            raise ValueError

        neighbors, neighborhoods = Sudoku.neighbors[(row, col)]

        # If this square must contain the leftover digit , eliminate this digit from this square's neighbors
        if len(possibilities[row][col]) == 1:
            for neighbor in neighbors:
                cls.eliminate(neighbor[0], neighbor[1], min(possibilities[row][col]), possibilities, solution)

        # In each of the neighbhorhoods of this square, check if there's a square that must necessarily contain
        # the digit just eliminated from this square.
        for neighborhood in neighborhoods:
            possible_squares_for_element = []
            for neighbor_row, neighbor_col in neighborhood:
                if element in possibilities[neighbor_row][neighbor_col]:
                    possible_squares_for_element.append((neighbor_row, neighbor_col))
            # a contradiction has occurred if no one else in the neighborhood could have this digit
            if len(possible_squares_for_element) == 0:
                raise ValueError
            # if only one other square in the neighborhood can contain the digit, then that square must contain it
            if len(possible_squares_for_element) == 1:
                square_for_element = possible_squares_for_element[0]
                solution[(square_for_element[0], square_for_element[1])] = element
                cls.assign(square_for_element[0], square_for_element[1], element, possibilities, solution)


# define neighbors here because the class Solver can't be resolved if we're still in the middle of defining the class
Sudoku.neighbors = {key: Sudoku.find_neighbors(*key) for key in Sudoku.all_row_col_combinations}


def main():
    with open(sys.argv[1], "r") as sudoku_file:
        sum_of_first_three_digits = 0
        for line in sudoku_file:
            # Store the identifier of this sudoku for output
            sudoku_id = line.rstrip()
            # Parse the next 9 lines as sudoku
            rows = []
            for _ in range(9):
                rows.append(sudoku_file.readline().rstrip())
            print(sudoku_id)
            sudoku_solver = Sudoku(sudoku_seed_text=rows)
            sudoku_solver.print_sudoku()
            print()
            sudoku_solver.solve()
            sudoku_solver.print_sudoku()
            first_three_digits = sudoku_solver.sudoku[(0, 0)] + sudoku_solver.sudoku[(0, 1)] + \
                                  sudoku_solver.sudoku[(0, 2)]
            three_digit_number = int(first_three_digits)
            sum_of_first_three_digits += three_digit_number
            print()

        print(sum_of_first_three_digits)


if __name__ == "__main__":
    main()
