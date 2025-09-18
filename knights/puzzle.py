from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
A0_stmt = And(AKnight, AKnave)
knowledge0 = And(
    # TODO
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    Implication(AKnight, A0_stmt),
    Implication(AKnave, Not(A0_stmt))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
A1_stmt = And(AKnave, BKnave)
knowledge1 = And(
    # TODO
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    Implication(AKnight, A1_stmt),
    Implication(AKnave, Not(A1_stmt))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
A2_stmt = Biconditional(AKnight, BKnight)
B2_stmt = Not(Biconditional(AKnight, BKnight))
knowledge2 = And(
    # TODO
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    Implication(AKnight, A2_stmt),
    Implication(AKnave, Not(A2_stmt)),
    Implication(BKnight, B2_stmt),
    Implication(BKnave, Not(B2_stmt))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

A_said_knight = Symbol("A said 'I am a Knight'")
A_said_knave = Symbol("A said 'I am a Knave'")

# A dijo exactamente una de las dos
A_said_xor = And(Or(A_said_knight, A_said_knave), Not(And(A_said_knight, A_said_knave)))
# Veracidad de lo que A dijo (depende de cuál dijo)
A_utterance_true = Or(
    And(A_said_knight, AKnight),
    And(A_said_knave, AKnave)
)


knowledge3 = And(
    # TODO
    And(Or(AKnight, AKnave), Not(And(AKnight, AKnave))),
    And(Or(BKnight, BKnave), Not(And(BKnight, BKnave))),
    And(Or(CKnight, CKnave), Not(And(CKnight, CKnave))),

    Implication(AKnight, A_utterance_true),
    Implication(AKnave, Not(A_utterance_true)),

    Implication(BKnight, A_said_knave),
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(A_said_knave)),
    Implication(BKnave, Not(CKnave)),

    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
