from fractions import Fraction
from math import log2
from typing import NamedTuple


class Substrate(NamedTuple):
    name: str
    capacity: Fraction


class TransportSubstrate(NamedTuple):
    colour: str
    states: tuple
    edges: tuple
    admissible: tuple
    burden: tuple
    capacity: Fraction
    source: str
    target: str

X = ("x0", "x1")
D = (("x0", "x1"),)
ADM = (("x0",), ("x1",), ("x0", "x1"))
PHI = (
    (("x0",), Fraction(0)),
    (("x1",), Fraction(0)),
    (("x0", "x1"), Fraction(3, 2)),
)
VISIBLE_SIGNATURE = (X, D, ADM, PHI)
PHI_GAMMA = Fraction(3, 2)

S_MINUS = Substrate("S_minus", Fraction(1))
S_PLUS = Substrate("S_plus", Fraction(2))
OMEGA = (S_MINUS, S_PLUS)
PRIOR = {S_MINUS: Fraction(1, 2), S_PLUS: Fraction(1, 2)}
TARGET = S_PLUS

S_THREE = Substrate("S_three", Fraction(3))
OMEGA_SAME_VERDICT = (S_PLUS, S_THREE)
PRIOR_SAME_VERDICT = {
    S_PLUS: Fraction(1, 2),
    S_THREE: Fraction(1, 2),
}
TARGET_SAME_VERDICT = S_THREE

X_EDGE = ("s", "t")
TRANSPORT_EDGE = (("s", "t"),)
EDGE_TRAJECTORIES = (("s",), ("t",), ("s", "t"))
ADM_EDGE = EDGE_TRAJECTORIES
PHI_EDGE = (
    (("s",), Fraction(0)),
    (("t",), Fraction(0)),
    (("s", "t"), Fraction(0)),
)
CAPACITY_EDGE = Fraction(1)
ADM_EDGE_EXCISED = (("s",), ("t",))
PHI_EDGE_EXCISED = (
    (("s",), Fraction(0)),
    (("t",), Fraction(0)),
)

T_RED = TransportSubstrate(
    "red",
    X_EDGE,
    TRANSPORT_EDGE,
    ADM_EDGE,
    PHI_EDGE,
    CAPACITY_EDGE,
    "s",
    "t",
)
T_BLUE = TransportSubstrate(
    "blue",
    X_EDGE,
    TRANSPORT_EDGE,
    ADM_EDGE,
    PHI_EDGE,
    CAPACITY_EDGE,
    "s",
    "t",
)
OMEGA_EDGE = (T_RED, T_BLUE)
PRIOR_EDGE = {T_RED: Fraction(1, 2), T_BLUE: Fraction(1, 2)}
TARGET_EDGE = T_BLUE


def q_C(substrate):
    return VISIBLE_SIGNATURE


def isomorphic(left, right):
    return q_C(left) == q_C(right) and left.capacity == right.capacity


def budget_positive(substrate):
    return substrate.capacity - PHI_GAMMA > 0


def completed_presentation(substrate):
    return (q_C(substrate), substrate.capacity)


def e_C(substrate):
    return (q_C(substrate), None)


def compatible(presentation, substrate):
    visible, capacity = presentation
    return q_C(substrate) == visible and (
        capacity is None or substrate.capacity == capacity
    )


def P_C(presentation, omega=OMEGA):
    completions = [s for s in omega if compatible(presentation, s)]
    answers = {budget_positive(s) for s in completions}
    return bool(completions) and len(answers) == 1


def q_C_same(substrate):
    return q_C(substrate)


def e_C_same(substrate):
    return e_C(substrate)


def P_C_same(presentation):
    return P_C(presentation, OMEGA_SAME_VERDICT)


def fibre(observation, omega=OMEGA):
    return [s for s in omega if q_C(s) == observation]


def entropy_bits(probabilities):
    return sum(-p * log2(p) for p in probabilities if p > 0)


def q_E(substrate):
    return (
        substrate.colour,
        substrate.states,
        substrate.capacity,
        substrate.source,
        substrate.target,
    )


def completed_E(substrate):
    return substrate


def e_E(substrate):
    return substrate._replace(
        edges=(),
        admissible=ADM_EDGE_EXCISED,
        burden=PHI_EDGE_EXCISED,
    )


def reachable(edges, source, target):
    frontier = [source]
    seen = {source}
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        for left, right in edges:
            if left == current and right not in seen:
                seen.add(right)
                frontier.append(right)
    return False


def P_E(presentation):
    return reachable(
        presentation.edges,
        presentation.source,
        presentation.target,
    )


target_fibre = fibre(q_C(TARGET))
normalizer = sum(PRIOR[s] for s in target_fibre)
posterior = [float(PRIOR[s] / normalizer) for s in target_fibre]
binding = entropy_bits(posterior)
delta_C = 1 - int(P_C(e_C(TARGET)))

same_fibre = [
    s
    for s in OMEGA_SAME_VERDICT
    if q_C_same(s) == q_C_same(TARGET_SAME_VERDICT)
]
same_normalizer = sum(PRIOR_SAME_VERDICT[s] for s in same_fibre)
same_posterior = [
    float(PRIOR_SAME_VERDICT[s] / same_normalizer) for s in same_fibre
]
same_binding = entropy_bits(same_posterior)
delta_same = 1 - int(
    P_C_same(e_C_same(TARGET_SAME_VERDICT))
)

edge_fibre = [
    s for s in OMEGA_EDGE if q_E(s) == q_E(TARGET_EDGE)
]
edge_normalizer = sum(PRIOR_EDGE[s] for s in edge_fibre)
edge_posterior = [
    float(PRIOR_EDGE[s] / edge_normalizer) for s in edge_fibre
]
edge_binding = entropy_bits(edge_posterior)
excised_edge = e_E(TARGET_EDGE)
delta_E = 1 - int(P_E(excised_edge))

assert all(PRIOR[s] > 0 for s in OMEGA)
assert sum(PRIOR.values()) == 1
assert dict(PHI)[("x0",)] <= dict(PHI)[("x0", "x1")]
assert set(target_fibre) == set(OMEGA)
assert not budget_positive(S_MINUS) and budget_positive(S_PLUS)
assert P_C(completed_presentation(TARGET))
assert not P_C(e_C(TARGET))
assert q_C(S_MINUS) == q_C(S_PLUS)
assert not isomorphic(S_MINUS, S_PLUS)
assert delta_C == 1
assert binding == 1.0

assert all(PRIOR_SAME_VERDICT[s] > 0 for s in OMEGA_SAME_VERDICT)
assert sum(PRIOR_SAME_VERDICT.values()) == 1
assert set(same_fibre) == set(OMEGA_SAME_VERDICT)
assert q_C_same(S_PLUS) == q_C_same(S_THREE)
assert all(budget_positive(s) for s in OMEGA_SAME_VERDICT)
assert P_C_same(completed_presentation(TARGET_SAME_VERDICT))
assert P_C_same(e_C_same(TARGET_SAME_VERDICT))
assert not isomorphic(S_PLUS, S_THREE)
assert delta_same == 0
assert same_binding == 1.0

assert all(PRIOR_EDGE[s] > 0 for s in OMEGA_EDGE)
assert sum(PRIOR_EDGE.values()) == 1
assert set(ADM_EDGE) == set(EDGE_TRAJECTORIES)
assert set(dict(PHI_EDGE)) == set(ADM_EDGE)
assert all(value == 0 for value in dict(PHI_EDGE).values())
assert dict(PHI_EDGE)[("s",)] <= dict(PHI_EDGE)[("s", "t")]
assert CAPACITY_EDGE > 0
assert T_RED._replace(colour="blue") == T_BLUE
assert q_E(T_RED)[1:] == q_E(T_BLUE)[1:]
assert len({q_E(s) for s in OMEGA_EDGE}) == len(OMEGA_EDGE)
assert edge_fibre == [TARGET_EDGE]
assert completed_E(TARGET_EDGE) == TARGET_EDGE
assert P_E(completed_E(TARGET_EDGE))
assert excised_edge.states == X_EDGE
assert excised_edge.edges == ()
assert excised_edge.admissible == ADM_EDGE_EXCISED
assert excised_edge.burden == PHI_EDGE_EXCISED
assert set(dict(excised_edge.burden)) == set(excised_edge.admissible)
assert excised_edge.capacity == CAPACITY_EDGE
assert excised_edge.colour == TARGET_EDGE.colour
assert excised_edge.source == "s" and excised_edge.target == "t"
assert not P_E(excised_edge)
assert delta_E == 1
assert edge_binding == 0.0

print("target:", TARGET.name)
print("witness:", S_MINUS.name)
print("budget verdicts:", int(budget_positive(S_PLUS)), int(budget_positive(S_MINUS)))
print("fibre size:", len(target_fibre))
print("delta_C:", delta_C)
print("binding_bits:", binding)
print("profile:", (delta_C, binding))
print("edge_profile:", (delta_E, edge_binding))
print("same_verdict_capacity_profile:", (delta_same, same_binding))
