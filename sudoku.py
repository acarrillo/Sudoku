from typing import List
from typing import Set
from typing import Dict
from typing import Tuple
from copy import deepcopy


def find_neighbors(row: int, col: int) -> Tuple[Set, List[Set]]:
    """Maps a coordinate in a Sudoku grid to that coordinate's neighbors and its neighborhoods.

    Neighbors of a square are the squares in the grid that share a neighborhood with the specified square.
    A neighborhood is a set of squares that are in the same row, same column, or same block.
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


# Calculates all the coordinates in a 9 by 9 grid
all_row_col_combinations = [(row, col) for row in range(9) for col in range(9)]


class Sudoku(object):
    """Represents a Sudoku grid.

    After creating an instance of Sudoku, it can be solved by calling solve().
    Get a representation of the Sudoku by using the builtin str().

    A sample use case:
    sudoku = Sudoku(raw_text="...")
    sudoku.solve()
    solution = str(sudoku)
    """

    def __repr__(self):
        """Returns the current state of the Sudoku"""
        grid_digits = []
        for row in range(9):
            for col in range(9):
                if (row, col) not in self.sudoku:
                    grid_digits.append("0")
                else:
                    grid_digits.append(self.sudoku[(row, col)])
        grid_output = "".join(grid_digits)
        sudoku_output = "Sudoku(raw_text=\"{}\")>".format(grid_output)
        return sudoku_output

    def __str__(self):
        """Returns the current state of the Sudoku grid as nine lines of nine digits.

        '0' represents an unsolved square
        """
        grid_digits = []
        for row in range(9):
            for col in range(9):
                if (row, col) not in self.sudoku:
                    grid_digits.append("0")
                else:
                    grid_digits.append(self.sudoku[(row, col)])
            grid_digits.append("\n")
        grid_output = "".join(grid_digits)
        return grid_output

    def __init__(self, raw_text: str):
        """Take in a string of at least 81 non-whitespace characters to parse as a Sudoku"""
        self.initial = Sudoku.clean_raw_text(raw_text)
        self.sudoku = Sudoku.parse_sudoku_text(self.initial)

    @staticmethod
    def clean_raw_text(raw_text: str) -> str:
        """Removes  all whitespace from raw_text and checks to ensure that all characters are digits.

        Raises ValueError if raw_text does not contain only 81 digits and whitespace
        """
        # remove all whitespace
        sudoku_text = "".join(raw_text.split())
        # input should have 81 characters that are only from '0' to '9'
        if not sudoku_text.isdecimal():
            raise ValueError("Non-whitespace characters in input should only be characters from '0' to '9'")
        try:
            sudoku_text.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("Non-whitespace characters in input should only be characters from '0' to '9'")
        if len(sudoku_text) != 81:
            raise ValueError("Input should have 81 non-whitespace characters")
        return sudoku_text

    @staticmethod
    def parse_sudoku_text(sudoku_text: str) -> Dict[Tuple, str]:
        """Parses a textual representation of a Sudoku grid into this class's canonical representation"""
        sudoku = {}
        for row_index in range(9):
            for col_index in range(9):
                current_digit = sudoku_text[row_index * 9 + col_index]
                if current_digit != "0":
                    sudoku[(row_index, col_index)] = current_digit
        return sudoku

    def solve(self):
        """Solve the Sudoku"""
        if Sudoku.is_solved(self.sudoku):
            return
        possibilities = Sudoku.generate_initial_possibilities()
        # More squares will be filled in as we assign each hinted square and deduce the other squares, and
        # more keys will be added to self.sudoku. We can't iterate through an iterable that changes, so copy the keys
        # of the hinted squares and iterate through the copy.
        keys = set(self.sudoku.keys())
        for square in keys:
            # Place the hinted digits in their squares and deduce the digits of the other squares
            Sudoku.assign(square[0], square[1], self.sudoku[square], possibilities, self.sudoku)

        # If the Sudoku can't be solved with pure deduction, guess some digits and see which one works
        if not Sudoku.is_solved(self.sudoku):
            self.sudoku = self.search(possibilities, self.sudoku)

    @staticmethod
    def generate_initial_possibilities() -> List[List[Set[str]]]:
        """Create a 2-dimensional array in which each element is a set of digits from '1' to '9'"""
        all_possibilities = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
        possibilities = [[] for _ in range(9)]
        for row_index in range(9):
            for col_index in range(9):
                possibilities[row_index].append(all_possibilities.copy())
        return possibilities

    @staticmethod
    def assign(row, col, digit_to_assign: str, possibilities: List[List[Set[str]]], solution: Dict[Tuple, str]):
        """Assign element to the solution at the specified row and col and eliminate other possibilities."""
        # assign the digit as the solution
        solution[(row, col)] = digit_to_assign
        # eliminate the rest of the digits from possibilities
        digits_to_discard = possibilities[row][col].difference({digit_to_assign})
        for digit in digits_to_discard:
            Sudoku.eliminate(row, col, digit, possibilities, solution)

    @staticmethod
    def eliminate(row, col, digit: str, possibilities: List[List[Set[str]]], solution: Dict[Tuple, str]):
        """Eliminate the specified digit from the possibilities in the specified square.

        This method also propagates the effect of eliminating this digit from the possibilities in the square
        """
        # element was already discarded from possibilities[row][col
        if digit not in possibilities[row][col]:
            return

        possibilities[row][col].discard(digit)

        # A contradiction occurred if there are no more possibilities for this square
        if len(possibilities[row][col]) == 0:
            raise ValueError("Contradiction at ({}, {}) - no more possibilities".format(row, col))

        neighbors, neighborhoods = Sudoku.neighbors[(row, col)]

        # If this square must contain the leftover digit , eliminate this digit from this square's neighbors
        if len(possibilities[row][col]) == 1:
            for neighbor in neighbors:
                Sudoku.eliminate(neighbor[0], neighbor[1], min(possibilities[row][col]), possibilities, solution)

        # In each of the neighborhoods of this square, check if there's a square that must necessarily contain
        # the digit just eliminated from this square.
        for neighborhood in neighborhoods:
            possible_squares_for_digit = []
            for neighbor_row, neighbor_col in neighborhood:
                if digit in possibilities[neighbor_row][neighbor_col]:
                    possible_squares_for_digit.append((neighbor_row, neighbor_col))
            # a contradiction has occurred if no one else in the neighborhood could have this digit
            if len(possible_squares_for_digit) == 0:
                raise ValueError("Contradiction at ({}, {}) - '{}' cannot be in neighborhood {}".format(row, col, digit,
                                                                                                        neighborhood))
            # if only one other square in the neighborhood can contain the digit, then that square must contain it
            if len(possible_squares_for_digit) == 1:
                square_for_digit = possible_squares_for_digit[0]
                solution[square_for_digit] = digit
                Sudoku.assign(*square_for_digit, digit, possibilities, solution)

    @staticmethod
    def search(possibilities, solution: Dict[Tuple, str]):
        """Enumerate the possibilities of the Sudoku until a successful solution is found"""
        # If the Sudoku is solved, return it
        if Sudoku.is_solved(solution):
            return solution

        most_deducted_square = Sudoku.get_square_with_least_possibilities(possibilities, solution)
        most_deducted_square_possibilities = possibilities[most_deducted_square[0]][most_deducted_square[1]].copy()
        # For each possibility for this square...
        for possibility in most_deducted_square_possibilities:
            try:
                solution_copy = deepcopy(solution)
                possibilities_copy = deepcopy(possibilities)

                # ...assign the possibility and eliminate the other possibilities
                Sudoku.assign(most_deducted_square[0], most_deducted_square[1], possibility, possibilities_copy,
                              solution_copy)
                return Sudoku.search(possibilities_copy, solution_copy)
            except ValueError:
                # If a contradiction has occurred, move on and try the next possibility
                continue
        # This will only get raised if all the possibilities of a square have been tried and all of them have ended in
        # contradictions in the process of solving them
        raise ValueError("Exhausted possibilities at ({}, {})".format(*most_deducted_square))

    @staticmethod
    def get_square_with_least_possibilities(possibilities, solution: Dict[Tuple, str]):
        """Finds the unsolved square with the least remaining possibilities"""
        square_least_possibilities = tuple()
        # An unsolved square will have at most 9 possibilities,
        # so set the initial least_possibilities to be greater than 9
        least_possibilities = 10
        for row in range(9):
            for col in range(9):
                if (row, col) not in solution and len(possibilities[row][col]) < least_possibilities:
                    square_least_possibilities = (row, col)
                    least_possibilities = len(possibilities[row][col])
        return square_least_possibilities

    @staticmethod
    def is_solved(sudoku: Dict[Tuple, str]):
        """Determines if the Sudoku is solved"""
        return len(sudoku) == 81

    # Stores the neighbors and neighborhoods of a given coordinate in a Sudoku grid
    neighbors = {key: find_neighbors(*key) for key in all_row_col_combinations}
