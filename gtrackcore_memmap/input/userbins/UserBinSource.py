from gtrackcore_memmap.core.DataTypes import getSupportedFileSuffixesForBinning
from gtrackcore_memmap.input.wrappers.GESorter import GESorter
from gtrackcore_memmap.util.CommonFunctions import parseRegSpec, parseShortenedSizeSpec, \
                                        convertTNstrToTNListFormat
from gtrackcore_memmap.util.CustomExceptions import ShouldNotOccurError
    
class UserBinSource(object):
    '''Possible definitions of UserBinSource, based on (regSpec,binSpec)-tuple:
    ('file',fn) where instead of 'file', a more specific filetype such as 'bed' could be specified
    (chrReg,binSize) where chrReg is a Region specification as in UCSC Genome browser (string), or '*' to denote whole genome, and where binSize is a number specifying length of each bin that the region should be split into.
    '''
    def __new__(cls, regSpec, binSpec, genome=None, categoryFilterList=None, strictMatch=True, includeExtraChrs = False): #,fileType):
        if regSpec in ['file', 'track'] + getSupportedFileSuffixesForBinning():
            #if fileType != 'bed':
            #    raise NotImplementedError
            
            assert genome is not None
            
            from gtrackcore_memmap.input.core.GenomeElementSource import GenomeElementSource
            if regSpec == 'file':
                geSource = GenomeElementSource(binSpec, genome=genome)
            elif regSpec == 'track':
                from gtrackcore_memmap.input.adapters.TrackGenomeElementSource import FullTrackGenomeElementSource
                trackName = convertTNstrToTNListFormat(binSpec)
                geSource = FullTrackGenomeElementSource(genome, trackName, allowOverlaps=False)
            else:
                geSource = GenomeElementSource(binSpec, genome=genome, suffix=regSpec)
            
            if categoryFilterList is not None:
                from gtrackcore_memmap.input.wrappers.GECategoryFilter import GECategoryFilter
                geSource = GECategoryFilter(geSource, categoryFilterList, strict=strictMatch)
            return cls._applyEnvelope(geSource)
        else:
            if binSpec == '*':
                binSize = None
            else:
                binSize = parseShortenedSizeSpec(binSpec)
            
            from gtrackcore_memmap.input.userbins.AutoBinner import AutoBinner
            return AutoBinner(parseRegSpec(regSpec, genome, includeExtraChrs=includeExtraChrs), binSize)
    
    @staticmethod
    def _applyEnvelope(geSource):
        from gtrackcore_memmap.input.wrappers.GERegionBoundaryFilter import GERegionBoundaryFilter
        from gtrackcore_memmap.input.wrappers.GEOverlapClusterer import GEOverlapClusterer
        return GERegionBoundaryFilter(GEOverlapClusterer(GESorter(geSource)), GlobalBinSource(geSource.genome))

class UnBoundedUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from gtrackcore_memmap.input.wrappers.GEOverlapClusterer import GEOverlapClusterer
        return GEOverlapClusterer(GESorter(geSource))

class UnBoundedUnClusteredUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        return GESorter(geSource)
        
class ValuesStrippedUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from gtrackcore_memmap.input.wrappers.GEMarkRemover import GEMarkRemover
        return GESorter(GEMarkRemover(geSource))

class BoundedUnClusteredUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        from gtrackcore_memmap.input.wrappers.GERegionBoundaryFilter import GERegionBoundaryFilter
        return GERegionBoundaryFilter(GESorter(geSource), GlobalBinSource(geSource.genome) )

class UnfilteredUserBinSource(UserBinSource):
    @staticmethod
    def _applyEnvelope(geSource):
        return geSource
    
class GlobalBinSource(object):
    def __new__(cls, genome):
        return UserBinSource(genome+':*','*')
    
class MinimalBinSource(object):
    def __new__(cls, genome):
        from gtrackcore_memmap.track.core.GenomeRegion import GenomeRegion
        from gtrackcore_memmap.metadata.GenomeInfo import GenomeInfo
        chrList = GenomeInfo.getChrList(genome)
        if len(chrList) > 0:
            return [GenomeRegion(genome, GenomeInfo.getChrList(genome)[0], 0, 1)]
