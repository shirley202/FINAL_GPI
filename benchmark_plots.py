import json
import numpy as np
import matplotlib.pyplot as plt

# ===========================
# Cargar resultados guardados
# ===========================
# Este archivo será generado automáticamente por benchmark.py
RESULT_FILE = "benchmark_results.json"

with open(RESULT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

prec_tfidf = np.array(data["prec_tfidf"])
prec_dense = np.array(data["prec_dense"])
prec_hybrid = np.array(data["prec_hybrid"])

mrr_tfidf = np.array(data["mrr_tfidf"])
mrr_dense = np.array(data["mrr_dense"])
mrr_hybrid = np.array(data["mrr_hybrid"])

labels = ["TF-IDF", "Denso", "Híbrido"]


# ===========================
# A) Gráfica Precision@3
# ===========================
plt.figure(figsize=(8, 5))
values = [np.mean(prec_tfidf), np.mean(prec_dense), np.mean(prec_hybrid)]
plt.bar(labels, values, color=["red", "orange", "green"])
plt.title("Comparación de Precision@3")
plt.ylabel("Precisión promedio")
plt.ylim(0, 1)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.savefig("precision_at_3.png")
plt.close()


# ===========================
# B) Gráfica MRR
# ===========================
plt.figure(figsize=(8, 5))
values = [np.mean(mrr_tfidf), np.mean(mrr_dense), np.mean(mrr_hybrid)]
plt.bar(labels, values, color=["red", "orange", "green"])
plt.title("Comparación de MRR (Mean Reciprocal Rank)")
plt.ylabel("MRR promedio")
plt.ylim(0, 1)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.savefig("mrr_comparison.png")
plt.close()


# ===========================
# C) Radar Chart (Comparación Global)
# ===========================
metrics = ["Precision@3", "MRR"]
angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
angles += angles[:1]  # cerrar el radar

def radar_values(values):
    values = values.tolist()
    values += values[:1]
    return values

tfidf_values = radar_values([np.mean(prec_tfidf), np.mean(mrr_tfidf)])
dense_values = radar_values([np.mean(prec_dense), np.mean(mrr_dense)])
hybrid_values = radar_values([np.mean(prec_hybrid), np.mean(mrr_hybrid)])

plt.figure(figsize=(6, 6))
ax = plt.subplot(111, polar=True)

plt.xticks(angles[:-1], metrics)

ax.plot(angles, tfidf_values, label="TF-IDF", color="red")
ax.fill(angles, tfidf_values, alpha=0.1, color="red")

ax.plot(angles, dense_values, label="Denso", color="orange")
ax.fill(angles, dense_values, alpha=0.1, color="orange")

ax.plot(angles, hybrid_values, label="Híbrido", color="green")
ax.fill(angles, hybrid_values, alpha=0.1, color="green")

plt.title("Comparación de Modelos en 2 Métricas")
plt.legend(loc="upper right")
plt.savefig("radar_comparison.png")
plt.close()

print("\n✔ Gráficas generadas con éxito:")
print(" - precision_at_3.png")
print(" - mrr_comparison.png")
print(" - radar_comparison.png\n")
