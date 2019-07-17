'''
Documentation, License etc.

@package compute_descriptors
'''

import numpy as np

import conversion
import image
import file_handling

class RadialAverage:
    def __init__(self, mse, frequencyError):
        self.mse = mse
        self.frequencyError = frequencyError
    
        
class Descriptor:
    def __init__(self, integrator, mean, var, radial_averages, avg_spp, avg_time):
        self.integrator = integrator
        self.mean = mean
        self.var = var
        self.radial_averages = radial_averages
        self.avg_spp = avg_spp
        self.avg_time = avg_time
        
        self.radial_averages.sort(key=lambda ra: ra.mse)
    
    def meanImage(self):
        return self.mean
    
    def sdPpImage(self, config):
        return conversion.colour_mapped(conversion.rgb_to_lum(np.sqrt(self.var)), 0, config.sdPP_max);

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
        return f"{self.integrator.upper()} (RMSE: {self.rmse():.3}, s: {self.rmseSD():.3}, t: {self.avg_spp}x{self.avg_time:.3}s)"

def comp_partial_descriptor(shortRendering, reference, config):
    e = config.error_fun(shortRendering, reference)
    ps = image.powerSpectrum(e)
    ra = image.radial_average(ps)
    e *= e
    mse = np.mean(e)
    return RadialAverage(mse, ra)

def comp(scene, integrator, config):
    files = file_handling.files_for(scene, integrator, config)
    aggr = image.OnlineAvgAndVar(512, 512, 3) 
    for f in files.paths: 
        i = config.imread_fun(f) 
        aggr.update(i)
    (mean, var) = aggr.finalize()
    
    reference = mean
    if config.use_external_reference_image:
        reference = config.reference_image(scene)
    
    
    radial_averages = []
    avg_spp = 0;
    avg_time = 0;
    for f in files.paths:
        avg_spp += config.sample_budget_extractor(f)
        avg_time += config.time_budget_extractor(f)
        i = config.imread_fun(f)
        radial_averages.append(comp_partial_descriptor(i, reference, config))
    
    avg_spp /= len(files.paths)
    avg_time /= len(files.paths)
    
    return Descriptor(integrator, mean, var, radial_averages, avg_spp, avg_time);
        
    

    
    
    
        
    