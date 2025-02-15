from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Logic to say that A is either a knight
    # or a knave, not both
    # Equivalent to an XOR
    Biconditional(AKnight, Not(AKnave)),
    # Biconditional helps us handle both cases
    # 1) Case where A is a knight
    # 2) Case where A is a knave
    # Idea is that (P and Q) and (not P and not Q) is equal to P <-> Q
    # THANK YOU TA for the hint!
    Biconditional(AKnight, And(AKnight, AKnave)),
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # XOR, same logic as prior
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    # Biconditional again allows for a more
    # condensed logic instead of two implications
    Biconditional(AKnight, And(AKnave, BKnave)),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # XOR
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    # First Statement
    Biconditional(
        AKnight,
        # Two cases to consider
        # 1) both are knights
        # 2) both are knaves
        # Can be represented as a biconditional
        Biconditional(AKnight, BKnight),
    ),
    # Second Statement
    Biconditional(
        BKnight,
        # Same as XOR
        Not(Biconditional(AKnight, BKnight)),
    ),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # XOR
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(CKnight, Not(CKnave)),
    # First Statement
    # Biconditional again handles both
    # cases where A is knight or knave
    Biconditional(AKnight, Or(AKnight, AKnave)),
    # Second Statement
    # We use nested implications because B says that A says
    Biconditional(BKnight, Implication(AKnight, AKnave)),
    # Third Statement
    Biconditional(BKnight, CKnave),
    # Fourth Statement
    Biconditional(CKnight, AKnight),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3),
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
