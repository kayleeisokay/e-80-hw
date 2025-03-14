import sys

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, words in self.domains.items():
            # Remove words that do not match length
            self.domains[var] = {w for w in words if len(w) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        first_index, second_index = self.crossword.overlaps[x, y]
        # Collect words to remove from a variable
        to_remove = set()

        # Checks if an overlap is possible
        for word_x in self.domains[x]:
            has_match = False
            # Check if neighbor has a existing overlap
            for word_y in self.domains[y]:
                if word_x[first_index] == word_y[second_index]:
                    has_match = True
                    break
            if not has_match:
                to_remove.add(word_x)
                revised = True
        # Remove words that do not have overlap
        self.domains[x] = self.domains[x] - to_remove

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialize arcs

        # If arcs are not passed in
        if arcs is None:
            arcs = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]
        # If arcs are passed in
        else:
            arcs = arcs.copy()

        while arcs:
            # dequeue
            x, y = arcs.pop(0)
            # if Revise(csp, X, Y):
            if self.revise(x, y):
                # if size of X.domain == 0:
                if len(self.domains[x]) == 0:
                    return False
                # for each Z in X.neighbors - {Y}:
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return set(assignment.keys()) == self.crossword.variables

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # all values are distinct
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        # every value is the correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
            # no conflicts between neighboring variables
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Helper function to count number of conflicts
        # Easier to have it here than to break it out to a
        # separate private function
        def count_conflicts(word):
            conflicts = 0

            # Get unassigned neightbors
            assigned = set(assignment.keys())
            neighbors = set(self.crossword.neighbors(var))
            unassigned_neighbors = neighbors - assigned

            # Loop over neighbors and count conflicts
            for neighbor in unassigned_neighbors:
                w_index, n_index = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[w_index] != neighbor_word[n_index]:
                        conflicts += 1
            return conflicts

        # Sort the domain of the variable by conflicts
        return sorted(list(self.domains[var]), key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get unassigned variables
        vars = self.crossword.variables
        assigned = assignment.keys()
        unassigned = list(set(vars) - set(assigned))

        # Sort the unassigned variables by remaining values
        return sorted(unassigned, key=lambda var: len(self.domains[var]))[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Recursion base case
        if self.assignment_complete(assignment):
            return assignment

        # Taken from lecture pseudocode, thank god for the pseudocode
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            # Pass in arcs to inference
            inferences = self.ac3(
                [(neighbor, var) for neighbor in self.crossword.neighbors(var)]
            )
            if self.consistent(new_assignment) and inferences:
                result = self.backtrack(new_assignment)
                if result:
                    return result
                new_assignment.pop(var, None)
        # no assignment is possible
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
