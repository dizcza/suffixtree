import random
from dataclasses import dataclass, field
from typing import List, Dict, Hashable, Union
from networkx import DiGraph


@dataclass
class Node:
    id: int
    link: Dict = field(default_factory=dict)

    def __hash__(self):
        return self.id.__hash__()

    def __str__(self) -> str:
        return str(self.id)


class SuffixTree(DiGraph):
    ROOT = 0

    def __init__(self):
        super().__init__()
        self.add_node(Node(self.ROOT))

    @property
    def last_node_id(self):
        return self.order() - 1

    def add_node(self, node: Node):
        super().add_node(node.id, data=node)

    def get_node(self, id: int) -> Node:
        return self.nodes[id]['data']

    def parent_id(self, id: int) -> Union[int, None]:
        return next(self.predecessors(id), None)

    def child_id(self, parent_id: int, alpha: Hashable) -> int:
        """Returns child node by first letter (alpha) in sequence on edge from parent"""
        return next(
            filter(
                lambda x: self[parent_id][x].get('alpha') == alpha,
                self[parent_id]),
            None)

    def label(self, edge):
        """Return label corresponding to an edge"""
        if not self._seq:
            return None
        return self._seq[edge['pos'] - edge['length']:edge['pos']]

    def length(self, node_id: int) -> int:
        """Return length of path from root to a node with node_id

        Args:
            node_id (int): id of the end node

        Returns:
            int: length
        """
        l = 0
        while node_id != 0:
            parent = self.parent_id(node_id)
            l += self.edges[parent, node_id]['length']
            node_id = parent
        return l

    def path(self, node_id):
        path = []
        while node_id != 0:
            parent = self.parent_id(node_id)
            label = self.label(self.edges[parent, node_id])
            label.reverse()
            path += label
            node_id = parent
        path.reverse()
        return path

    def link(self, id: int, alpha: Hashable) -> int:
        """Get alpha prefix link of a node"""
        return self.get_node(id).link.get(alpha)

    def attach(self, parent: Node, child: Node, alpha: Hashable, length: int,
               pos: int):
        """Attach new node to tree

        Args:
            parent (Node): parent node to attach
            child (Node): new node
            alpha (Hashable): first element of edge label
            length (int): an edge label's length
            pos (int): next position after edge label in source sequence
        """
        self.add_node(child)
        self.add_edge(
            parent.id, child.id,
            alpha=alpha, length=length, pos=pos
        )

    def split_edge(self, parent: Node, child: Node, edge: Dict,
                   counter: int) -> Node:
        """Split an edge to insert new node

        Args:
            parent (Node): [description]
            child (Node): [description]
            edge (Dict): [description]
            counter (int): [description]

        Returns:
            Node: new node
        """
        new_node = Node(self.order())
        # attach w_ to parent
        self.attach(
            self.get_node(parent), new_node, edge['alpha'],
            counter, edge['pos'] - edge['length'] + counter
        )
        # attach u to w_ (edge from w_ to child)
        self.attach(
            new_node, self.get_node(child),
            self._seq[edge['pos'] - edge['length'] + counter],
            edge['length'] - counter, edge['pos']
        )
        # delete old edge
        self.remove_edge(parent, child)
        return new_node

    def extend(self, start, suffix: List[Hashable]):
        path = []  # stack of passed edges
        v = old = self.last_node_id
        vlen = len(suffix)
        w = None
        # Looking for a vertex from last added node to root with prefix link sub[0]
        while not w:
            parent_v = self.parent_id(v)
            if parent_v is None:  # special case when w is ROOT
                w = self.ROOT
                vlen = 0
                break
            vlen -= self[parent_v][v]['length']
            path.append((parent_v, self[parent_v][v]))  # put to stack
            v = parent_v
            w = self.link(v, suffix[0])
        u = self.child_id(w, suffix[vlen])
        if u:  # if True we must split an edge first
            edge_wu = self[w][u]
            seq_wu = self.label(edge_wu)
            j = 1 if w == self.ROOT else 0  # check if root case
            while path[-1][1]['alpha'] == seq_wu[j]:
                j += path[-1][1]['length']
                path.pop()  # remove edge from stack
            node_w_ = self.split_edge(w, u, edge_wu, j)
            vlen += self[w][node_w_.id]['length']
            self.get_node(path[-1][0]).link[suffix[0]] = w = node_w_.id
        # Create new leaf from w_
        length_leaf = len(suffix) - vlen
        pos_leaf = len(self._seq)
        leaf_node = Node(self.order())
        self.attach(
            self.get_node(w),
            leaf_node, suffix[-length_leaf],
            length_leaf, pos_leaf
        )
        leaf_node.start = start
        # Create prefix link from old to the new leaf
        self.get_node(old).link[suffix[0]] = leaf_node.id

    def generate(self, sequence: List[Hashable], progress: bool = True):
        self._seq = sequence
        range_ = range(1, len(sequence) + 1)
        if progress:
            from tqdm import tqdm
            range_ = tqdm(range_)
        for i in range_:
            sub = sequence[-i:]
            self.extend(len(sequence) - i, sub)

    def to_nx(self):
        g = DiGraph()
        for u, v, d in self.edges(data=True):
            d['label'] = self.label(d)
            if self.out_degree(v) == 0:
                v = f"{v}:{self.nodes[v]['data'].start}"
            g.add_edge(u, v, **d)
        return g
