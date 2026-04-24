r"""
Improved prover: free-variable sequent calculus with unification and
iterative deepening.

Conceptual changes vs the baseline (Algorithm 2):

  1. Quantifier instantiation (!L, ?R) introduces a METAVARIABLE rather
     than a blindly-chosen concrete term. The correct term is determined
     retroactively when a branch closes via id + unification.

  2. Eigenvariables (introduced by !R / ?L) are SKOLEM TERMS parameterised
     by the metavariables currently in scope. This keeps the free-variable
     tableau sound under Robinson-style unification with occurs check.

  3. Iterative deepening on the total number of !L / ?R applications
     guarantees termination while preserving completeness up to the
     configured maximum depth.

  4. When multiple !L / ?R formulas are available, we instantiate the one
     that has been instantiated fewest times so far, breaking ties by
     position. This keeps the search fair in the presence of several
     quantified hypotheses.

The algorithm is a "liberalised" free-variable tableau: once a branch
closes via a particular unifier, we commit to it. Full backtracking over
closure choices would restore completeness but is out of scope for this
implementation.
"""

import time

from fol_ast import (
    Var, Const, Func, Atom, Top, Bot,
    Not, And, Or, Implies, Forall, Exists,
    subst as apply_subst_formula,
)
from unify import MVar, unify_atoms


class _Deadline(Exception):
    pass


# ---------- Sequent helpers (same shape as baseline) ----------

def _dedup_append(seq, *items):
    out = list(seq)
    for it in items:
        if it not in out:
            out.append(it)
    return tuple(out)


def _replace_at(seq, i, *items):
    out = list(seq[:i]) + list(seq[i + 1:])
    for it in items:
        if it not in out:
            out.append(it)
    return tuple(out)


def _remove_at(seq, i):
    return seq[:i] + seq[i + 1:]


# ---------- Prover ----------

class FVProver:
    def __init__(self, max_qdepth=10, timeout=5.0):
        self.max_qdepth = max_qdepth
        self.timeout = timeout
        self.applications = 0
        self._counter = 0
        self._deadline = 0.0
        self.last_qdepth = 0

    def _fresh_mvar(self):
        self._counter += 1
        return MVar(f"X{self._counter}")

    def _fresh_skolem(self, mvars_in_scope):
        self._counter += 1
        name = f"_sk{self._counter}"
        if not mvars_in_scope:
            return Const(name)
        return Func(name, tuple(mvars_in_scope))

    def prove(self, formula):
        """
        Iterative deepening on !L / ?R depth. Returns:
            True    -- a proof was found
            False   -- all depths up to max_qdepth tried and exhausted
            None    -- wall-clock timeout
        """
        self._deadline = time.perf_counter() + self.timeout
        total_apps = 0
        for qdepth in range(1, self.max_qdepth + 1):
            self.applications = 0
            self._counter = 0
            self.last_qdepth = qdepth
            if time.perf_counter() > self._deadline:
                return None
            try:
                result = self._prove((), (formula,), {}, (), qdepth, {})
                total_apps += self.applications
                if result is not None:
                    self.applications = total_apps
                    return True
            except _Deadline:
                self.applications = total_apps + self.applications
                return None
        self.applications = total_apps
        return False

    def _prove(self, gamma, delta, subst, mvars, qdepth, inst_counts):
        """
        Prove the sequent gamma |- delta under `subst`, with metavariables
        `mvars` currently in scope and `qdepth` remaining !L / ?R applications.

        Returns an extended substitution that closes the subtree, or None.
        """
        self.applications += 1
        if (self.applications & 0xFF) == 0:
            if time.perf_counter() > self._deadline:
                raise _Deadline()

        # ---- Step 1: closure rules ----
        for f in gamma:
            if isinstance(f, Bot):
                return subst                               # BL
        for g in delta:
            if isinstance(g, Top):
                return subst                               # TR
        for f in gamma:                                    # id + unification
            if isinstance(f, Atom):
                for g in delta:
                    if isinstance(g, Atom):
                        mgu = unify_atoms(f, g, subst)
                        if mgu is not None:
                            return mgu

        # ---- Step 2: non-branching rules ----
        for i, f in enumerate(gamma):
            if isinstance(f, And):                         # /\L
                return self._prove(
                    _replace_at(gamma, i, f.left, f.right),
                    delta, subst, mvars, qdepth, inst_counts)
            if isinstance(f, Not):                         # ~L
                return self._prove(
                    _remove_at(gamma, i),
                    _dedup_append(delta, f.sub),
                    subst, mvars, qdepth, inst_counts)
            if isinstance(f, Exists):                      # ?L: Skolem eigenvar
                sk = self._fresh_skolem(mvars)
                return self._prove(
                    _replace_at(gamma, i, apply_subst_formula(f.body, f.var, sk)),
                    delta, subst, mvars, qdepth, inst_counts)

        for i, f in enumerate(delta):
            if isinstance(f, Or):                          # \/R
                return self._prove(
                    gamma,
                    _replace_at(delta, i, f.left, f.right),
                    subst, mvars, qdepth, inst_counts)
            if isinstance(f, Implies):                     # ->R
                return self._prove(
                    _dedup_append(gamma, f.left),
                    _replace_at(delta, i, f.right),
                    subst, mvars, qdepth, inst_counts)
            if isinstance(f, Not):                         # ~R
                return self._prove(
                    _dedup_append(gamma, f.sub),
                    _remove_at(delta, i),
                    subst, mvars, qdepth, inst_counts)
            if isinstance(f, Forall):                      # !R: Skolem eigenvar
                sk = self._fresh_skolem(mvars)
                return self._prove(
                    gamma,
                    _replace_at(delta, i, apply_subst_formula(f.body, f.var, sk)),
                    subst, mvars, qdepth, inst_counts)

        # ---- Step 3: branching rules (substitution threads through) ----
        for i, f in enumerate(delta):
            if isinstance(f, And):                         # /\R
                s1 = self._prove(
                    gamma, _replace_at(delta, i, f.left),
                    subst, mvars, qdepth, inst_counts)
                if s1 is None:
                    return None
                return self._prove(
                    gamma, _replace_at(delta, i, f.right),
                    s1, mvars, qdepth, inst_counts)

        for i, f in enumerate(gamma):
            if isinstance(f, Or):                          # \/L
                s1 = self._prove(
                    _replace_at(gamma, i, f.left), delta,
                    subst, mvars, qdepth, inst_counts)
                if s1 is None:
                    return None
                return self._prove(
                    _replace_at(gamma, i, f.right), delta,
                    s1, mvars, qdepth, inst_counts)
            if isinstance(f, Implies):                     # ->L
                rest = _remove_at(gamma, i)
                s1 = self._prove(
                    rest, _dedup_append(delta, f.left),
                    subst, mvars, qdepth, inst_counts)
                if s1 is None:
                    return None
                return self._prove(
                    _dedup_append(rest, f.right), delta,
                    s1, mvars, qdepth, inst_counts)

        # ---- Step 4: !L / ?R with a fresh metavariable ----
        if qdepth <= 0:
            return None

        # Fairly pick the !L / ?R formula instantiated least so far.
        best = None
        best_count = None
        for i, f in enumerate(gamma):
            if isinstance(f, Forall):
                c = inst_counts.get(id(f), 0)
                if best is None or c < best_count:
                    best = ('L', i, f)
                    best_count = c
        for i, f in enumerate(delta):
            if isinstance(f, Exists):
                c = inst_counts.get(id(f), 0)
                if best is None or c < best_count:
                    best = ('R', i, f)
                    best_count = c

        if best is None:
            return None                                    # stop: no rules apply

        side, _i, f = best
        X = self._fresh_mvar()
        new_mvars = mvars + (X,)
        new_counts = dict(inst_counts)
        new_counts[id(f)] = best_count + 1
        inst = apply_subst_formula(f.body, f.var, X)

        if side == 'L':
            return self._prove(
                _dedup_append(gamma, inst), delta,
                subst, new_mvars, qdepth - 1, new_counts)
        else:
            return self._prove(
                gamma, _dedup_append(delta, inst),
                subst, new_mvars, qdepth - 1, new_counts)
