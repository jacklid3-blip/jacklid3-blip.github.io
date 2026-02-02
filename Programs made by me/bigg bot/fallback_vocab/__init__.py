"""
Fallback vocabulary modules - Split for faster loading and maintainability
"""

from .questions import QUESTIONS
from .entertainment import ENTERTAINMENT
from .food import FOOD
from .sports import SPORTS
from .technology import TECHNOLOGY
from .science import SCIENCE
from .nature import NATURE
from .life_emotions import LIFE_EMOTIONS
from .travel import TRAVEL
from .work import WORK
from .misc import MISC
from .fnaf import FNAF


def get_all_responses():
    """Merge all vocabulary dictionaries into one"""
    all_responses = {}
    all_responses.update(QUESTIONS)
    all_responses.update(ENTERTAINMENT)
    all_responses.update(FOOD)
    all_responses.update(SPORTS)
    all_responses.update(TECHNOLOGY)
    all_responses.update(SCIENCE)
    all_responses.update(NATURE)
    all_responses.update(LIFE_EMOTIONS)
    all_responses.update(TRAVEL)
    all_responses.update(WORK)
    all_responses.update(MISC)
    all_responses.update(FNAF)
    return all_responses
