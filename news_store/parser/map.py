from .finviz import FinvizParser
from .reuters import ReutersParser
from .wsj import WSJParser

PARSER_MAP = {'Finviz': FinvizParser,
              'Reuters': ReutersParser,
              'WSJ': WSJParser}
