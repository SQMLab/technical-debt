values = [
    40.28,0.16, 0.39, 1.09, 0.27, 1.40, 2.61, 2.69, 0.17,  0.92,
    1.12, 2.51, 2.46, 0.96, 0.48, 1.79, 1.55, 1.20, 0.92, 5.06,
    0.00, 1.65, 0.00, 0.35, 2.57, 1.14, 6.92, 4.25, 1.17, 0.81,
    1.75, 1.34, 1.85, 0.93, 0.46, 1.42, 1.95, 1.01, 1.01, 0.00,
    1.13, 0.60, 3.01, 5.56, 0.00, 1.30, 2.88, 1.46, 0.74, 0.00,
    6.06, 3.13, 1.57, 0.83, 0.00, 0.00, 0.85, 0.86, 2.63, 0.00,
    0.93, 1.87, 0.95, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00,
    7.61, 2.20, 0.00, 1.12, 1.12, 0.00, 1.18, 0.00, 2.53, 2.70,
    0.00, 1.35, 4.11, 1.37, 0.00, 0.00, 0.00, 0.00, 3.45, 0.00,
    0.00, 7.41, 0.00, 1.89, 1.92, 0.00, 0.00, 4.00, 0.00
]

print(sum(values) / len(values))
print(sum(values[1:]) / len(values[1:]))


from collections import Counter

# List of categories to group and count
x = [
    "requirement", "how-to", "refactor", "superficial-test", "temporary-fix", "requirement", "defect", "requirement",
    "requirement", "requirement", "refactor", "how-to", "skip-test", "how-to", "refactor", "superficial-test",
    "temporary-fix", "requirement", "dependency", "requirement", "requirement", "requirement", "requirement",
    "requirement", "requirement", "code", "requirement", "requirement", "requirement", "requirement", "build",
    "requirement", "requirement", "requirement", "requirement", "requirement", "requirement", "requirement", "code",
    "requirement", "requirement", "requirement", "requirement", "requirement", "requirement", "requirement", "requirement",
    "requirement", "refactor", "requirement", "how-to", "how-to", "subset-test", "defect", "requirement", "requirement",
    "requirement", "defect", "requirement", "superficial-test", "requirement", "requirement", "temporary-fix",
    "requirement", "skip-test", "requirement", "requirement", "dependency", "requirement", "how-to", "temporary-fix",
    "temporary-fix", "requirement", "requirement", "refactor", "skip-test", "requirement", "requirement", "requirement",
    "requirement", "code", "requirement", "code", "requirement", "requirement", "requirement", "temporary-fix",
    "requirement", "requirement", "requirement", "requirement", "requirement", "skip-test", "requirement", "skip-test",
    "how-to", "requirement", "requirement", "requirement", "requirement", "requirement", "how-to", "requirement",
    "temporary-fix", "dependency", "requirement", "documentation", "defect", "requirement", "temporary-fix", "requirement",
    "requirement", "requirement", "skip-test", "dependency", "build", "requirement", "requirement", "documentation",
    "requirement", "requirement", "requirement", "requirement", "requirement", "requirement", "code", "requirement",
    "requirement", "requirement", "requirement", "skip-test", "temporary-fix", "build", "code", "skip-test", "skip-test",
    "temporary-fix", "requirement", "temporary-fix", "requirement", "temporary-fix", "defect", "defect", "defect",
    "requirement", "requirement", "requirement", "requirement", "requirement", "subset-test", "requirement",
    "impractical-case", "defect", "requirement", "dependency", "temporary-fix", "skip-test", "requirement",
    "requirement", "documentation", "requirement", "skip-test", "requirement", "how-to", "refactor", "requirement",
    "requirement", "defect", "defect", "requirement", "requirement", "defect", "requirement", "requirement",
    "requirement", "requirement", "defect", "requirement", "requirement", "requirement", "how-to", "temporary-fix",
    "requirement", "requirement", "requirement", "requirement", "requirement", "how-to", "requirement", "requirement",
    "requirement", "how-to", "requirement", "requirement", "how-to", "requirement", "requirement", "temporary-fix",
    "requirement", "dependency", "temporary-fix", "requirement", "requirement", "requirement", "requirement",
    "multi", "how-to", "requirement", "requirement", "temporary-fix", "dependency", "requirement", "dependency",
    "skip-test", "requirement", "defect", "requirement", "requirement", "requirement", "defect", "defect", "how-to",
    "requirement", "requirement", "requirement", "how-to", "requirement", "requirement", "requirement", "requirement",
    "requirement", "requirement", "requirement", "temporary-fix", "requirement", "requirement", "refactor", "code",
    "superficial-test", "requirement", "code", "refactor", "how-to", "requirement", "requirement", "requirement",
    "requirement", "defect", "requirement", "skip-test", "skip-test", "requirement", "requirement", "defect", "defect",
    "requirement", "skip-test", "multi", "requirement", "superficial-test", "documentation", "requirement", "defect",
    "refactor", "requirement", "multi", "requirement", "requirement", "how-to", "requirement", "temporary-fix", "defect",
    "requirement", "requirement", "requirement", "requirement", "how-to", "dependency", "refactor", "how-to", "requirement",
    "skip-test", "requirement", "requirement", "requirement", "requirement", "temporary-fix"
]
y = [
    "requirement", "requirement", "defect", "requirement", "requirement", "requirement", "how-to", "how-to",
    "requirement", "dependency", "skip-test", "requirement", "requirement", "skip-test", "defect", "requirement",
    "requirement", "defect", "superficial-test", "requirement", "requirement", "temporary-fix", "requirement",
    "requirement", "requirement", "requirement", "requirement", "code", "temporary-fix", "requirement", "requirement",
    "how-to", "dependency", "requirement", "defect", "how-to", "requirement", "superficial-test", "requirement",
    "requirement", "temporary-fix", "defect", "defect", "defect", "requirement", "code", "requirement", "temporary-fix",
    "documentation", "requirement", "requirement", "requirement", "requirement", "requirement", "how-to", "requirement",
    "requirement", "requirement", "requirement", "requirement", "how-to", "requirement", "defect", "defect", "how-to",
    "superficial-test", "requirement", "requirement", "requirement", "defect", "requirement", "requirement", "requirement",
    "requirement", "requirement", "how-to", "defect", "requirement", "requirement", "superficial-test", "impractical-case",
    "temporary-fix", "temporary-fix", "temporary-fix", "requirement", "requirement", "requirement", "requirement",
    "requirement", "temporary-fix", "design", "requirement", "temporary-fix", "requirement", "requirement", "requirement",
    "requirement", "requirement", "how-to", "requirement", "requirement", "requirement", "temporary-fix", "requirement",
    "requirement", "how-to", "impractical-case", "requirement", "requirement", "defect", "how-to", "temporary-fix",
    "requirement", "defect", "requirement", "requirement", "how-to", "requirement", "documentation", "requirement",
    "requirement", "requirement", "temporary-fix", "requirement", "requirement", "requirement", "requirement", "requirement",
    "requirement", "how-to", "dependency", "requirement", "requirement", "how-to", "requirement", "requirement", "defect",
    "defect", "requirement", "requirement", "requirement", "temporary-fix", "dependency", "skip-test", "requirement",
    "requirement", "requirement", "temporary-fix", "requirement", "temporary-fix", "code", "requirement", "requirement",
    "skip-test", "requirement", "requirement", "requirement", "requirement", "requirement", "superficial-test", "requirement",
    "documentation", "requirement", "requirement", "how-to", "requirement", "requirement", "superficial-test", "requirement",
    "requirement", "temporary-fix", "impractical-case", "code", "build", "temporary-fix", "requirement", "requirement",
    "requirement", "requirement", "skip-test", "skip-test", "requirement", "requirement", "defect", "requirement",
    "requirement", "refactor", "requirement", "requirement", "requirement", "requirement", "requirement", "requirement",
    "temporary-fix", "documentation", "requirement", "code", "requirement", "requirement", "requirement", "requirement",
    "requirement", "requirement", "skip-test", "requirement", "temporary-fix", "requirement", "requirement", "requirement",
    "requirement", "requirement", "superficial-test", "requirement", "documentation", "temporary-fix", "how-to", "requirement",
    "how-to", "requirement", "superficial-test", "impractical-case", "requirement", "dependency", "requirement",
    "requirement", "requirement", "impractical-case", "requirement", "requirement", "defect", "how-to", "requirement",
    "requirement", "requirement", "requirement", "how-to", "requirement", "multi", "impractical-case", "design", "requirement",
    "how-to", "requirement", "code", "requirement", "requirement", "requirement", "requirement", "requirement", "requirement",
    "requirement", "requirement", "requirement", "requirement", "documentation", "requirement", "requirement", "requirement",
    "requirement", "requirement", "temporary-fix", "requirement", "how-to", "defect", "how-to", "requirement", "requirement",
    "requirement", "requirement", "requirement", "requirement", "temporary-fix", "requirement", "requirement", "defect",
    "requirement", "impractical-case", "requirement", "requirement", "requirement", "code", "requirement", "defect",
    "requirement", "requirement", "requirement", "requirement", "requirement", "dependency", "requirement", "requirement"
]

s = {}
for arr in [x, y]:
    for c in arr:
        if c in s:
            s[c] += 1
        else:
            s[c] = 1
print(s)
