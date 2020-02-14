from Pccompound import Pccompound
class Ensemble_pccompound:
    """This class represent an ensembl of Pccompound objects, it's composed of:
    - a list of cid
    - a size attribute
    - a corresponding list of Pccompound objects
    """
    def __init__(self, pccompound_list):
        self.cid_list = [Pccompound.get_cid(pc) for pc in pccompound_list]
        self.size = len(pccompound_list)
        self.pccompound_list = pccompound_list