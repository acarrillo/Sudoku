from sudoku import Sudoku
import unittest


class TestSudoku(unittest.TestCase):
    def test_solve_with_sum_of_first_three_digits(self):
        """Verifies the correctness of Sudoku.solve() by using Project Euler's method in Problem 96.

        Solves 50 Sudoku grids defined in testcases.txt. For each solution, concatenates the first 3 digits in the first
        row of the grid and adds that 3-digit number to a running sum. Check that the final running sum is correct.
        """
        with open("testcases.txt", "r") as sudoku_file:
            sum_of_first_three_digits = 0
            for _ in sudoku_file:
                # Each Sudoku is preceded by an identifier that we don't need.
                # Parse the next 9 lines as Sudoku
                raw_text = ""
                for _ in range(9):
                    raw_text += (sudoku_file.readline().rstrip())

                sudoku_solver = Sudoku(raw_text=raw_text)

                sudoku_solver.solve()

                first_three_digits = sudoku_solver.sudoku[(0, 0)] + sudoku_solver.sudoku[(0, 1)] + sudoku_solver.sudoku[(0, 2)]
                three_digit_number = int(first_three_digits)
                sum_of_first_three_digits += three_digit_number

            self.assertEqual(24702, sum_of_first_three_digits)
