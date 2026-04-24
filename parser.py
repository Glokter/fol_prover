"""
Parser for a subset of TPTP FOF (First-Order Form).

Handles the input format commonly used for Pelletier's problems and the
TPTP SYN category. Supports:

    fof(<name>, <role>, <formula>).

where <formula> is built from:
    atoms            P, P(t1, ..., tn), $true, $false
    negation         ~ F
    connectives      F & G, F | G, F => G, F <=> G
    quantifiers      ! [X, Y, ...] : F     (forall)
                     ? [X, Y, ...] : F     (exists)

Block comments /* ... */ and line comments % ... are ignored.

Returns a list of (name, role, formula) tuples. For proving, we treat
formulas with role 'conjecture' as the goal; 'axiom' formulas are
conjoined as hypotheses.
"""

from lark import Lark, Transformer, v_args
from fol_ast import (
    Var, Const, Func, Atom, Top, Bot,
    Not, And, Or, Implies, Forall, Exists,
)

GRAMMAR = r"""
start: tptp_input+

tptp_input: "fof" "(" NAME "," NAME "," formula ")" "."

?formula: iff_formula

?iff_formula: impl_formula
            | impl_formula "<=>" iff_formula   -> iff

?impl_formula: or_formula
             | or_formula "=>" impl_formula    -> implies

?or_formula: and_formula
           | or_formula "|" and_formula        -> or_

?and_formula: unary_formula
            | and_formula "&" unary_formula    -> and_

?unary_formula: "~" unary_formula              -> not_
              | quant_formula
              | atom
              | "(" formula ")"

quant_formula: QUANT "[" var_list "]" ":" unary_formula

QUANT: "!" | "?"

var_list: VAR ("," VAR)*

?atom: "$true"                                 -> top
     | "$false"                                -> bot
     | PRED "(" term_list ")"                  -> pred_atom
     | PRED                                    -> prop_atom

term_list: term ("," term)*

?term: VAR                                     -> var_term
     | FUNC "(" term_list ")"                  -> func_term
     | FUNC                                    -> const_term

VAR: /[A-Z][A-Za-z0-9_]*/
PRED: /[a-z][A-Za-z0-9_]*/
FUNC: /[a-z][A-Za-z0-9_]*/
NAME: /[A-Za-z0-9_]+/

COMMENT_LINE: /%[^\n]*/
COMMENT_BLOCK: /\/\*(.|\n)*?\*\//

%import common.WS
%ignore WS
%ignore COMMENT_LINE
%ignore COMMENT_BLOCK
"""


@v_args(inline=True)
class _Builder(Transformer):
    # Top-level
    def start(self, *inputs):
        return list(inputs)

    def tptp_input(self, name, role, formula):
        return (str(name), str(role), formula)

    # Formulas
    def iff(self, a, b):
        return And(Implies(a, b), Implies(b, a))

    def implies(self, a, b):
        return Implies(a, b)

    def or_(self, a, b):
        return Or(a, b)

    def and_(self, a, b):
        return And(a, b)

    def not_(self, f):
        return Not(f)

    def quant_formula(self, q, vars_, body):
        cls = Forall if str(q) == "!" else Exists
        result = body
        # Quantifiers nest right-to-left: ![X,Y]: F  ==  !X. !Y. F
        for v in reversed(vars_):
            result = cls(v, result)
        return result

    def var_list(self, *names):
        return [Var(str(n)) for n in names]

    def top(self):
        return Top()

    def bot(self):
        return Bot()

    def pred_atom(self, pred, args):
        return Atom(str(pred), tuple(args))

    def prop_atom(self, pred):
        return Atom(str(pred), ())

    # Terms
    def term_list(self, *ts):
        return list(ts)

    def var_term(self, name):
        return Var(str(name))

    def func_term(self, name, args):
        return Func(str(name), tuple(args))

    def const_term(self, name):
        return Const(str(name))


_parser = Lark(GRAMMAR, parser="lalr", transformer=_Builder())


def parse(text: str):
    """Parse TPTP FOF text. Returns list of (name, role, formula) tuples."""
    return _parser.parse(text)


def load_problem(text: str):
    """
    Load a TPTP problem and reduce it to a single proof obligation.

    Axioms A1, ..., An and conjecture C become the formula
        (A1 & ... & An) -> C
    If there is no conjecture, just conjoin axioms (validity check).
    If there are no axioms, return the conjecture as-is.
    """
    items = parse(text)
    axioms = [f for (_, role, f) in items if role != "conjecture"]
    conjectures = [f for (_, role, f) in items if role == "conjecture"]

    if len(conjectures) > 1:
        raise ValueError("multiple conjectures not supported")

    if axioms and conjectures:
        conj = axioms[0]
        for a in axioms[1:]:
            conj = And(conj, a)
        return Implies(conj, conjectures[0])
    if conjectures:
        return conjectures[0]
    if axioms:
        conj = axioms[0]
        for a in axioms[1:]:
            conj = And(conj, a)
        return conj
    raise ValueError("empty problem")
