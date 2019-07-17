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

classdef Helper
    
    properties
    end
    
    methods(Static)
        function out = removeTrailingSlash(in)
            out=in;
            if ~isempty(regexp(out, '/$', 'ONCE'))
                out(length(out))=[];
            end
        end
        
        function out = assureOneTrailingSlash(in)
            out=[Helper.removeTrailingSlash(in) '/'];
        end
        
        function bad = checkForInfAndNan(fileList, config)
            bad = false;
            for i=1:length(fileList)
                img = config.imReadFun(fileList(i).path);
                if hasInfNaN(img)
                    disp(['inf or NaN found in ' fileList(i).path]);
                    bad = true;
                end
            end
        end
        
        function [ fileList ] = getFileList(dataDir, config)

            dataDir = Helper.removeTrailingSlash(dataDir);
            
            list = dir(dataDir);
            if isempty(list)
                fprintf('directory %s is empty\n', dataDir);
                return;
            end
            
            list(cell2mat({list.isdir}) == 1) = [];
            
            %fileList(length(list), 1) = struct('path', [], 'renderTime', [], 'spp', []);
            fileList = struct('path', {}, 'renderTime', {}, 'spp', {});
            
            for i=1:length(list)
                elem = list(i);
                
                filePath = [dataDir '/' elem.name];
                
                if isempty(regexp(filePath, config.shortRenderingRegexp))
                    continue;
                end
                
                fileList(end + 1).path = filePath; %#ok<AGROW>
                
                timeString = regexp(filePath, config.timeBudgetRegexp, 'match');
                timeString = regexp(timeString{1}, '[\d.]+', 'match');
                time = str2double(timeString{1});

                sppString = regexp(filePath, config.sampleBudgetRegexp, 'match');
                sppString = regexp(sppString{1}, '[\d.]+', 'match');
                spp = str2double(sppString{1});
            
                fileList(end).renderTime = time;
                fileList(end).spp = spp;
            end
        end
        
        function [ radMean, radVariance, transformed] = radAvg( img, params )
            if ~exist('params', 'var')
                params.useGPU = false;
            end

            transformed = Helper.radialtransform(img, params);
            radMean = gather(mean(transformed));
            radMean = reshape(radMean, size(radMean, 2), size(radMean, 3));
            radVariance = gather(var(transformed));
            radVariance = reshape(radVariance, size(radVariance, 2), size(radVariance, 3));
        end

        function w=radialtransform(img, params)

            S = Helper.radialdiscretization(size(img));
            w = [min(S(1:2))/2, 4*min(S(1:2))];
            deltaAngle = 2*pi/S(2);
            if params.useGPU
                [r, phi] = meshgrid(gpuArray(0:1:S(1)-1), gpuArray(0:deltaAngle:2*pi-deltaAngle));
            else
                [r, phi] = meshgrid(0:1:S(1)-1, 0:deltaAngle:2*pi-deltaAngle);
            end

            x = r.*cos(phi) + size(img,2)/2 + 1; % +1 is to account for fftshift placing the DC at w/2 + 1, h/2 + 1
            y = r.*sin(phi) + size(img,1)/2 + 1;

            w=Helper.readbilinear(img,x,y);

        end

        function w=radialdiscretization(S)
            w = [min(S(1:2))/2, 4*min(S(1:2))];
        end

        function w=readbilinear(img,x_,y_)
            x = mod(x_-1, size(img,2));
            y = mod(y_-1, size(img,1));
            px0 = floor(x);
            px1 = mod(floor(x+1),size(img,2));
            py0 = floor(y);
            py1 = mod(floor(y+1),size(img,1));
            wx = repmat(x-floor(x),1,1,size(img,3));
            wy = repmat(y-floor(y),1,1,size(img,3));

            if size(img,3) == -3,
                p00 = cat(3, img(sub2ind(size(img),py0(:)+1,px0(:)+1,1*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py0(:)+1,px0(:)+1,2*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py0(:)+1,px0(:)+1,3*ones(length(py0(:)),1))) );

                p01 = cat(3, img(sub2ind(size(img),py0(:)+1,px1(:)+1,1*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py0(:)+1,px1(:)+1,2*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py0(:)+1,px1(:)+1,3*ones(length(py0(:)),1))) );

                p10 = cat(3, img(sub2ind(size(img),py1(:)+1,px0(:)+1,1*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py1(:)+1,px0(:)+1,2*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py1(:)+1,px0(:)+1,3*ones(length(py0(:)),1))) );

                p11 = cat(3, img(sub2ind(size(img),py1(:)+1,px1(:)+1,1*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py1(:)+1,px1(:)+1,2*ones(length(py0(:)),1))), ...
                             img(sub2ind(size(img),py1(:)+1,px1(:)+1,3*ones(length(py0(:)),1))) );
            elseif size(img,3) == 1
                p00 = img(sub2ind(size(img),py0(:)+1,px0(:)+1));
                p01 = img(sub2ind(size(img),py0(:)+1,px1(:)+1));
                p10 = img(sub2ind(size(img),py1(:)+1,px0(:)+1));
                p11 = img(sub2ind(size(img),py1(:)+1,px1(:)+1));
            else
                thirdCoord = ((1:size(img, 3))'*ones(length(py0(:)),1)')';
                p00 = img(sub2ind(size(img), (repmat(py0(:)+1, size(img, 3), 1)), (repmat(px0(:)+1, size(img, 3), 1)), thirdCoord(:)));
                p01 = img(sub2ind(size(img), (repmat(py0(:)+1, size(img, 3), 1)), (repmat(px1(:)+1, size(img, 3), 1)), thirdCoord(:)));
                p10 = img(sub2ind(size(img), (repmat(py1(:)+1, size(img, 3), 1)), (repmat(px0(:)+1, size(img, 3), 1)), thirdCoord(:)));
                p11 = img(sub2ind(size(img), (repmat(py1(:)+1, size(img, 3), 1)), (repmat(px1(:)+1, size(img, 3), 1)), thirdCoord(:)));
            end

            p00 = reshape(p00,[size(x), size(img,3)]);
            p01 = reshape(p01,[size(x), size(img,3)]);
            p10 = reshape(p10,[size(x), size(img,3)]);
            p11 = reshape(p11,[size(x), size(img,3)]);

            w = (1-wy).*(1-wx).*p00 + (1-wy).*wx.*p01 + wy.*(1-wx).*p10 + wy.*wx.*p11;
        end
        
        function [ l ] = luminance( img, config )
            if size(img, 3) == 3
                l = config.lumFct(1) * img(:,:,1,:) + config.lumFct(2) * img(:,:,2,:) + config.lumFct(3) * img(:,:,3,:);
                return;
            end
            if size(img, 3) == 1
                l=img;
                return;
            end
            error('luminance functions works only if the 3rd dimension is 1 or 3');
        end
        
        function [ldrImage, usedParams] = toneMap(hdrImage, config, params)
            %TONEMAPREINHARDMOD Summary of this function goes here
            %   Detailed explanation goes here

            % formulas from Realtime HDR Rendering (Christian Luksch 2007, Bachelor Thesis
            % at TU Vienna)

            hdrImageLum = Helper.luminance(hdrImage, config);

            if ~exist('params', 'var')
                params = struct();
            end

            if ~isfield(params, 'delta')
                params.delta = 0.001;
            end

            if ~isfield(params, 'L_average')
                tmp = log(params.delta + hdrImageLum);
                params.L_average = exp(mean(tmp(:)));
            end

            if ~isfield(params, 'L_white')
                params.L_white = mean(hdrImageLum(hdrImageLum>quantile(hdrImageLum(:), 0.999)));
                params.L_white = 0.8;
            end

            if ~isfield(params, 'key_a')
                params.key_a = max(0, 1.5 - 1.5 / (params.L_average*0.1 + 1))+0.1;
            end

            if ~isfield(params, 'method')
                params.method = 'reinhard_mod';
            end

            scaled = (params.key_a / params.L_average) * hdrImage;
            usedParams = params;

            if strcmp(params.method, 'log')
                ldrImage = log(hdrImage + 0.001);
            end

            if strcmp(params.method, 'linear')
                maxLum = max(max(hdrImageLum));
                ldrImage = hdrImage ./ maxLum;
            end

            % reinhard
            if strcmp(params.method, 'reinhard')
                ldrImage = scaled ./ (1 + scaled);
            end

            % reinhard mod
            if strcmp(params.method, 'reinhard_mod')
                ldrImage = (scaled .* (1 + scaled./(params.L_white^2))) ./ (1 + scaled);
            end
            gamma = 2.2;
            ldrImage = power(ldrImage, 1/gamma);
        end
        
        % variant == 0 -> linearised + gamma correction
        % variant == 1 -> wiggely + gamma correction
        % variant == 2 -> linearised + no gamma correction
        % variant == 3 -> wiggely + no gamma correction
        function map = myColourMap(n, variant)
            if nargin < 1
               n = size(get(gcf,'Colormap'),1);
            end

            parulaCM = parula(256);
            parulaFirst = parulaCM(1, :);
            parulaLast = parulaCM(end, :);

            parulaCM(1, :) = [];
            parulaCM(end, :) = [];

            values = [
                       interp1(1:2, [0 0 0; parulaFirst], linspace(1,2,25), 'linear')
                       parulaCM
                       interp1(1:2, [parulaLast; 1 1 1], linspace(1,2,20), 'linear')
                       ];

            P = size(values,1);
            
            % variant == 0 -> linearised + gamma correction
            % variant == 1 -> wiggely + gamma correction
            % variant == 2 -> linearised + no gamma correction
            % variant == 3 -> wiggely + no gamma correction
            
            if mod(variant, 2) == 0
                lum = 0.212671 * values(:,1) + 0.715160 * values(:,2) + 0.072169 * values(:,3);  % luminance as seen by the human eye
                linear = linspace(0,1,length(lum))';
                scalingFactor = linear./lum;    % scale, so that luminace is linear from 0 to 1
                scalingFactor(1) = 1;

                values = bsxfun(@times, values, scalingFactor);
                surplus = max(0, values-1);    % red goes above 1, distribute the surplus on the other two channels
                values(:, 1) = values(:, 1) - surplus(:, 1);
                values(:, 2) = values(:, 2) + surplus(:, 1)*0.5*0.212671/0.715160;
                values(:, 3) = values(:, 3) + surplus(:, 1)*0.5*0.212671/0.072169;

                surplus = max(0, values-1);    % green goes above 1 only at the end, add to blue as red is also above
                values(:, 2) = values(:, 2) - surplus(:, 2);
                values(:, 3) = values(:, 3) + surplus(:, 2)*0.715160/0.072169;
            end
            
            if variant >= 2
                map = interp1(1:P, values, linspace(1,P,n), 'linear'); % old / no gamma correction
            else
                map = interp1(1:size(values,1), values, power(linspace(0,1,n), 1/2.2).*(P-1)+1, 'linear'); % gamma correction
            end
            
%             figure;
%             plot(map);
%             hold on;
%             plot(0.212671 * map(:,1) + 0.715160 * map(:,2) + 0.072169 * map(:,3));
%             legend('r', 'g', 'b', 'lum');
        end

        % Reduce polygon to a given number of vertices
        %
        % poly = reduce_poly(poly, num)
        %
        % Inputs: poly        Polygon (2 rows, n columns)
        %         num         Required number of vertices
        %
        % Outputs: poly       Final polygon
        %
        % Description: This code reduces the number of vertices in a closed polygon
        % to the number specified by 'num'. It does this by calculating the
        % importance of each vertex based on angle and segment length and then
        % removing the least important. The process is repeated until the desired
        % number of vertices is reached.
        %
        % Example:
        % t = 0:0.1:2*pi;
        % poly1 = [sin(t); cos(t)];
        % poly2 = reduce_poly(poly1, 21);
        % poly_draw = [poly2 poly2(:,1)];
        % plot(poly_draw(1,:), poly_draw(2,:), '.-')
        % axis equal
        %
        % Coded by: Peter Bone (peterbone@hotmail.com)
        % Copyright (c) 2014, Peter Bone
        % All rights reserved.
        % 
        % Redistribution and use in source and binary forms, with or without
        % modification, are permitted provided that the following conditions are
        % met:
        % 
        %     * Redistributions of source code must retain the above copyright
        %       notice, this list of conditions and the following disclaimer.
        %     * Redistributions in binary form must reproduce the above copyright
        %       notice, this list of conditions and the following disclaimer in
        %       the documentation and/or other materials provided with the distribution
        % 
        % THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        % AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        % IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
        % ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
        % LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
        % CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
        % SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
        % INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
        % CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
        % ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
        % POSSIBILITY OF SUCH DAMAGE.
        %------------------------------------------------------------------------
        function poly = reduce_poly(poly, num)
            numv = length(poly);

            % Calculate initial importance of each vertex
            imp = zeros(1,numv);
            for v = 1 : numv
                imp(v) = Helper.vertex_importance(v, poly, numv);
            end

            % Iterate until desired number of vertices is reached
            while numv > num
                [~, i] = min(imp(1:numv));

                % Remove vertex with least importance
                if i < numv
                    poly(:,i:numv-1) = poly(:,i+1:numv);
                    imp(i:numv-1) = imp(i+1:numv);
                    vp = i;
                else
                    vp = 1;
                end
                numv = numv - 1;

                % Recalculate importance for vertices neighbouring the removed one
                vm = 1 + mod(i - 2, numv);
                imp(vp) = Helper.vertex_importance(vp, poly, numv);
                imp(vm) = Helper.vertex_importance(vm, poly, numv);
            end

            % Clip polygon to the final length
            poly = poly(:,1:num);
        end

        function a = vertex_importance(v, poly, numv)
            % Find adjacent vertices
            vp = 1 + mod(v, numv);
            vm = 1 + mod(v - 2, numv);

            % Obtain adjacent line segments and their lengths
            dir1 = poly(:,v) - poly(:,vm);
            dir2 = poly(:,vp) - poly(:,v);
            len1 = norm(dir1);
            len2 = norm(dir2);

            % Calculate angle between vectors and multiply by segment lengths
            % This is the importance of the vertex.
            % Vertices with large angle and large segments attached are less
            % likely to be removed
            len1len2 = len1 * len2;
            if len1len2 == 0
                a=0;
                return;
            end
            a = abs(acos((dir1' * dir2) / len1len2)) * len1len2;
            %a = abs(1 - ((dir1' * dir2) / len1len2)) * len1len2;
        end
    end
end
