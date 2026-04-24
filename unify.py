"""
Robinson-style syntactic unification over terms augmented with
metavariables (MVar). A substitution is a dict mapping MVar -> Term.

Used by the free-variable sequent prover to determine the correct term
instantiations for forall-left / exists-right rules by unifying candidate
closure atoms instead of guessing terms.
"""

from dataclasses import dataclass
from fol_ast import Var, Const, Func, Atom


@dataclass(frozen=True)
class MVar:
    """Metavariable: a placeholder whose value is determined by unification."""
    name: str

    def __str__(self) -> str:
        return f"?{self.name}"


def walk(t, subst):
    """Follow the substitution chain until reaching a non-resolvable term."""
    while isinstance(t, MVar) and t in subst:
        t = subst[t]
    return t


def apply(t, subst):
    """Apply the substitution eagerly to a term (for display/debugging)."""
    t = walk(t, subst)
    if isinstance(t, Func):
        return Func(t.name, tuple(apply(a, subst) for a in t.args))
    return t


def _occurs(mv, t, subst):
    """Occurs check: does MVar mv appear in term t under subst?"""
    t = walk(t, subst)
    if isinstance(t, MVar):
        return t == mv
    if isinstance(t, Func):
        return any(_occurs(mv, a, subst) for a in t.args)
    return False


def unify(t1, t2, subst):
    """
    Try to unify terms t1 and t2 under the current substitution.
    Returns an extended substitution on success, or None on failure.
    """
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)
    if t1 == t2:
        return subst
    if isinstance(t1, MVar):
        if _occurs(t1, t2, subst):
            return None
        new_subst = dict(subst)
        new_subst[t1] = t2
        return new_subst
    if isinstance(t2, MVar):
        if _occurs(t2, t1, subst):
            return None
        new_subst = dict(subst)
        new_subst[t2] = t1
        return new_subst
    if isinstance(t1, Func) and isinstance(t2, Func):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return None
        s = subst
        for a, b in zip(t1.args, t2.args):
            s = unify(a, b, s)
            if s is None:
                return None
        return s
    # Mismatched kinds (e.g. Const vs Func, different Consts) -> failure
    return None


def unify_atoms(a1, a2, subst):
    """Unify two atomic formulas argument-wise. Same predicate required."""
    if a1.pred != a2.pred or len(a1.args) != len(a2.args):
        return None
    s = subst
    for t1, t2 in zip(a1.args, a2.args):
        s = unify(t1, t2, s)
        if s is None:
            return None
    return s
