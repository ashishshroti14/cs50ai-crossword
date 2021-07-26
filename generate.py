import sys

from crossword import *

sys.setrecursionlimit(5000)


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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for variable in self.crossword.variables:
            for word in list(self.domains[variable]):
                if len(word) != variable.length:
                    self.domains[variable].remove(word)
        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x,y]
        if overlap == None:
            return False
        revision_count = 0
        for xword in list(self.domains[x]):
            count = 0
            for yword in self.domains[y]:
                if xword[overlap[0]] == yword[overlap[1]]:
                    count+=1
            if count == 0:
                self.domains[x].remove(xword)
                revision_count+=1
        if revision_count > 0:
            return True
        else:
            return False


        # raise NotImplementedError
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs == None:
            arc_queue = []
            for var1 in self.crossword.variables:
                for var2 in self.crossword.variables:
                    if var1 !=var2:
                        overlap = self.crossword.overlaps[var1, var2]
                        if overlap == None :
                            continue
                        elif (var1, var2) in arc_queue:
                                continue
                        else :
                            arc_queue.append((var1, var2))

        else: 
            arc_queue = arcs

        for arc in arc_queue:


            revised = self.revise(arc[0], arc[1])
            if revised == True:
                if len(self.domains[arc[0]]) == 0:
                    return False
                neighbors = self.crossword.neighbors(arc[0])
                for neighbor in neighbors:
                    arc_queue.append((arc[0], neighbor))
        return True

        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values_set = set(assignment)
        if len(values_set) != len(assignment):
            return False
        for var  in assignment:
            if var.length != len(assignment[var]):
                return False
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                overlap = self.crossword.overlaps(var, neighbor)
                if overlap == None:
                    continue
                elif assignment(var)[overlap[0]] != assignment(neighbor)[overlap[1]]:
                    return False
        return True
            
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        values = []
        counts = {}
        neighbors = self.crossword.neighbors(var)
        for var_word in self.domains[var]:
            count = 0
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap == None:
                    continue
                else: 
                    for neighbor_word in self.domains[neighbor]:
                        if var_word[overlap[0]] != neighbor_word[overlap[1]]:
                            count+=1
            counts[var_word] = count

        sorted_counts  = dict(sorted(counts.items(), key=lambda item: item[1]))

        values = list(sorted_counts)

        return values

        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        var_list = []
        max_neighbor_count = 0
        min_values_remaining = 1000000

        for var in self.crossword.variables:
            if var not in assignment:
                if len(self.domains[var])< min_values_remaining:
                    min_values_remaining = len(self.domains[var]) 
                    var_list = [var]
                elif len(self.domains[var]) == min_values_remaining:
                    var_list.append(var)
        
        if len(var_list) == 1:
            return var_list[0]
        else:
            max_neighbor_var = None
            for var in var_list:
                if len(self.crossword.neighbors(var)) > max_neighbor_count:
                    max_neighbor_count = len(self.crossword.neighbors(var))
                    max_neighbor_var = var
            return max_neighbor_var


        # raise NotImplementedError


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment) == True:

            return assignment

        var = self.select_unassigned_variable(assignment)

        values = self.order_domain_values(var, assignment)

        if len(values) == 0:

            return None
        assignment[var] = values[0]

        return self.backtrack(assignment)


        # raise NotImplementedError


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
