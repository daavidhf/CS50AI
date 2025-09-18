import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
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
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
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
            to_delete = set()
            for x in words:
                if len(x) != var.length:
                    to_delete.add(x)
            for d in to_delete:
                self.domains[var].remove(d)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps.get((x,y))
        if overlap is None:
            return False
        
        i, j = overlap
        to_remove = set()
        
        for x_var in self.domains[x]:
            supported = False
            for y_var in self.domains[y]:
                if x_var[i] == y_var[j]:
                    supported = True
                    break
            if not supported:
                to_remove.add(x_var)
        
        if to_remove:
            self.domains[x] -= to_remove
            return True
        
        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        if arcs is None:
            queue = []
            for xi in self.crossword.variables:
                for xj in self.crossword.neighbors(xi):
                    if self.crossword.overlaps.get((xi,xj)) is not None:
                        queue.append((xi,xj))
        else:
            queue = list(arcs)

        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi,xj):
                if not self.domains[xi]:
                    return False
                for xk in self.crossword.neighbors(xi)-{xj}:
                    if self.crossword.overlaps.get((xk,xi)) is not None:
                        queue.append((xk,xi))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """        
        for var in self.crossword.variables: 
            if var not in assignment or assignment[var] is None:
                return False
        return True
    
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = list(assignment.values())

        # 1) Palabras distintas, no se repiten
        if len(values) != len(set(values)):
            return False
        
        # 2) Longitud correcta
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
        
        # 3) No hay conflictos entre variables vecinas
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[(var, neighbor)]
                    if overlap is not None:
                        i, j = overlap
                        if assignment[var][i] != assignment[neighbor][j]:
                            return False
        
        return True
              
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        scores = {}
        for candidate in self.domains[var]:
            conflicts = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                overlap = self.crossword.overlaps.get((var,neighbor))
                i,j = overlap
                for neighbor_word in self.domains[neighbor]:
                    if candidate[i] != neighbor_word[j]:
                        conflicts += 1
            scores[candidate] = conflicts
        
        values = list(self.domains[var])
        values.sort(key=lambda word: (scores[word], word))
        return values
    
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_var = None # Variable
        best_mrv = None # Minor remaining value
        best_degree = None # Highest degree

        for var in self.crossword.variables:
            if var in assignment:
                continue

            # tamaño del dominio actual
            mrv = len(self.domains[var])

            # degree: numero de vecinos no asignados
            degree = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    degree += 1
            
            # Si no hay variable elegida todavia
            if best_var is None:
                best_var = var
                best_mrv = mrv
                best_degree = degree
                continue

            # Menor MRV primero
            if mrv < best_mrv:
                best_var = var
                best_mrv = mrv
                best_degree = degree

            elif mrv == best_mrv and degree > best_degree:
                best_var = var
                best_mrv = mrv
                best_degree = degree

        return best_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # ¿Está todo asignado?
        if self.assignment_complete(assignment):
            return assignment
        
        # Elegir variable no asignada por orden (MRV + degree)
        var = self.select_unassigned_variable(assignment)

        # Prueba valores empezando por el menos restrictivo
        for value in self.order_domain_values(var,assignment):

            # Construccion de asignacion tentativa
            tentative = dict(assignment)
            tentative[var] = value

            # Chequeo de consistencia
            if not self.consistent(tentative):
                continue

            # Captura de dominios para poder deshacer
            snapshot = {}
            for v in self.domains.keys():
                snapshot[v] = set(self.domains[v]) # set() sirve para hacer una copia y no compartir el conjunto
            
            # Fijar el dominio de var al valor elegido y correr AC-3
            self.domains[var] = {value}

            # Inicializa arcos para propagar (vecinos -> var)
            arcs =[]
            for n in self.crossword.neighbors(var):
                arcs.append((n,var))
            ok = self.ac3(arcs)

            if ok:
                # Si tras AC-3 ningun dominio esta vacio, avanzar
                result = self.backtrack(tentative)
                if result is not None:
                    return result

            # Deshacer: restaurar dominios y probar otro valor    
            self.domains = snapshot

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
