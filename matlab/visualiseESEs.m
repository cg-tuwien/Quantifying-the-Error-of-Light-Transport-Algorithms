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

function visualiseESEs( eses, outDir, config, tmParams)
%VISUALISEESES exports the standard deviation images with a nice colour map
%and make the ESE plots as seen in the paper.
%   eses: array of structures as returned by computeEse
%   outDir: destination for svg and png output
%   config: configuration, an example is given in usageExample
%   tmParams: optional tone mapping parameters
mkdir(outDir);

if ~exist('tmParams', 'var')
    [~, tmParams] = Helper.toneMap(eses(1).shortRenderingMean, config);
end

%% prep
fig = figure('Color', 'w');
fig.Position = [00, 500, 330, 300];
fig.PaperPosition = [0, 0, 2.00, 3.00];
axe = subplot('Position', [0.15 0.15+0.05*length(eses) 0.82 0.84-0.05*length(eses)]);

labels = arrayfun(@(ese){...
    [ese.name ' (RMSE:' shortNum2Str(ese.rmse) ', s:' shortNum2Str(ese.rmseStdDev) ...
                 ', t:' shortNum2Str(ese.averageSpp) 'x' shortNum2Str(ese.averageTimePerSampleLayer) 's)'] ...
    }, eses);

colours = [ [0.7, 0.0, 0];
            [0.0, 0.45, 0.7];
            [0.7, 0.45, 0.0];
            [0.0, 0.6, 0];
            [0.9, 0.5, 0.0];
            [0.75, 0.0, 0.75];
            [0.7, 0.5, 0]];

%% std dev and covariance images
for i=1:length(eses)
    imwrite(Helper.toneMap(eses(i).shortRenderingMean, config, tmParams), [Helper.assureOneTrailingSlash(outDir) 'mean_' eses(i).name '.jpg']);
    
    imwrite(ind2rgb(gray2ind(eses(i).standardDeviationImage ./ config.stdDevImgCutoff, 2^16), ...
                    Helper.myColourMap(2^16, 0)), ...
            [Helper.assureOneTrailingSlash(outDir) 'stdDev_' eses(i).name '.png']);
    
    covarianceImageMvdRng = (eses(i).covarianceImage + config.stdDevImgCutoff^2) / 2;
    covarianceImageMvdRng(covarianceImageMvdRng < 0) = 0;
    covarianceImageMvdRng(covarianceImageMvdRng > config.stdDevImgCutoff^2) = config.stdDevImgCutoff^2;
    imwrite(ind2rgb(gray2ind(covarianceImageMvdRng ./ config.stdDevImgCutoff^2, 2^16), ...
                    Helper.myColourMap(2^16, 0)), ...
            [Helper.assureOneTrailingSlash(outDir) 'cov_' eses(i).name '.png']);
    
    sqrtCovWithoutVar = sqrt(eses(i).covarianceImage);
    covarianceImageMvdRng = real(sqrtCovWithoutVar) - imag(sqrtCovWithoutVar);
    covarianceImageMvdRng = (covarianceImageMvdRng + config.stdDevImgCutoff) / 2;
    covarianceImageMvdRng(covarianceImageMvdRng < 0) = 0;
    covarianceImageMvdRng(covarianceImageMvdRng > config.stdDevImgCutoff^2) = config.stdDevImgCutoff^2;
    imwrite(ind2rgb(gray2ind(covarianceImageMvdRng ./ config.stdDevImgCutoff, 2^16), ...
                    Helper.myColourMap(2^16, 0)), ...
            [Helper.assureOneTrailingSlash(outDir) 'sqrtCov_' eses(i).name '.png']);
end

%% graphs
X = [1:eses(i).nFreqs, eses(i).nFreqs:-1:1];

for i=1:length(eses)
    % tail
    Y = [eses(i).lowerTail'; flipud(eses(i).upperTail')]';
    reducedPoly = reduce_polyProxy([X;Y], 2 * config.svgLineReductionN);
    X_ = reducedPoly(1, :);
    Y = reducedPoly(2, :);
    s = fill(X_, Y, colours(i, :), 'LineStyle', 'none'); hold on
    alpha(s, 0.2);
end
for i=1:length(eses)
    % body
    Y = [eses(i).lowerTailBody'; flipud(eses(i).upperBodyTail')]';
    reducedPoly = reduce_polyProxy([X;Y], 2 * config.svgLineReductionN);
    X_ = reducedPoly(1, :);
    Y = reducedPoly(2, :);
    s = fill(X_, Y, colours(i, :), 'LineStyle', 'none'); hold on
    alpha(s, 0.2);

    % head
    Y = [eses(i).lowerBodyHead'; flipud(eses(i).upperHeadBody')]';
    reducedPoly = reduce_polyProxy([X;Y], 2 * config.svgLineReductionN);
    X_ = reducedPoly(1, :);
    Y = reducedPoly(2, :);
    s = fill(X_, Y, colours(i, :), 'LineStyle', 'none'); hold on
    alpha(s, 0.4);
end
    
for i=1:length(eses)
    % mean
    Y = eses(i).mean;
    reducedPoly = reduce_polyProxy([1:eses(i).nFreqs;Y], config.svgLineReductionN);
    X_ = reducedPoly(1, :);
    Y = reducedPoly(2, :);
    plot(X_, Y, 'LineWidth', 2, 'Color', colours(i, :)); hold on %ui stack on top or uistack(s, 'bottom'); the areas
end

[leg,icons,plots,s] = legend(labels, 'Location', 'southoutside');
leg.Position(2) = 0.01;
leg.Box = 'off';

limits = axis();
limits(1) = 1;
limits(2) = eses(1).nFreqs;
if config.errorRangeForPlotting(1) > 0
    limits(3) = config.errorRangeForPlotting(1);
end
if config.errorRangeForPlotting(2) > 0
    limits(4) = config.errorRangeForPlotting(2);
end
axis(limits);

axe.XScale = 'lin';
axe.YScale = 'log';
axe.XTick = 1:50:10001;
axe.XTickLabel = cellfun(@(x)({num2str(x)}), num2cell(0:50:10000));

ylabel('error');
h_xlabel = xlabel('frequency');
h_xlabel.HorizontalAlignment = 'right';
h_xlabel.Position(1) = 255;
h = text(0, h_xlabel.Position(2), ['N=' num2str(min(cell2mat({eses(:).nImgs})))]);
if var(cell2mat({eses(:).nImgs})) ~= 0
    warning('The ESEs for the given algorithms were not computed with the same number of pictures. Minimum will be reported!')
end
h.FontWeight = 'normal';
h.VerticalAlignment = 'top';
h.HorizontalAlignment = 'left';
h.FontAngle = 'italic';

saveas(fig, [Helper.assureOneTrailingSlash(outDir) 'ese.svg']);

end

function stri = shortNum2Str(num)
    stri = strrep(num2str(num, 3), '+0', '');
end

function poly = reduce_polyProxy(poly, num)
    poly(2, :) = log10(poly(2, :));
    max1 = max(poly(1, :)) * 0.1;
    max2 = max(poly(2, :)) * 0.1;
    poly(1, :) = poly(1, :) ./ max1;
    poly(2, :) = poly(2, :) ./ max2;
    
    poly = Helper.reduce_poly(poly, num);
    
    poly(1, :) = poly(1, :) * max1;
    poly(2, :) = poly(2, :) * max2;
    poly(2, :) = 10.^(poly(2, :));
end
