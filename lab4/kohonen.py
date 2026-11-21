import numpy as np
import matplotlib.pyplot as plt
import time

# Исходные данные
X = np.array([
    [9, 6],
    [11, 5],
    [16, -13],
    [-4, -5],
    [18, -10],
    [-16, -4],
    [4, 0],
    [9, 6],
    [-6, -4],
    [8, 5],
    [3, 0],
    [-15, -4],
    [-15, 0],
    [8, 6],
    [-16, -4],
    [-14, -2],
    [16, -13]
], dtype=float)

N_CLUSTERS = 5
EPOCHS = 500

# Min-Max нормировка
X_min = X.min(axis=0)
X_max = X.max(axis=0)
X_norm = (X - X_min) / (X_max - X_min)

def normalize_vector(v):
    """Нормировка весового вектора."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def train_wta(data, fatigue=False, seed=42):
    rng = np.random.default_rng(seed)

    # Случайная инициализация весов
    weights = rng.uniform(0, 1, (N_CLUSTERS, 2))

    for i in range(N_CLUSTERS):
        weights[i] = normalize_vector(weights[i])

    tiredness = np.zeros(N_CLUSTERS)

    start = time.perf_counter()

    for epoch in range(EPOCHS):
        # Уменьшение скорости обучения
        alpha = 0.6 * (0.02 / 0.6) ** (
            epoch / max(EPOCHS - 1, 1)
        )

        indices = rng.permutation(len(data))

        for idx in indices:
            x = data[idx]

            distances = np.linalg.norm(
                weights - x, axis=1
            )

            if fatigue:
                scores = distances + 0.08 * tiredness
                winner = np.argmin(scores)

                # Утомляемость постепенно уменьшается
                tiredness *= 0.97
                tiredness[winner] += 0.15
            else:
                winner = np.argmin(distances)

            # Обновление весов победителя
            weights[winner] += alpha * (
                x - weights[winner]
            )

           

    elapsed = time.perf_counter() - start

    # Определение ближайшего нейрона для каждого объекта
    distances = np.linalg.norm(
        data[:, None, :] - weights[None, :, :],
        axis=2
    )

    labels = np.argmin(distances, axis=1)

    return weights, labels, elapsed

def best_training(data, fatigue=False):
    """Выбор лучшего запуска с непустыми кластерами."""
    best = None
    best_error = float("inf")

    for seed in range(100):
        weights, labels, elapsed = train_wta(
            data, fatigue, seed
        )

        counts = np.bincount(
            labels, minlength=N_CLUSTERS
        )

        if np.any(counts == 0):
            continue

        error = np.sum(
            (data - weights[labels]) ** 2
        )

        if error < best_error:
            best_error = error
            best = (weights, labels, elapsed)

    if best is None:
        raise RuntimeError(
            "Не удалось получить четыре непустых кластера. "
            "Измените число запусков или параметры обучения."
        )

    return best

# Классический WTA
weights_classic, labels_classic, time_classic = (
    best_training(X_norm, fatigue=False)
)

# WTA с утомляемостью
weights_fatigue, labels_fatigue, time_fatigue = (
    best_training(X_norm, fatigue=True)
)

def print_results(name, labels, elapsed):
    print("\n", name)
    print("Время обучения:", round(elapsed, 6), "сек.")

    for k in range(N_CLUSTERS):
        points = X[labels == k]
        print(f"\nКластер {k + 1}:")
        print(points)
        print("Количество объектов:", len(points))

print_results(
    "Классический WTA",
    labels_classic,
    time_classic
)

print_results(
    "WTA с утомляемостью",
    labels_fatigue,
    time_fatigue
)

print("\nСравнение времени:")
print("Классический WTA:", time_classic)
print("WTA с утомляемостью:", time_fatigue)

# Графики
fig, axes = plt.subplots(1, 3, figsize=(17, 5))

colors = ["red", "blue", "green", "orange", "purple"]

# Исходные точки и классический WTA
for k in range(N_CLUSTERS):
    points = X[labels_classic == k]
    axes[0].scatter(
        points[:, 0], points[:, 1],
        color=colors[k], label=f"Кластер {k + 1}"
    )

axes[0].set_title("Классический WTA")
axes[0].set_xlabel("X")
axes[0].set_ylabel("Y")
axes[0].grid()
axes[0].legend()

# Нормированные объекты и веса нейронов
for k in range(N_CLUSTERS):
    points = X_norm[labels_classic == k]
    axes[1].scatter(
        points[:, 0], points[:, 1],
        color=colors[k], label=f"Кластер {k + 1}"
    )

axes[1].scatter(
    weights_classic[:, 0],
    weights_classic[:, 1],
    marker="X", s=180,
    color="black", label="Веса нейронов"
)

axes[1].set_title("Нормированные объекты и веса")
axes[1].set_xlabel("X норм.")
axes[1].set_ylabel("Y норм.")
axes[1].grid()
axes[1].legend()

# Масштабирование весов в исходную систему координат
weights_original = (
    weights_classic * (X_max - X_min) + X_min
)

# Для сопоставления также вычисляем центры кластеров
centers = np.array([
    X[labels_classic == k].mean(axis=0)
    for k in range(N_CLUSTERS)
])

axes[2].scatter(
    X[:, 0], X[:, 1],
    color="gray", label="Исходные объекты"
)

axes[2].scatter(
    weights_original[:, 0],
    weights_original[:, 1],
    marker="X", s=180,
    color="red", label="Масштабированные веса"
)

axes[2].scatter(
    centers[:, 0], centers[:, 1],
    marker="*", s=220,
    color="blue", label="Центры кластеров"
)

axes[2].set_title("Масштабированные веса")
axes[2].set_xlabel("X")
axes[2].set_ylabel("Y")
axes[2].grid()
axes[2].legend()

plt.tight_layout()
plt.savefig("kohonen_results.png", dpi=200)
plt.show()
