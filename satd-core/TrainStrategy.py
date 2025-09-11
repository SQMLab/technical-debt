from enum import Enum


class TrainStrategy(Enum):
    N_SHOT_RANDOM = 'n_shot_random'
    N_SHOT_SIMILAR = 'n_shot_similar'
    N_SHOT_TOP = 'n_shot_top'
    ALL = 'all'
