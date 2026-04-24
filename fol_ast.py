"""
Abstract syntax tree for first-order logic formulas.

Terms:    Var, Const, Func
Formulas: Atom, Not, And, Or, Implies, Forall, Exists, Top, Bot
"""

from dataclasses import dataclass, field
from typing import Tuple


# ---------- Terms ----------

@dataclass(frozen=True)
class Var:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Const:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Func:
    name: str
    args: Tuple["Term", ...]

    def __str__(self) -> str:
        return f"{self.name}({', '.join(str(a) for a in self.args)})"


Term = Var | Const | Func


# ---------- Formulas ----------

@dataclass(frozen=True)
class Atom:
    pred: str
    args: Tuple[Term, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        if not self.args:
            return self.pred
        return f"{self.pred}({', '.join(str(a) for a in self.args)})"


@dataclass(frozen=True)
class Top:
    def __str__(self) -> str:
        return "T"


@dataclass(frozen=True)
class Bot:
    def __str__(self) -> str:
        return "F"


@dataclass(frozen=True)
class Not:
    sub: "Formula"

    def __str__(self) -> str:
        return f"~{self.sub}"


@dataclass(frozen=True)
class And:
    left: "Formula"
    right: "Formula"

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


@dataclass(frozen=True)
class Or:
    left: "Formula"
    right: "Formula"

    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


@dataclass(frozen=True)
class Implies:
    left: "Formula"
    right: "Formula"

    def __str__(self) -> str:
        return f"({self.left} -> {self.right})"


@dataclass(frozen=True)
class Forall:
    var: Var
    body: "Formula"

    def __str__(self) -> str:
        return f"(!{self.var}. {self.body})"


@dataclass(frozen=True)
class Exists:
    var: Var
    body: "Formula"

    def __str__(self) -> str:
        return f"(?{self.var}. {self.body})"


Formula = Atom | Top | Bot | Not | And | Or | Implies | Forall | Exists


# ---------- Substitution ----------

def subst_term(t, x, s):
    """Replace free occurrences of x with s in term t.

    Unknown atomic term types (e.g. metavariables introduced by the
    improved prover) pass through unchanged.
    """
    if isinstance(t, Var):
        return s if t == x else t
    if isinstance(t, Func):
        return Func(t.name, tuple(subst_term(a, x, s) for a in t.args))
    return t  # Const, MVar, or other atomic term


def subst(f: Formula, x: Var, s: Term) -> Formula:
    """Replace free occurrences of x with s in formula f."""
    if isinstance(f, Atom):
        return Atom(f.pred, tuple(subst_term(a, x, s) for a in f.args))
    if isinstance(f, (Top, Bot)):
        return f
    if isinstance(f, Not):
        return Not(subst(f.sub, x, s))
    if isinstance(f, And):
        return And(subst(f.left, x, s), subst(f.right, x, s))
    if isinstance(f, Or):
        return Or(subst(f.left, x, s), subst(f.right, x, s))
    if isinstance(f, Implies):
        return Implies(subst(f.left, x, s), subst(f.right, x, s))
    if isinstance(f, (Forall, Exists)):
        # Don't substitute under a binder for the same variable
        if f.var == x:
            return f
        cls = type(f)
        return cls(f.var, subst(f.body, x, s))
    raise TypeError(f"unknown formula: {f}")
