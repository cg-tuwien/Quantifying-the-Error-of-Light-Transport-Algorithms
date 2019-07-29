# Quantifying the Error of Light Transport Algorithms
![teaser](https://www.cg.tuwien.ac.at/research/publications/2019/celarek_adam-2019-qelta/celarek_adam-2019-qelta-teaser.png "Overview of the processing and output")
Flow chart of the proposed method with outputs (\*): A long rendering process is partitioned into many short runs (a) which are used to estimate error images (b). These are used to calculate a reliable estimate of the expected mean square error (MSE, c*), that could e.g. be used to rank a set of different rendering algorithms. The error images (b) are also used to generate a standard-deviation-per-pixel visualization (d*), which shows which of several competing algorithms is best for a specific lighting situation. Finally, Fourier powerspectra (e) are computed and combined into the error spectrum ensemble (ESE, f*) that plots the expected error and outliers with respect to frequency, visualizing for instance correlation between pixels.

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

## Paper files
* [full paper](https://www.cg.tuwien.ac.at/research/publications/2019/celarek_adam-2019-qelta/celarek_adam-2019-qelta-paper_preprint.pdf)
* [supplemental material](https://www.cg.tuwien.ac.at/research/publications/2019/celarek_adam-2019-qelta/celarek_adam-2019-qelta-supplemental_material.pdf)
* [presentation slides](https://www.cg.tuwien.ac.at/research/publications/2019/celarek_adam-2019-qelta/celarek_adam-2019-qelta-presentation.pdf)
* [university page](https://www.cg.tuwien.ac.at/research/publications/2019/celarek_adam-2019-qelta/)

## Repository
The repository consists of 3 parts:
- A generator for short renderings in 'python/short_rendering_generator/'.\
  It lets you automate the process of generating short renderings for different algorithms / parameter combinations and scenes. The script first finds a suitable rendering budget (samples per pixel) for a target rendering time. It then generates a list of   rendering commands. These commands are currently executed in parallel on the current machine, but it should be easy to export them to a file and execute e.g. on a cluster computer.
- A MATLAB implementation for calculating ESE, SDpp and some other outputs in 'matlab/'.\
  This implementation was used along with the python generator to generate the data for the paper and is well tested.
- A python implementation for calculating ESE, SDpp and some other outputs in 'python/compute_descriptors/'.\
  This is a reimplementation of the MATLAB version made after the paper was released, it's therefore less tested. The colour mapping of the SDpp images is different, otherwise the outputs should be identical.

You are welcome to commit any improvements you might have.

## Support
Please use the issue tracker if you have any questions, so others can benefit from it.
If you need to send me an e-mail anyways, use Quantifying-the-Error-of-Light-Transport-Algorithms at xibo dot at.
