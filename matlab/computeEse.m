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

function [ ese ] = computeEse(fileList, name, config, referencePath)
%COMPUTEESE Computes the ese descriptor for the data in fileList
%   fileList: array of structures with the fields path, spp and renderTime
%   referencePath: path to the high quality reference image
%   name: of the algorithm, used for identification in visualiseESEs()
%   config: configuration, an example is given in usageExample

    ese.shortRenderingMean = computeMeanShortRendering(fileList, config);
    if exist('referencePath', 'var')
        reference = config.imReadFun(referencePath);
    else
        reference = ese.shortRenderingMean;
    end
    
    reference = Helper.luminance(reference, config);
    N = length(fileList);
    ese.nImgs = N;
    
    %% compute range that will be used for the error descriptor (in case the images are not square and power of 2
    s = 2^floor(log2(min(size(reference))));
    refS = size(reference);
    tl = floor(refS/2) - s/2 + 1;
    br = floor(refS/2) + s/2;
    config.colRange = tl(1):br(1);
    config.rowRange = tl(2):br(2);
    config.eseSize = s;
    ese.nFreqs = s/2;
    reference = reference(config.colRange, config.rowRange);
    
    %% compute time normalisation factors, i.e. for normalisation to one second.
    ese.averageTime = mean(cell2mat({fileList.renderTime}));
    ese.averageSpp = mean(cell2mat({fileList.spp}));
    config.timePerSampleLayer = mean(cell2mat({fileList.renderTime}) ./ cell2mat({fileList.spp}));
    ese.averageTimePerSampleLayer = config.timePerSampleLayer;
    
    
    %% prepare / divide data onto a selected number of threads
    for t=1:config.nThreads
        threadData(t).N = ceil(N / config.nThreads); %#ok<AGROW>
        threadData(t).indexStart = (t-1)*threadData(t).N+1; %#ok<AGROW>
        threadData(t).indexEnd = min(N, (t)*threadData(t).N); %#ok<AGROW>
        threadData(t).fileList = fileList(threadData(t).indexStart:threadData(t).indexEnd); %#ok<AGROW>
        threadData(t).N = length(threadData(t).fileList); %#ok<AGROW>
        threadData(t).sqErrorSum = zeros(config.eseSize, config.eseSize); %#ok<AGROW>
        threadData(t).covSum = zeros(config.eseSize, config.eseSize); %#ok<AGROW>
        threadData(t).workResults = zeros(threadData(t).N, s/2+1); %#ok<AGROW>
    end
    
    %% compute radial averages, mse per image and a per pixel sum of squared error (for variance per pixel calc)
    if config.nThreads > 1
        parfor t=1:config.nThreads
            for i=threadData(t).indexStart:config.nImgPerWorkUnit:threadData(t).indexEnd %#ok<PFBNS>
                from = i;
                to = min(i+config.nImgPerWorkUnit-1, threadData(t).indexEnd);
                [workResults, sqErrorSum] = computeRadAvgs(fileList(from:to), reference, config); %#ok<PFBNS>

                threadData(t).workResults((from:to)-threadData(t).indexStart+1, :) = workResults;
                threadData(t).sqErrorSum = threadData(t).sqErrorSum + sqErrorSum;
            end
        end
    else
        t=1;    % do not start thread pool etc. if only one thread used.
        for i=1:config.nImgPerWorkUnit:threadData(t).N
            from = i;
            to = min(i+config.nImgPerWorkUnit-1, N);
            [workResults, sqErrorSum] = computeRadAvgs(fileList(from:to), reference, config);

            threadData(t).workResults(from:to, :) = workResults;
            threadData(t).sqErrorSum = threadData(t).sqErrorSum + sqErrorSum;
        end
    end
    
    %% unpack and combine thread data
    ese.varianceImage = zeros(config.eseSize, config.eseSize);
    workResults = zeros(N, s/2+1);
    for t=1:config.nThreads
        ese.varianceImage = ese.varianceImage + threadData(t).sqErrorSum;
        workResults(threadData(t).indexStart:threadData(t).indexEnd, :) = threadData(t).workResults;
    end
    
    ese.varianceImage = ese.varianceImage / N;
    ese.standardDeviationImage = sqrt(ese.varianceImage);
    
    %% covariance image (sum of covariances of the given pixel with every other)
    if config.nThreads > 1
        parfor t=1:config.nThreads
            for i=threadData(t).indexStart:config.nImgPerWorkUnit:threadData(t).indexEnd %#ok<PFBNS>
                from = i;
                to = min(i+config.nImgPerWorkUnit-1, threadData(t).indexEnd);
                
                threadData(t).covSum = threadData(t).covSum + ...
                    sum(computeCovs(fileList(from:to), reference, config, ese.varianceImage), 3); %#ok<PFBNS>
            end
        end
    else
        t=1;    % do not start thread pool etc. if only one thread used.
        for i=1:config.nImgPerWorkUnit:threadData(t).N
            from = i;
            to = min(i+config.nImgPerWorkUnit-1, N);

            compCovs = computeCovs(fileList(from:to), reference, config, ese.varianceImage);
            threadData(t).covSum = threadData(t).covSum + ...
                sum(compCovs, 3);
        end
    end
    
    %% unpack and combine thread data for covariances
    ese.covarianceImage = zeros(config.eseSize, config.eseSize);
    for t=1:config.nThreads
        ese.covarianceImage = ese.covarianceImage + threadData(t).covSum;
    end
    
    ese.covarianceImage = ese.covarianceImage / (N -1);
    ese.sqrtCovarianceImage = sqrt(ese.covarianceImage);
    
    
    %% sort radial averages
    [~, sortedIndices] = sort(workResults(:, 1));
    workResults = workResults(sortedIndices, :);

    
    %% ese graphs
    ltRange  =                                    1:ceil(N*config.lowerTailBodyBorder);
    ltbRange = ceil(N*config.lowerTailBodyBorder+1):ceil(N*config.lowerBodyHeadBorder);
    lbhRange = ceil(N*config.lowerBodyHeadBorder+1):ceil(N*0.5);
    uhbRange =                        ceil(N*0.5+1):ceil(N*config.upperHeadBodyBorder);
    ubtRange = ceil(N*config.upperHeadBodyBorder+1):ceil(N*config.upperBodyTailBorder);
    utRange  = ceil(N*config.upperBodyTailBorder+1):N;
    
    ese.mean          = mean(workResults(:,        2:end), 1);
    ese.lowerTail     = mean(workResults(ltRange,  2:end), 1);
    ese.lowerTailBody = mean(workResults(ltbRange, 2:end), 1);
    ese.lowerBodyHead = mean(workResults(lbhRange, 2:end), 1);
    
    ese.upperHeadBody = mean(workResults(uhbRange, 2:end), 1);
    ese.upperBodyTail = mean(workResults(ubtRange, 2:end), 1);
    ese.upperTail =     mean(workResults(utRange,  2:end), 1);
    
    %% other, scalar ese data
    
    ese.mse = mean(workResults(:, 1));
    ese.mseVariance = var(workResults(:, 1));
    ese.mseStdDev = sqrt(ese.mseVariance);
    
    ese.rmse = sqrt(ese.mse);
    ese.rmseVariance = var(sqrt(workResults(:, 1)));
    ese.rmseStdDev = sqrt(ese.rmseVariance);
    
    % see also ese.averageTime, ese.averageSpp and
    % ese.averageTimePerSampleLayer (computed above)
    
    ese.name = name;
end

function [ mean ] = computeMeanShortRendering(fileList, config)
    dummy = config.imReadFun(fileList(1).path);
    N = length(fileList);
    for t=1:config.nThreads
        threadData(t).N = ceil(N / config.nThreads); %#ok<AGROW>
        threadData(t).indexStart = (t-1)*threadData(t).N+1; %#ok<AGROW>
        threadData(t).indexEnd = min(N, (t)*threadData(t).N); %#ok<AGROW>
        threadData(t).fileList = fileList(threadData(t).indexStart:threadData(t).indexEnd); %#ok<AGROW>
        threadData(t).N = length(threadData(t).fileList); %#ok<AGROW>
        
        threadData(t).mean = zeros(size(dummy)); %#ok<AGROW>
    end
    
    parfor t=1:config.nThreads
        if ~isempty(threadData(t).fileList)
            mean = config.imReadFun(threadData(t).fileList(1).path); %#ok<PFBNS>
            for i=2:length(threadData(t).fileList)
                img = config.imReadFun(threadData(t).fileList(i).path);
                mean = mean + (img - mean) / i;
            end
            threadData(t).mean = mean;
        end
    end
    
    mean = zeros(size(dummy));
    for t=1:config.nThreads
        mean = mean + threadData(t).mean * threadData(t).N / N;
    end
end

function [ covs ] = computeCovs(fileList, reference, config, varianceImage)
    % equation:
    % tmp = (\Err_{m, n}^2 - \widehat{Var{\Err_m}})
    % covImg[m] = \frac{1}{(N-1) M} \sum_{n=1}^N tmp[m] \sum_{m'=1}^M tmp[m']
    
    N = length(fileList);
    M = numel(varianceImage);
    tmp = zeros(size(reference, 1), size(reference, 2), N);
    for i=1:N
        img = Helper.luminance(config.imReadFun(fileList(i).path), config) - reference;
        tmp(:, :, i) = img(config.colRange, config.rowRange, :) .* sqrt( config.timePerSampleLayer * fileList(i).spp);
    end
    
    if config.useRelativeError
        tmp = bsxfun(@rdivide, tmp, reference+0.001);
    end
    
    tmp = tmp.^2;
    %tmp = (\Err_{m, n}^2 - \widehat{Var{\Err_m}})
    tmp = bsxfun(@minus, tmp, varianceImage);
    
%     varvarE = tmp .* tmp;
    
    % \frac{1}{M}\sum_{m'=1}^M tmp[m']
    innerSum = sum(sum(tmp, 1), 2) / M;
    
    % tmp[m] \sum_{m'=1}^M tmp[m']
    tmp = bsxfun(@times, tmp, innerSum);
    
%     tmp = tmp - varvarE / M;
    
    
%     \sum_{n=1}^N tmp[m] \sum_{m'=1}^M tmp[m'] (1/(N-1) calculated later)
    covs = sum(tmp, 3);
end

function [ workResult, sqErrSum] = computeRadAvgs(fileList, reference, config)
    N = length(fileList);
    errCube = zeros(size(reference, 1), size(reference, 2), N);
    for i=1:N
        img = Helper.luminance(config.imReadFun(fileList(i).path), config) - reference;
        errCube(:, :, i) = img(config.colRange, config.rowRange, :) .* sqrt( config.timePerSampleLayer * fileList(i).spp);
    end
    
    if config.useRelativeError
        errCube = bsxfun(@rdivide, errCube, reference+0.001);
    end
    
    errCubeSq = errCube.^2;
    workResult(1:N, 1) = fftshift(shiftdim(mean(mean(errCubeSq, 1), 2), 2));
    sqErrSum = sum(errCubeSq, 3);
    clear errCubeSq;
    
    errCubePwrSpectrum = fftshift(abs(fft2(errCube))).^2;
    workResult(1:N, 2:(config.eseSize/2 + 1)) = Helper.radAvg(errCubePwrSpectrum)';
end

