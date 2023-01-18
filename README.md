# Pipeline for *In Vivo* Imaging Analysis

Simply a repo for the analysis of *in vivo* calcium imaging and optogenetics experiments during mouse behavior. I am slowly migrating my entire multi-language/multi-environment analysis pipeline to this single codebase. Its purpose is generally for version control, but feel free to use whatever is useful to you. This repo makes use of several packages I have written that can be downloaded separately to facilitate use (and avoid having to deal with this repo's dependency armageddon).

### To-Do
+ Seperate Large NDARRAY & Dataframes from JSON to binary?
+ Full implementation for multi-plane
+ Full implementation for multi-color "coloring"
+ Convience wrapper (ok maybe not, see below)
+ deal with dependency spaghetti & code spaghetti and all spaghettis
+ Pull out Management for separately maintained repo
+ Pull out Bruker Meta for separately maintained repo
+ Pull out IO for separately maintained repo (?)
+ Pull out Coloring for separately maintained repo

### Coding Style
Generally follows PEP8
