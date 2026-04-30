%--------------------------------------------------------------------------
% Synthetic stress problems (author-generated)
%
% Parametric "chain" problems of the form:
%   !X. (p(X) -> p(f(X))),  p(a)   |-   p(f^n(a))
%
% The goal is provable by n applications of !L (instantiating X with
% a, f(a), ..., f^(n-1)(a)) followed by n modus ponens steps. Chain depth
% controls the difficulty exponentially for the naive baseline.
%
% Also includes "combine" problems: conjunctions of k independent chain
% problems to test scaling with problem size.
%--------------------------------------------------------------------------

% Chain depth 1..6
fof(chain1, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(a))).

fof(chain2, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(f(a)))).

fof(chain3, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(f(f(a))))).

fof(chain4, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(f(f(f(a)))))).

fof(chain5, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(f(f(f(f(a))))))).

fof(chain6, conjecture,
    ((! [X] : (p(X) => p(f(X)))) & p(a)) => p(f(f(f(f(f(f(a)))))))).

% Quantifier-alternation stress: 2-deep and 3-deep
fof(alt2, conjecture,
    (! [X] : ? [Y] : p(X, Y)) =>
    (! [X] : ? [Y] : (p(X, Y) | p(Y, X)))).

fof(alt3, conjecture,
    (! [X] : ? [Y] : ! [Z] : p(X, Y, Z)) =>
    (! [X] : ? [Y] : ! [Z] : (p(X, Y, Z) | q))).

% Many-universals: multiple universals must each be instantiated
fof(mult_univ, conjecture,
    ((! [X] : p(X)) & (! [X] : q(X)) & (! [X] : r(X)))
    => (p(a) & q(b) & r(c))).

% Existential witness: a concrete witness is available
fof(exist_wit, conjecture,
    (p(a) & q(a)) => ? [X] : (p(X) & q(X))).
