import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if self.count == len(self.cells) else set()

    # Fix, when conclusion is possible
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def _lowerbound(self, i: int, j: int) -> bool:
        """Helper function to ensure that when
        we search for neighbors, we don't go out of
        bounds in the negative direction.

        Args:
            i (int): row index
            j (int): column index

        Returns:
            bool: True if i and j are positive
        """
        return (i >= 0) and (j >= 0)

    def _upperbound(self, i: int, j: int) -> bool:
        """Helper function to ensure that when
        we search for neighbors, we don't go out of
        bounds in the positive direction.

        Args:
            i (int): row index
            j (int): column index

        Returns:
            bool: True if i and j are less than height
                and width respectively
        """
        return (i < self.height) and (j < self.width)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        self._add_new_sentence(cell, count)

        # Keep running until no possible updates to the kb can be made
        kb_updated = True
        while kb_updated:
            kb_updated = False
            # 4) mark any additional cells as safe or as mines
            # if it can be concluded based on the AI's knowledge base
            kb_updated = self._update_safe_and_mines(kb_updated)
            # 5) add any new sentences to the AI's knowledge base
            # if they can be inferred from existing knowledge
            kb_updated = self._inference(kb_updated)

    def _add_new_sentence(self, cell: tuple, count: int) -> None:
        """
        based on a cell we are constructing new knowledge.
        We build a sentence based on the neighbors of the cell
        """
        neighbors = set()

        # Code is similar to nearby_mines
        # Row index
        for i in range(cell[0] - 1, cell[0] + 2):
            # Col index
            for j in range(cell[1] - 1, cell[1] + 2):
                neighbor_cell = (i, j)
                # ignore the reference cell, safe cells, and moves made
                if (
                    (neighbor_cell == cell)
                    or (neighbor_cell in self.safes)
                    or (neighbor_cell in self.moves_made)
                ):
                    continue

                # if mine, decrement the count
                if neighbor_cell in self.mines:
                    count -= 1
                    continue

                if self._lowerbound(i, j) and self._upperbound(i, j):
                    neighbors.add(neighbor_cell)

        s = Sentence(neighbors, count)
        self.knowledge.append(s)

    def _update_safe_and_mines(self, kb_updated: bool) -> bool:
        """Does step 4. mark any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base.

         Args:
            kb_updated (bool): knowledge update flag

        Returns:
            bool: knowledge update flag
        """
        safe_cells = set()
        mine_cells = set()

        # Accrue all safe and mine cells from the KB
        for sentence in self.knowledge:
            safe_cells = sentence.known_safes().union(safe_cells)
            mine_cells = sentence.known_mines().union(mine_cells)

        # Mark any additional cells as safe or as mines
        if safe_cells:
            kb_updated = True
            for safe_cell in safe_cells:
                self.mark_safe(safe_cell)
        if mine_cells:
            kb_updated = True
            for mine_cell in mine_cells:
                self.mark_mine(mine_cell)

        # Clean up empty sentences
        self.knowledge = [
            sentence for sentence in self.knowledge if len(sentence.cells) > 0
        ]

        return kb_updated

    def _inference(self, kb_updated: bool) -> bool:
        """Implements the algorithm from the HW specs.
        Compare all pairwise sentences. If one is a subset of the other
        then we create a new sentence where the
            new sentence  = set2 - set1
            new_count = count2 - count1

        Args:
            kb_updated (bool): knowledge update flag

        Returns:
            bool: knowledge update flag
        """
        new_sentences = []
        for i in range(len(self.knowledge)):
            for j in range(i + 1, len(self.knowledge)):

                set1 = self.knowledge[i].cells
                set2 = self.knowledge[j].cells

                count1 = self.knowledge[i].count
                count2 = self.knowledge[j].count

                # Deduplicate/strict subset
                if set1 == set2:
                    continue

                # Second condition prevents negative counts
                # I was getting negative counts for some reason
                # Check both directions
                if set1.issubset(set2) and (count2 - count1 >= 0):
                    new_sentence = Sentence(set2 - set1, count2 - count1)

                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)
                elif set2.issubset(set1) and (count1 - count2 >= 0):
                    new_sentence = Sentence(set1 - set2, count1 - count2)

                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)

        # Add new sentences to the knowledge base
        if new_sentences:
            kb_updated = True
            self.knowledge.extend(new_sentences)
        return kb_updated

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.

        For simplicity, we pick a random safe cell.
        """
        safe_choices = self.safes - self.moves_made
        safe_choices = list(safe_choices)

        return random.choice(safe_choices) if safe_choices else None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Using list comprehension as recommended by TA
        # Creates a lit of all cells that are not mines
        # and not explored.
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made.union(self.mines)
        ]

        return random.choice(choices) if choices else None
