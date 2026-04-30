%--------------------------------------------------------------------------
% TPTP-style SYN problems
%
% These are classical FOL tautologies drawn from the style of the TPTP
% SYN (syntactic) category. Sources:
%   - G. Sutcliffe. "The TPTP Problem Library and Associated Infrastructure.
%     From CNF and FOF Versions, to TH0, TFF and THF." Journal of
%     Automated Reasoning 43(4):337-362, 2009.
%   - TPTP Problem Library v8.2.0, category SYN.
% URL: https://tptp.org
%
% We use simplified versions that fit our parser's subset (no equality,
% no typed function symbols).
%--------------------------------------------------------------------------

% Quantifier duality
fof(syn_qdual1, conjecture,
    (~ ? [X] : p(X)) <=> (! [X] : ~ p(X))).

fof(syn_qdual2, conjecture,
    (~ ! [X] : p(X)) <=> (? [X] : ~ p(X))).

% Quantifier distribution
fof(syn_qdist_forall_and, conjecture,
    (! [X] : (p(X) & q(X))) <=> ((! [X] : p(X)) & (! [X] : q(X)))).

fof(syn_qdist_exists_or, conjecture,
    (? [X] : (p(X) | q(X))) <=> ((? [X] : p(X)) | (? [X] : q(X)))).

% Swap of adjacent quantifiers (one direction only)
fof(syn_swap_exists_forall, conjecture,
    (? [X] : ! [Y] : p(X, Y)) => (! [Y] : ? [X] : p(X, Y))).

% Prenex: push quantifier out of implication
fof(syn_prenex_impl, conjecture,
    (! [X] : (p(X) => q))
<=> ((? [X] : p(X)) => q)).

% Composition of functions respects universals
fof(syn_comp_univ, conjecture,
    (! [X] : p(f(X))) => p(f(a))).

% Double-quantifier renaming
fof(syn_rename_dbl, conjecture,
    (! [X,Y] : r(X,Y)) <=> (! [Y,X] : r(X,Y))).

% Exchange of universals is fine
fof(syn_exch_univ, conjecture,
    (! [X] : ! [Y] : r(X,Y)) => (! [Y] : ! [X] : r(X,Y))).

% Combination with propositional structure
fof(syn_mixed1, conjecture,
    ((! [X] : (p(X) => q(X))) & (? [X] : p(X))) => (? [X] : q(X))).

fof(syn_mixed2, conjecture,
    ((! [X] : (p(X) => q(X))) & (! [X] : (q(X) => r(X))))
    => (! [X] : (p(X) => r(X)))).

% Nested existentials with a shared argument
fof(syn_shared_exist, conjecture,
    (? [X] : (p(X) & q(X))) => ((? [X] : p(X)) & (? [X] : q(X)))).

% Anti-symmetric: converse of the above does not hold in general
% (this is a NON-theorem, for sanity-checking non-provability).
fof(syn_nonthm, conjecture,
    ((? [X] : p(X)) & (? [X] : q(X))) => (? [X] : (p(X) & q(X)))).

% Barcan-like (this one IS valid in classical FOL with constant domains)
fof(syn_barcan, conjecture,
    (! [X] : (p => q(X))) <=> (p => ! [X] : q(X))).

% A non-trivial prenex equivalence
fof(syn_prenex_mixed, conjecture,
    (! [X] : (p(X) => ? [Y] : q(Y)))
<=> ((? [X] : p(X)) => (? [Y] : q(Y)))).
