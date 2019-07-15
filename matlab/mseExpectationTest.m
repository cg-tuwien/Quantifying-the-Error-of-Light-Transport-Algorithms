% Copyright (c) 2019, Adam Celarek
% Copyright (c) 2016, Jaakko Lehtinen
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

function mseExpectationTest()
f = figure('Color', 'w');
f.Position = [00, 1000, 300, 200];
f.PaperPosition = [0, 0, 3, 2];
% mySubplot = @(m,n,p) subtightplot(m, n, p, [0.005 0.005], [0.18 0.08], [0.06 0.01]);
%   gap- two elements vector [vertical,horizontal] defining the gap between neighbouring axes. Default value
%            is 0.01. Note this vale will cause titles legends and labels to collide with the subplots, while presenting
%            relatively large axis. 
%   marg_h  margins in height in normalized units (0...1)
%            or [lower uppper] for different lower and upper margins 
%   marg_w  margins in width in normalized units (0...1)
%            or [left right] for different left and right margins 

% mySubplot(1, 5, 2);
bothMethodsProg(5, @rand, @(dta)1, 9914.17, [0.0, 0.45, 0.7], [0.7, 0.0, 0], [0.0, 0.7, 0]);
% oldMethod(10, @genImportanceSamples, @importanceSampleProb, 4918.77, [0.7, 0.0, 0]);
set(gca, 'YTickLabel', []);
set(gca, 'XTick', [1, 100, 10000, 1000000]);
% title('')
legend('closed form E(MSE)', 'MSE', 'estimated E(MSE)')
xlabel('N')
ylabel('MSE')

saveas(f, 'mseVsEstExpMse.svg');
end

function bothMethodsProg(nPixels, genSamples, sampleProb, analVar, colourOld, colourNew, colourGroundTruth)
    exact=9.21044036697652; %1/(0.0001+rnd)
%     exact=6.90875477931522; %1/(0.001+rnd)
    %exact=11.51293546492023; %1/(0.00001+rnd)
    
rndDta = genSamples(10^7, nPixels);
vals = getValsFor(rndDta, sampleProb);

sampleC = int32(10.^(0:0.05:log10(size(rndDta, 1))));

measuredErrOldMethod = arrayfun(@(n)(  mean((mean(vals(1:n, :), 1)-exact).^2, 2)  ), sampleC);
measuredErrNewMethod = arrayfun(@(n)(  mean(mean((vals(1:n, :)-exact).^2, 1))/double(n)  ), sampleC);

loglog([1,max(double(sampleC))], [analVar, analVar/max(double(sampleC))], 'Color', colourGroundTruth); hold on
loglog(sampleC, measuredErrOldMethod, 'Color', colourOld); hold on
loglog(sampleC, measuredErrNewMethod, 'Color', colourNew); hold on


axis([1, max(sampleC), 10^-4, 10^4])

% title(['average betwen ' num2str(avgSamples) ' processes']);
end

function vals = getValsFor(rndDta, sampleProb)
    vals = (1./(rndDta+0.0001))./sampleProb(rndDta);
end

function pd = importanceSampleProb(dta)
    pd = 2-2*dta;
end

function rndDta = genImportanceSamples(rows, cols)
    rndDta = 1-sqrt(1-rand(rows, cols));
end


