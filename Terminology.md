# MCell and CellBlender Terminology #

## Introduction ##

Because the CellBlender project involves several specialties (biology, computer science, mcell, python, and blender) there can be a confusing and conflicting usage of common terms like "object", "molecule", and "reaction". Sometimes the context is sufficient to disambiguate usage, but it helps to start with clear definitions that we try to use consistently. This page is intended to help us define and share some of those clear definitions.

NOTE: This is just a proposed usage after a discussion with Tom. This is mostly to experiment with the Wiki and get it bootstrapped for our use.

## Definitions ##

**Object** - This is a highly overloaded term because it means different things in different contexts. In the programming world, it means an instance of a class. In some langauages (like Java) it can also be a top level class which is the super-class of all other classes. In the MCell world, it means cell structures (like cell walls) that are physical ... but excludes individual molecules. In the Blender world, it includes non-MCell items like cameras and lights. For that reason, this is probably not a good term to use without some qualifier and/or a very clear context.

**Molecule** - Refers to an _instance_ of a molecular species. However, it has (in some cases) been used as a synonym for a molecular species. To be clearer, we should strive to use "molecule" or "molecules" when we are talking about specific or aggregate instances, and use the term "molecular species" (or just "species") when talking about a particular kind of molecule.

**Reaction** - Refers to a type of reaction rather than a specific reaction. When referring to a specific reaction instance, the term "reaction occurrence" is preferred. Note that this creates somewhat of a logical inconsistency since we are using "Molecule" to be an instance and using "Reaction" to essentially be a species of reaction (requiring "reaction occurrence" to specify an actual instance.