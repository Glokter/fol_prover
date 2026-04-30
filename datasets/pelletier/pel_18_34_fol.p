%--------------------------------------------------------------------------
% Pelletier Problems 18-34 (classical first-order logic, equality-free)
%
% Source: F. J. Pelletier. "Seventy-Five Problems for Testing Automatic
% Theorem Provers." Journal of Automated Reasoning 2 (1986): 191-216.
%--------------------------------------------------------------------------

% Pel 18: "There is something that everyone loves" / drinker-style
fof(pel18, conjecture, ? [Y] : ! [X] : (f(Y) => f(X))).

% Pel 19
fof(pel19, conjecture,
    ? [X] : ! [Y,Z] : ((p(Y) => q(Z)) => (p(X) => q(X)))).

% Pel 20
fof(pel20_ax1, axiom,
    ! [X,Y] : ? [Z] : ! [W] : ((p(X) & q(Y)) => (r(Z) & s(W)))).
fof(pel20_ax2, axiom, ? [X,Y] : (p(X) & q(Y))).
fof(pel20, conjecture, ? [X] : r(X)).

% Pel 21
fof(pel21_ax1, axiom, ? [X] : (p => f(X))).
fof(pel21_ax2, axiom, ? [X] : (f(X) => p)).
fof(pel21, conjecture, ? [X] : (p <=> f(X))).

% Pel 22
fof(pel22_ax, axiom, ! [X] : (p <=> f(X))).
fof(pel22, conjecture, p <=> ! [X] : f(X)).

% Pel 23
fof(pel23, conjecture,
    (! [X] : (p | f(X))) <=> (p | ! [X] : f(X))).

% Pel 24
fof(pel24_ax1, axiom, ~ ? [X] : (s(X) & q(X))).
fof(pel24_ax2, axiom, ! [X] : (p(X) => (q(X) | r(X)))).
fof(pel24_ax3, axiom, (~ ? [X] : p(X)) => ? [Y] : q(Y)).
fof(pel24_ax4, axiom, ! [X] : ((q(X) | r(X)) => s(X))).
fof(pel24, conjecture, ? [X] : (p(X) & r(X))).

% Pel 25
fof(pel25_ax1, axiom, ? [X] : p(X)).
fof(pel25_ax2, axiom, ! [X] : (f(X) => (~ g(X) & r(X)))).
fof(pel25_ax3, axiom, ! [X] : (p(X) => (g(X) & f(X)))).
fof(pel25_ax4, axiom, (! [X] : (p(X) => q(X))) | ? [X] : (p(X) & r(X))).
fof(pel25, conjecture, ? [X] : (q(X) & p(X))).

% Pel 26
fof(pel26_ax1, axiom, (? [X] : p(X)) <=> (? [X] : q(X))).
fof(pel26_ax2, axiom,
    ! [X,Y] : ((p(X) & q(Y)) => (r(X) <=> s(Y)))).
fof(pel26, conjecture,
    (! [X] : (p(X) => r(X))) <=> (! [X] : (q(X) => s(X)))).

% Pel 27
fof(pel27_ax1, axiom, ? [X] : (f(X) & ~ g(X))).
fof(pel27_ax2, axiom, ! [X] : (f(X) => h(X))).
fof(pel27_ax3, axiom, ! [X] : ((j(X) & i(X)) => f(X))).
fof(pel27_ax4, axiom, (? [X] : (h(X) & ~ g(X))) => ! [X] : (i(X) => ~ h(X))).
fof(pel27, conjecture, ! [X] : (j(X) => ~ i(X))).

% Pel 28
fof(pel28_ax1, axiom, ! [X] : (p(X) => ! [X2] : q(X2))).
fof(pel28_ax2, axiom, (! [X] : (q(X) | r(X))) => ? [X] : (q(X) & s(X))).
fof(pel28_ax3, axiom, (? [X] : s(X)) => ! [X] : (f(X) => g(X))).
fof(pel28, conjecture,
    ! [X] : ((p(X) & f(X)) => g(X))).

% Pel 29
fof(pel29_ax, axiom, (? [X] : f(X)) & (? [X] : g(X))).
fof(pel29, conjecture,
    ((! [X] : (f(X) => h(X))) & (! [X] : (g(X) => j(X))))
<=> (! [X,Y] : ((f(X) & g(Y)) => (h(X) & j(Y))))).

% Pel 30
fof(pel30_ax1, axiom,
    ! [X] : ((f(X) | g(X)) => ~ h(X))).
fof(pel30_ax2, axiom,
    ! [X] : ((g(X) => ~ i(X)) => (f(X) & h(X)))).
fof(pel30, conjecture, ! [X] : i(X)).

% Pel 31
fof(pel31_ax1, axiom,
    ~ ? [X] : (f(X) & (g(X) | h(X)))).
fof(pel31_ax2, axiom, ? [X] : (i(X) & f(X))).
fof(pel31_ax3, axiom, ! [X] : (~ h(X) => j(X))).
fof(pel31, conjecture, ? [X] : (i(X) & j(X))).

% Pel 32
fof(pel32_ax1, axiom,
    ! [X] : ((f(X) & (g(X) | h(X))) => i(X))).
fof(pel32_ax2, axiom,
    ! [X] : ((i(X) & h(X)) => j(X))).
fof(pel32_ax3, axiom, ! [X] : (k(X) => h(X))).
fof(pel32, conjecture, ! [X] : ((f(X) & k(X)) => j(X))).

% Pel 33
fof(pel33, conjecture,
    (! [X] : ((p(a) & (p(X) => p(b))) => p(c)))
<=> (! [X] : ((~ p(a) | p(X) | p(c)) & (~ p(a) | ~ p(b) | p(c))))).

% Pel 34 (Andrews' Challenge)
fof(pel34, conjecture,
    ((? [X] : ! [Y] : (p(X) <=> p(Y))) <=> ((? [X] : q(X)) <=> (! [Y] : p(Y))))
<=>
    ((? [X] : ! [Y] : (q(X) <=> q(Y))) <=> ((? [X] : p(X)) <=> (! [Y] : q(Y))))).
