# FSM-evolve
Evolving propensities of finite state machines for analysing dynamics related to evolutionary behaviours

# status
at the moment - pretty rough-as-guts and sketchy too ...it's working... only just.

# Introduction
some of the most controversial claims about evolution concern explanations of behaviour generally and particularly of human behaviour.
many of these ideas (or at-least the dynamics behind them) should - if feasible - be demonstrable in a sensibly constructed artificial-life sim.
constructing such a simulation isn't particularly easy

# Design
A population of individuals can be modelled as densities flowing between a finite number of states.
At each state there is a number of choices are available to the individuals, which may be common to other states.
each choice yields a transmission of density to other states, which may depend on the on the population distribution itself.
the 'genetics' of the population are their propensities (ratio between probabilities) towards one choice over another.
using the GUI to setup such an arrangement - the simulation is initiated and evolves the genetics to yield the final state densities and transmission rates.
from which useful hypotheses may perhaps be inferred.

# Concepts
Any artificial life simulation can (in principle) be visualised as being composed of agents, interacting according to constructed rules across a finite (perhaps big) number of states.
the population itself can be seen to be in the compound-state of all its agents, and the process of the simulation as the taking of a trajectory in this compound-state-space.
However a population's time-evolution can be made continuous and be visualised as a probability/density flow across the state-space of the agents.
The rates of transmission between states in this flow is governed by statistics about the population's state-densities.
the steady-state-flow representing evolutionary stable states and the net rate of growth in such as steady-state is the fitness.

a mutant subpopulation (if the mutation is hidden and ideal mixing occurs) will evolve according to the steady-flow distribution of the super-population, and under its own genetic influences.
these genetic influences can be represented a difference in preferences between 'choices' of alternative actions for the individual; and the result of any choice being dependant on the 'environment' (ie. the densities of the superpopulation).
the fitness of one-or-several mutations (and of no mutation) can be evaluated and compared in the context of the superpopulation, and the most fit's preferences can be incorporated into that of the superpopulation's average.
this iteration can continue until such a time as there are no mutations which yield further advantage 

