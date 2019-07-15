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

function runMultipleScenes()
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
% config.timeBudgetRegexp = '/pt\d+';
config.sampleBudgetRegexp = '_sampleBudget_\d+';
config.shortRenderingRegexp = '\.exr$';
config.outputBasePath = './absErr/';
config.referenceBasePath = './references/';
config.shortRenderingsBasePath = './shortRenderings/';
config.maxN = 4000;

% ESE is computed on a greyscale image. These are the factors used for
% computing it.
config.lumFct = [0.212671, 0.715160, 0.072169];
% limits the number of threads if there is not sufficient memory on large
% machines
config.nThreads = 8;
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
% config.errorRangeForPlotting = [5*10^4 5*10^9];
config.errorRangeForPlotting = [-1 -1];

algorithms = {'pt', 'pssmlt', 'memlt'};
config.maxN = 4000;
check({'bathroom', 'bottle', 'door', 'kitchen', 'sponza', 'torus',...
       'boxRoughn1O256Light25', 'boxRoughn1O256Light100', 'boxRoughn1O256Light400'}, algorithms, config)
check({'boxRoughn1O32Light100', 'boxRoughn1O2048Light100'}, algorithms, config)

disp('check finished. starting computations')

config.maxN = 40;
runMultipleScenesWith({'bathroom', 'bottle', 'door', 'kitchen', 'sponza', 'torus'}, algorithms, config)
config.maxN = 400;
runMultipleScenesWith({'bathroom', 'bottle', 'door', 'kitchen', 'sponza', 'torus'}, algorithms, config)
config.maxN = 4000;
runMultipleScenesWith({'bathroom', 'bottle', 'door', 'kitchen', 'sponza', 'torus'}, algorithms, config)
runMultipleScenesWith({'boxRoughn1O256Light25', 'boxRoughn1O256Light100', 'boxRoughn1O256Light400'}, algorithms, config)
runMultipleScenesWith({'boxRoughn1O32Light100', 'boxRoughn1O2048Light100'}, algorithms, config)

config.useRelativeError = true;
config.outputBasePath = './relativeErr/';
runMultipleScenesWith({'boxRoughn1O256Light25', 'boxRoughn1O256Light100', 'boxRoughn1O256Light400'}, algorithms, config)
runMultipleScenesWith({'boxRoughn1O32Light100', 'boxRoughn1O2048Light100'}, algorithms, config)
runMultipleScenesWith({'bathroom', 'bottle', 'door', 'kitchen', 'sponza', 'torus'}, algorithms, config)

config.maxN = 16000;
config.useRelativeError = false;
config.outputBasePath = './largeN/';
runMultipleScenesWith({'torus'}, algorithms, config)

end

function check(scenes, algorithms, config)
bad = false;
for s = 1:length(scenes)
    scene = scenes{s};
    path = [config.shortRenderingsBasePath, scene];
    algorithmResultDirs = listAlgorithmDirs(path, algorithms);
    for a=1:length(algorithms)
        algorithm = algorithms{a};
        fileList = Helper.getFileList(algorithmResultDirs(algorithm), config);
        fileList((config.maxN+1):end) = [];
        combinationIsBad = Helper.checkForInfAndNan(fileList, config);
        bad = bad || combinationIsBad;
        if length(fileList) < config.maxN
            disp(['Not enough images (' num2str(config.maxN) ' required) in ' algorithmResultDirs(algorithm)]);
            bad = true;
        end
    end
end

if bad
    error('aborting');
end
end

function runMultipleScenesWith(scenes, algorithms, config)

for s = 1:length(scenes)
    scene = scenes{s};
    path = [config.shortRenderingsBasePath, scene];
    algorithmResultDirs = listAlgorithmDirs(path, algorithms);
    refPath = [config.referenceBasePath scene '.exr'];
    
    mkdir([config.outputBasePath scene '_N' num2str(config.maxN) '_refWith']);
    mkdir([config.outputBasePath scene '_N' num2str(config.maxN) '_refLess']);
    [refTm, tmParams] = Helper.toneMap(config.imReadFun(refPath), config);
    imwrite(refTm, [config.outputBasePath scene '_N' num2str(config.maxN) '_refWith/ref.jpg']);
    imwrite(refTm, [config.outputBasePath scene '_N' num2str(config.maxN) '_refLess/ref.jpg']);
    
    
    for a=1:length(algorithms)
        algorithm = algorithms{a};
        fileList = Helper.getFileList(algorithmResultDirs(algorithm), config);
        fileList((config.maxN+1):end) = [];
        
        example = Helper.toneMap(config.imReadFun(fileList(1).path), config, tmParams);
        imwrite(example, [config.outputBasePath scene '_N' num2str(config.maxN) '_refWith/exampleShortRendering_' algorithm '.jpg']);
        imwrite(example, [config.outputBasePath scene '_N' num2str(config.maxN) '_refLess/exampleShortRendering_' algorithm '.jpg']);
         
        eses_refWith(a) = computeEse(fileList, upper(algorithm), config, refPath); %#ok<AGROW>
        eses_refLess(a) = computeEse(fileList, upper(algorithm), config); %#ok<AGROW>
    end
    
    save([config.outputBasePath scene '_N' num2str(config.maxN) '_esesCached_refWith.mat'], 'eses_refWith')
    save([config.outputBasePath scene '_N' num2str(config.maxN) '_esesCached_refLess.mat'], 'eses_refLess')
    
    load([config.outputBasePath scene '_N' num2str(config.maxN) '_esesCached_refWith.mat'], 'eses_refWith')
    load([config.outputBasePath scene '_N' num2str(config.maxN) '_esesCached_refLess.mat'], 'eses_refLess')

    visualiseESEs(eses_refWith, [config.outputBasePath scene '_N' num2str(config.maxN) '_refWith'], config, tmParams);
    visualiseESEs(eses_refLess, [config.outputBasePath scene '_N' num2str(config.maxN) '_refLess'], config, tmParams);
    close all
end

end

function map = listAlgorithmDirs(path, algorithms)
    structList = dir(path);
    if isempty(structList)
        fprintf('directory %s is empty\n', path);
        return;
    end

    structList(cell2mat({structList.isdir}) == 0) = [];
    map = containers.Map;

    for i=1:length(structList)
        elem = structList(i);
        for a=1:length(algorithms)
            alg = algorithms{a};
            if ~isempty(regexp(elem.name, ['^' alg '.*'], 'once'))
                map(alg) = [path '/' elem.name];
                break;
            end
        end
    end
end

