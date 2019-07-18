'''
Documentation, License etc.

@package compute_descriptors
'''

import numpy as np
import math

import conversion
import image
import file_handling
import constants

class RadialAverage:
    def __init__(self, mse, frequencyError):
        self.mse = mse
        self.frequencyError = frequencyError
    
        
class Descriptor:
    def __init__(self, integrator, short_rendering_example, mean, var, radial_averages, avg_spp, avg_time):
        self.integrator = integrator
        self.short_rendering_example = short_rendering_example
        self.mean = mean
        self.var = var
        self.radial_averages = radial_averages
        self.avg_spp = avg_spp
        self.avg_time = avg_time
        
        self.radial_averages.sort(key=lambda ra: ra.mse)
    
    def meanImage(self):
        return self.mean
    
    def sdPpImage(self, config):
        return conversion.colour_mapped(np.sqrt(self.var), 0, config.sdPP_max);

    def n(self):
        return len(self.radial_averages)
    
    def rmse(self):
        mse = 0;
        for d in self.radial_averages:
            mse += d.mse;
        return np.sqrt(mse / self.n())
    
    def rmseSD(self):
        aggr = image.OnlineAvgAndVar(1, 1, 1)
        for d in self.radial_averages:
            aggr.update(np.full((1, 1, 1), np.sqrt(d.mse)))
        
        (mean, var) = aggr.finalize()
        return np.sqrt(var[0, 0, 0]);
    
    def __raMean(self, beginIdx, endIdx):
        beginIdx = int(beginIdx);
        endIdx = int(endIdx);
        raSum = np.zeros_like(self.radial_averages[beginIdx].frequencyError)
        n = 0
        for i in range(beginIdx, endIdx):
            raSum += self.radial_averages[i].frequencyError
            n += 1
        assert n == (endIdx - beginIdx)
        raMean = raSum / (endIdx - beginIdx)
        return raMean
    
    def ensembleMean(self):
        return self.__raMean(0, self.n());
    
    def lowerTail(self, config):
        return self.__raMean(0, config.ensemble_area_lower_tail_body_border * self.n());
    
    def lowerBody(self, config):
        return self.__raMean(config.ensemble_area_lower_tail_body_border * self.n(), config.ensemble_area_lower_body_head_border * self.n());
    
    def lowerHead(self, config):
        return self.__raMean(config.ensemble_area_lower_body_head_border * self.n(), 0.5 * self.n());
    
    def upperHead(self, config):
        return self.__raMean(0.5 * self.n(), config.ensemble_area_upper_head_body_border * self.n());
    
    def upperBody(self, config):
        return self.__raMean(config.ensemble_area_upper_head_body_border * self.n(), config.ensemble_area_upper_body_tail_border * self.n());
    
    def upperTail(self, config):
        return self.__raMean(config.ensemble_area_upper_body_tail_border * self.n(), self.n());
    
    def label(self):
        return f"{self.integrator.upper()} (RMSE: {self.rmse():.3}, s: {self.rmseSD():.3}, t: {self.avg_spp}x{self.avg_time / self.avg_spp:.3}s)"

def normalised_error(shortRendering, reference, avg_time, config):
    e = (shortRendering - reference) * math.sqrt(avg_time)
    if config.error_fun == constants.ERROR_FUN_RELATIVE:
        e /= reference + config.relative_error_eps
    return e

def comp_partial_descriptor(error, config):
    ps = image.powerSpectrum(error)
    ra = image.radial_average(ps)
    mse = np.mean(error * error)
    return RadialAverage(mse, ra)

def comp(scene, integrator, config):
    files = file_handling.files_for(scene, integrator, config)
    shortRenderingMean = np.zeros((512, 512, 3)) 
    avg_spp = 0;
    avg_time = 0;
    for f in files.paths: 
        i = config.imread_fun(f) 
        shortRenderingMean += i
        avg_spp += config.sample_budget_extractor(f)
        avg_time += config.time_budget_extractor(f)
    short_rendering_example = i
        
    shortRenderingMean /= len(files.paths)
    avg_spp /= len(files.paths)
    avg_time /= len(files.paths)
    
    reference = conversion.rgb_to_lum(shortRenderingMean)
    if config.use_external_reference_image:
        reference = conversion.rgb_to_lum(config.reference_image(scene))
    
    radial_averages = []
    shortRenderingVar = np.zeros((512, 512))
    for f in files.paths:
        i = conversion.rgb_to_lum(config.imread_fun(f))
        error = normalised_error(i, reference, avg_time, config)
        shortRenderingVar += error ** 2
        radial_averages.append(comp_partial_descriptor(error, config))
    
    shortRenderingVar /= len(files.paths)
    
    return Descriptor(integrator, short_rendering_example, shortRenderingMean, shortRenderingVar, radial_averages, avg_spp, avg_time);
        
    

    
    
    
        
    