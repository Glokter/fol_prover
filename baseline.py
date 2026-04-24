r"""
Baseline prover: a faithful implementation of Algorithm 2 from
Fundamentals of Logic and Computation (Hou, 2021), p. 67.

Naive backward proof search in the sequent calculus LK'. Given a formula A,
tries to derive the sequent (|- A) by applying inference rules backwards.

Rule priority (as specified in Algorithm 2):
  1. Closure:      id, TR, BL
  2. Non-branching: /\L, \/R, ->R, ~L, ~R, !R, ?L
  3. Branching:    /\R, \/L, ->L
  4. Quantifier instantiation with unused term: !L, ?R
  5. Quantifier instantiation with fresh term:  !L, ?R

The algorithm is naive: it does NOT backtrack on rule choice, and it does NOT
backtrack on term selection for quantifier instantiation. Choices are made
greedily and committed to. This is why the algorithm is weak in practice.

Termination: FOL is only semi-decidable for validity, so the prover uses a
rule-application budget to guarantee termination even on non-theorems.
"""

from fol_ast import (
    Var, Const, Func, Atom, Top, Bot,
    Not, And, Or, Implies, Forall, Exists,
    subst,
)


class BudgetExceeded(Exception):
    """Raised when the prover exhausts its rule-application budget."""


# ---------- Sequent helpers ----------

def _dedup_append(seq, *items):
    """Return seq with items appended; drop items already present."""
    out = list(seq)
    for it in items:
        if it not in out:
            out.append(it)
    return tuple(out)


def _replace_at(seq, i, *items):
    """Return seq with seq[i] replaced by items (deduplicated)."""
    out = list(seq[:i]) + list(seq[i + 1:])
    for it in items:
        if it not in out:
            out.append(it)
    return tuple(out)


def _remove_at(seq, i):
    return seq[:i] + seq[i + 1:]


def _collect_ground_terms(formula, acc):
    """Collect constants and function applications. Skips variables."""
    if isinstance(formula, Atom):
        for a in formula.args:
            _collect_ground_terms_in_term(a, acc)
    elif isinstance(formula, (Top, Bot)):
        pass
    elif isinstance(formula, Not):
        _collect_ground_terms(formula.sub, acc)
    elif isinstance(formula, (And, Or, Implies)):
        _collect_ground_terms(formula.left, acc)
        _collect_ground_terms(formula.right, acc)
    elif isinstance(formula, (Forall, Exists)):
        _collect_ground_terms(formula.body, acc)


def _collect_ground_terms_in_term(term, acc):
    if isinstance(term, Const):
        acc.add(term)
    elif isinstance(term, Func):
        acc.add(term)
        for a in term.args:
            _collect_ground_terms_in_term(a, acc)
    # Var: skip


def _terms_in_sequent(gamma, delta):
    acc = set()
    for f in gamma:
        _collect_ground_terms(f, acc)
    for f in delta:
        _collect_ground_terms(f, acc)
    return acc


# ---------- Prover ----------

class NaiveProver:
    def __init__(self, budget=20000, timeout=5.0):
        self.budget = budget
        self.timeout = timeout
        self.applications = 0
        self.fresh_counter = 0
        self._deadline = 0.0

    def _fresh(self):
        self.fresh_counter += 1
        return Const(f"_c{self.fresh_counter}")

    def prove(self, formula):
        """
        Try to prove |- formula. Returns True if proved, False if the
        algorithm terminates without a proof, or None if the budget
        or wall-clock timeout is exceeded.
        """
        import time
        self.applications = 0
        self.fresh_counter = 0
        self._deadline = time.perf_counter() + self.timeout
        try:
            return self._prove((), (formula,), frozenset())
        except (BudgetExceeded, RecursionError):
            return None

    def _prove(self, gamma, delta, used):
        """
        Prove the sequent gamma |- delta.

        `used` is a frozenset of (formula, term) pairs recording which
        terms have already been used to instantiate which !L / ?R formulas.
        """
        self.applications += 1
        if self.applications > self.budget:
            raise BudgetExceeded()
        # Cheap wall-clock check every 256 applications
        if (self.applications & 0xFF) == 0:
            import time
            if time.perf_counter() > self._deadline:
                raise BudgetExceeded()

        # ---- Step 1: closure rules (id, TR, BL) ----
        for f in gamma:
            if isinstance(f, Bot):
                return True                               # BL
            if f in delta:
                return True                               # id
        for f in delta:
            if isinstance(f, Top):
                return True                               # TR

        # ---- Step 2: non-branching rules ----
        for i, f in enumerate(gamma):
            if isinstance(f, And):                        # /\L
                return self._prove(
                    _replace_at(gamma, i, f.left, f.right), delta, used)
            if isinstance(f, Not):                        # ~L
                return self._prove(
                    _remove_at(gamma, i),
                    _dedup_append(delta, f.sub),
                    used)
            if isinstance(f, Exists):                     # ?L (eigenvar)
                c = self._fresh()
                return self._prove(
                    _replace_at(gamma, i, subst(f.body, f.var, c)),
                    delta, used)

        for i, f in enumerate(delta):
            if isinstance(f, Or):                         # \/R
                return self._prove(
                    gamma,
                    _replace_at(delta, i, f.left, f.right),
                    used)
            if isinstance(f, Implies):                    # ->R
                return self._prove(
                    _dedup_append(gamma, f.left),
                    _replace_at(delta, i, f.right),
                    used)
            if isinstance(f, Not):                        # ~R
                return self._prove(
                    _dedup_append(gamma, f.sub),
                    _remove_at(delta, i),
                    used)
            if isinstance(f, Forall):                     # !R (eigenvar)
                c = self._fresh()
                return self._prove(
                    gamma,
                    _replace_at(delta, i, subst(f.body, f.var, c)),
                    used)

        # ---- Step 3: branching rules ----
        for i, f in enumerate(delta):
            if isinstance(f, And):                        # /\R
                return (self._prove(gamma, _replace_at(delta, i, f.left), used)
                        and
                        self._prove(gamma, _replace_at(delta, i, f.right), used))

        for i, f in enumerate(gamma):
            if isinstance(f, Or):                         # \/L
                return (self._prove(_replace_at(gamma, i, f.left), delta, used)
                        and
                        self._prove(_replace_at(gamma, i, f.right), delta, used))
            if isinstance(f, Implies):                    # ->L
                rest = _remove_at(gamma, i)
                left_seq  = (rest, _dedup_append(delta, f.left))
                right_seq = (_dedup_append(rest, f.right), delta)
                return (self._prove(*left_seq, used)
                        and
                        self._prove(*right_seq, used))

        # ---- Step 4: !L / ?R with an unused existing term ----
        terms = _terms_in_sequent(gamma, delta)

        if terms:
            for i, f in enumerate(gamma):
                if isinstance(f, Forall):
                    for t in terms:
                        if (f, t) not in used:
                            inst = subst(f.body, f.var, t)
                            return self._prove(
                                _dedup_append(gamma, inst),
                                delta,
                                used | {(f, t)})
            for i, f in enumerate(delta):
                if isinstance(f, Exists):
                    for t in terms:
                        if (f, t) not in used:
                            inst = subst(f.body, f.var, t)
                            return self._prove(
                                gamma,
                                _dedup_append(delta, inst),
                                used | {(f, t)})

        # ---- Step 5: !L / ?R with a fresh term ----
        for i, f in enumerate(gamma):
            if isinstance(f, Forall):
                c = self._fresh()
                inst = subst(f.body, f.var, c)
                return self._prove(
                    _dedup_append(gamma, inst),
                    delta,
                    used | {(f, c)})
        for i, f in enumerate(delta):
            if isinstance(f, Exists):
                c = self._fresh()
                inst = subst(f.body, f.var, c)
                return self._prove(
                    gamma,
                    _dedup_append(delta, inst),
                    used | {(f, c)})

        # ---- No rule applies: stop ----
        return False
