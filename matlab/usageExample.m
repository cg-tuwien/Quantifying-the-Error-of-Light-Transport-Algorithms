% Copyright (c) 2019, Adam Celarek
% All rights reserved.
% 
% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is 
% furnished to do so, subject to the following conditions:
% 
% The above copyright notice and this permission notice shall be included in
% all copies or substantial portions of the Software.
% 
% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
% THE SOFTWARE.

function usageExample()
% render output should not be stored as png because the bit depth is not
% sufficient. However, HDR formats can not be read by default in matlab,
% hence a function must be provided. An example is https://github.com/banterle/HDR_Toolbox
%config.imReadFun = @hdrimread;
config.imReadFun = @exrread;

% regexpes are applied on the whole path. The time budget is used for
% scaling, while the sample budget is used only for the legend.
% the regexp should match a subpath containing the time and sample budget,
% respectively. the number itself is then extracted from the match.
config.timeBudgetRegexp = '_timeBudget_\d+\.?\d*';
config.sampleBudgetRegexp = '_sampleBudget_\d+';
config.shortRenderingRegexp = '\.exr$';
config.maxN = 4000;

% ESE is computed on a greyscale image. These are the factors used for
% computing it.
config.lumFct = [0.212671, 0.715160, 0.072169];
% limits the number of threads if there is not sufficient memory on large
% machines
config.nThreads = 4;
config.nImgPerWorkUnit = 20;    % imageSize * nImgPerWorkUnit * nThreads * 3 must fit into memory
% absolute error = render - reference
% relative error = absolute error / reference
config.useRelativeError = false;
config.lowerTailBodyBorder = .10;
config.lowerBodyHeadBorder = .20;
config.upperHeadBodyBorder = .80;
config.upperBodyTailBorder = .90;

% All standard deviation images are in the range [0 cutoff]
config.stdDevImgCutoff = 10;
% Used for compression, the number of line segments is reduced
% The maximum is the number of frequencies, i.e. image size / 2.
config.svgLineReductionN = 60;
% you can use the following to have plots of several scenes etc in one
% range. [min max], -1 means that it'll be determined automatically.
config.errorRangeForPlotting = [5*10^4 3*10^9];

% once computed, you can comment the these lines, load a cached version
% and edit the graph (if needed).
fileList = Helper.getFileList('./shortRenderings/torus/memlt_sampleBudget_2_timeBudget_4.134188888072967', config);
fileList((config.maxN + 1):end) = [];
eses(1) = computeEse(fileList, 'MLT', config);
refLessEses(1) = computeEse(fileList, 'MLT', config);

tic
fileList = Helper.getFileList('./torus/pt_sampleBudget_3_timeBudget_3.4696708703041077', config);
fileList((config.maxN + 1):end) = [];
eses(2) = computeEse(fileList, 'PT', config);
refLessEses(2) = computeEse(fileList, 'PT', config);
toc
save('esesCached.mat', 'eses')
save('refLessEsesCached.mat', 'refLessEses')

load('esesCached.mat', 'eses')
load('refLessEsesCached.mat', 'refLessEses')

visualiseESEs(eses, 'testOut', config);
visualiseESEs(refLessEses, 'refLesTestOut', config);

end

