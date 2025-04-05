import matplotlib.pyplot as plt

# Data
labels = [
    '>10,000 comments (45)',
    '1,000–10,000 comments (140)',
    '<1,000 comments (497)',
    'No test comments (318)'
]
sizes = [45, 140, 497, 318]
colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3']

# Plot
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title('')
plt.axis('equal')
plt.tight_layout()
plt.show()

