import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

from suffixtree import SuffixTree


st = SuffixTree()
st.generate(r'1001000100$')
g = st.to_nx()

edge_labels = {(u, v): d['label'] for u, v, d in st.edges(data=True)}

pos = graphviz_layout(g, prog="dot")
nx.draw_networkx(g, pos)
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
plt.show()
