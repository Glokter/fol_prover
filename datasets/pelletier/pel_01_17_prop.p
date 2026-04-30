%--------------------------------------------------------------------------
% Pelletier Problems 1-17 (propositional fragment)
%
% Source: F. J. Pelletier. "Seventy-Five Problems for Testing Automatic
% Theorem Provers." Journal of Automated Reasoning 2 (1986): 191-216.
% Standard TPTP transcriptions of these are freely distributed as part of
% the TPTP Problem Library (SYN001..SYN017).
%--------------------------------------------------------------------------

fof(pel01, conjecture, (p => q) <=> (~q => ~p)).

fof(pel02, conjecture, ~ ~p <=> p).

fof(pel03, conjecture, ~ (p => q) => (q => p)).

fof(pel04, conjecture, (~p => q) <=> (~q => p)).

fof(pel05, conjecture, ((p | q) => (p | r)) => (p | (q => r))).

fof(pel06, conjecture, p | ~p).

fof(pel07, conjecture, p | ~ ~ ~p).

fof(pel08, conjecture, ((p => q) => p) => p).

fof(pel09, conjecture,
    ((p | q) & (~p | q) & (p | ~q)) => ~(~p | ~q)).

fof(pel10_ax1, axiom, q => r).
fof(pel10_ax2, axiom, r => (p & q)).
fof(pel10_ax3, axiom, p => (q | r)).
fof(pel10, conjecture, p <=> q).

fof(pel11, conjecture, p <=> p).

fof(pel12, conjecture,
    ((p <=> q) <=> r) <=> (p <=> (q <=> r))).

fof(pel13, conjecture,
    (p | (q & r)) <=> ((p | q) & (p | r))).

fof(pel14, conjecture,
    (p <=> q) <=> ((q | ~p) & (~q | p))).

fof(pel15, conjecture,
    (p => q) <=> (~p | q)).

fof(pel16, conjecture,
    (p => q) | (q => p)).

fof(pel17, conjecture,
    ((p & (q => r)) => s) <=> ((~p | q | s) & (~p | ~r | s))).
