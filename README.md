# FSM-evolve
Evolving propensities of finite state machines for analyzing dynamics related to evolutionary behaviors

# status
at the moment - pretty rough-as-guts and sketchy too ...its working... only just.

# Introduction
some of the most controvercial claims about evolution concern explanations of behavior generally and particularly-of human behavior.
many of these ideas (or atleast the dynamics behind them) should - if feasible - be demonstrable in a sensibly constructed artifical-life sim.
constructing such a simulation isnt particularly easy

# Design
A population of individuals can be modeled as densities flowing between a finite number of states, where at each state is a number of choices are available to the individuals (which may be common to other states).
each choice yeilds a transmission of density to other states (which may depend on the on the population distribution itself).
the genetics of the population are encoded as their propensities to choose one choice over another (ratio between probabilities).
after setting up such an arrangement - the simulation is initiated and envolves the genetics to yeild the final state densities and transmission rates.
from which usefull hypothesis may perhaps be inferred.

# Concepts
Any artificial life simulation can (in principle) be visualised as being composed of agents, interacting according to constructed rules across a finite (perhaps big) number of states.
the population itself can be seen to be in the compound-state of all its agents, and the process of the simulation as the taking of a trajectory in this compound-state-space.
However a population's time-evolution can be made continuous and be visualised as a probability/density flow across the state-space of the agents.
The rates of transmission between states in this flow is governed by statistics about the population's state-densities.
the steady-state-flow representing evolutionary stable states and the net rate of growth in such as steady-state is the fitness.

a mutant subpopulation (if the mutation is hidden and ideal mixing occurs) will evolve according to the steady-flow distribution of the super-population, and under its own genetic influences.
these genetic influences can be represented a difference in preferences between 'choices' of alternative actions for the individual; and the result of any choice being dependant on the 'environment' (ie. the densities of the superpopulation).
the fitness of one-or-several mutations (and of no mutation) can be evaluated and compared in the context of the superpopulation, and the most fit's preferences can be incoroporated into that of the superpopulation's average.
this iteration can continue until such a time as there are no mutations which yeild further advantage 

