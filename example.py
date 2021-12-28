import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

from suffixtree import SuffixTree

s = [1, 0, 0] * 6
s = list(s)
s[1] = 1 - s[1]
s[4] = 1 - s[4]
s = ''.join(map(str, s))
s = '101010100100'
# s = '100100'
s = 'ABBABBBABB'

st = SuffixTree()
st.generate(s + '$')
g = st.to_nx()

edge_labels = {(u, v): d['label'] for u, v, d in g.edges(data=True)}

pos = graphviz_layout(g, prog="dot")
nx.draw_networkx(g, pos)
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
plt.show()
