"""
Dataset loader: reads TPTP .p files and splits them into individual
proof obligations.

A file may contain multiple `fof(..., conjecture, ...)` entries, each
forming its own problem together with any preceding axioms that share
a common name prefix. We use a simple convention:

  fof(pel20_ax1, axiom,  <formula>).
  fof(pel20_ax2, axiom,  <formula>).
  fof(pel20,      conjecture, <formula>).

All axioms whose name starts with "<conjecture_name>_" belong to that
conjecture's problem. Bare conjectures with no axioms are standalone.
"""

from pathlib import Path
from parser import parse, load_problem
from fol_ast import And, Implies


def load_file_problems(path):
    """
    Return a list of (problem_name, goal_formula) for a TPTP file.
    """
    text = Path(path).read_text()
    items = parse(text)

    # Group axioms with each conjecture by name prefix
    conjectures = [(name, f) for (name, role, f) in items if role == "conjecture"]
    axioms = [(name, f) for (name, role, f) in items if role != "conjecture"]

    problems = []
    for cname, cform in conjectures:
        prefix = cname + "_"
        related = [f for (aname, f) in axioms if aname.startswith(prefix)]
        if related:
            conj = related[0]
            for a in related[1:]:
                conj = And(conj, a)
            goal = Implies(conj, cform)
        else:
            goal = cform
        problems.append((cname, goal))
    return problems


def load_all(directory):
    """Load all .p files in a directory, return list of (name, goal)."""
    out = []
    for p in sorted(Path(directory).glob("*.p")):
        out.extend(load_file_problems(p))
    return out
