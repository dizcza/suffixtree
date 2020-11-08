from dataclasses import dataclass
from networkx import write_gml, write_graphml
from suffixtree import SuffixTree


@dataclass
class Point:
    lat: float
    lon: float

    def __hash__(self) -> int:
        return hash((self.lat, self.lon))

    def __eq__(self, o: object) -> bool:
        return self.__hash__() == o.__hash__()

    def __str__(self) -> str:
        return f'{self.lat},{self.lon}'


s = SuffixTree()
s.generate(
    (
        Point(1,1),
        Point(1,0),
        Point(0,1),
        Point(1,1),
        Point(1,0),
        Point(0,0),
    )
)
# s.generate('MISSISSIPPI$')

# annotate graph for vizualization
for i in range(1, s.order()):
    parent = s.parent_id(i)
    edge = s[parent][i]
    edge['label'] = s.label(edge)

write_gml(s, r'example.gml')
write_graphml(s, r'example.graphml')