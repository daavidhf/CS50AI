import itertools
import random


class Minesweeper():
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


class Sentence():
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
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        return set()
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()
        raise NotImplementedError

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


class MinesweeperAI():
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
        self.moves_made.add(cell)
        self.mark_safe(cell)

        i,j = cell
        neighbors = set()
        for r in range(i-1,i+2):        # range (i-1,i+2) genera solo [i-1, i, i+1] -> el ultimo valor de range no se genera en python
            for c in range(j-1,j+2):
                if (r,c) == cell:
                    continue
                if 0<=r<self.height and 0<=c<self.width:
                    neighbors.add((r,c))
        unknown = set()
        adjusted = count
        for n in neighbors:
            if n in self.mines:
                adjusted -= 1
            elif n in self.safes:
                continue
            else:
                unknown.add(n)

        if unknown:
            self.knowledge.append(Sentence(unknown, adjusted))
        
        flag = True
        while flag:
            flag = False

            new_mines = set()
            new_safes = set()
            for s in self.knowledge:
                new_mines |= (s.known_mines()-self.mines)
                new_safes |= (s.known_safes()-self.safes)
            for m in new_mines:
                self.mark_mine(m)
                flag = True
            for s in new_safes:
                self.mark_safe(s)
                flag = True

            # Limpiar oraciones vacías
            new_knowledge = []
            for s in self.knowledge:
                if len(s.cells) > 0:
                    new_knowledge.append(s)
            self.knowledge = new_knowledge
            # Limpiar oraciones duplicadas
            dedup, seen = [], set()
            for s in self.knowledge:
                key = (frozenset(s.cells), s.count)
                if key not in seen:
                    seen.add(key)
                    dedup.append(s)
            if len(dedup) != len(self.knowledge):
                flag = True
            self.knowledge = dedup

            # Inferencia por subconjuntos: si A ⊂ B => (B\A) = count(B)-count(A)
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 is s2 or not s1.cells:
                        continue
                    if s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        if diff_cells and diff_count >= 0:
                            cand = Sentence(diff_cells.copy(), diff_count)
                            key = (frozenset(cand.cells), cand.count)
                            if key not in seen:
                                seen.add(key)
                                new_sentences.append(cand)
            if new_sentences:
                self.knowledge.extend(new_sentences)
                flag = True

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        candidates = self.safes - self.moves_made
        return next(iter(candidates), None)
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set()
        for i in range(self.height):
            for j in range(self.width):
                cell=(i,j)
                all_cells.add(cell)
        candidates =  all_cells - self.mines - self.moves_made
        return next(iter(candidates), None)
        raise NotImplementedError