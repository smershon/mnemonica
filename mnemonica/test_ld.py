import load_data as d

d.add_fact('China', 'capital', 'Beijing')
d.add_fact('China', 'neighbor', 'Mongolia')
d.add_fact('China', 'population', 1357380000)
c = d.get_country('China')
print c
