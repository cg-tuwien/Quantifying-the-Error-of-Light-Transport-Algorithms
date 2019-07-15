# Quantifying the Error of Light Transport Algorithms
## Paper Abstract
This paper proposes a new methodology for measuring the error of unbiased physically based rendering algorithms. The
current state of the art includes mean squared error (MSE) based metrics and visual comparisons of equal-time renderings
of competing algorithms. Neither is satisfying as MSE does not describe behavior and can exhibit significant variance, and
visual comparisons are inherently subjective. Our contribution is two-fold: First, we propose to compute many short renderings
instead of a single long run and use the short renderings to estimate MSE expectation and variance as well as per-pixel
standard deviation. An algorithm that achieves good results in most runs, but with occasional outliers is essentially unreliable,
which we wish to quantify numerically. We use per-pixel standard deviation to identify problematic lighting effects of rendering
algorithms. The second contribution is the error spectrum ensemble (ESE), a tool for measuring the distribution of error over
frequencies. The ESE serves two purposes: It reveals correlation between pixels and can be used to detect outliers, which offset
the amount of error substantially.

## Repository
This repository contains a MATLAB and a python implementation for calculating SDpp images and the ESE. Additionally, there is also a python script for generating the short renderings.
