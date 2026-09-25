from __future__ import annotations

PLANTS = {
    "aloe-vera": {
        "common_name": "Aloe vera", "scientific_name": "Aloe vera", "family": "Asphodelaceae", "sunlight": "Mucho sol",
        "watering": "Bajo", "placement": "Interior/Exterior", "plant_type": "Suculenta"
    },
    "monstera-deliciosa": {
        "common_name": "Monstera deliciosa", "scientific_name": "Monstera deliciosa", "family": "Araceae", "sunlight": "Luz indirecta",
        "watering": "Medio", "placement": "Interior", "plant_type": "Tropical"
    },
    "dracaena-trifasciata": {
        "common_name": "Lengua de suegra", "scientific_name": "Dracaena trifasciata", "family": "Asparagaceae", "sunlight": "Luz indirecta",
        "watering": "Bajo", "placement": "Interior", "plant_type": "Follaje"
    },
    "lavandula-angustifolia": {
        "common_name": "Lavanda", "scientific_name": "Lavandula angustifolia", "family": "Lamiaceae", "sunlight": "Mucho sol",
        "watering": "Bajo", "placement": "Exterior", "plant_type": "Aromática"
    },
    "salvia-rosmarinus": {
        "common_name": "Romero", "scientific_name": "Salvia rosmarinus", "family": "Lamiaceae", "sunlight": "Mucho sol",
        "watering": "Bajo", "placement": "Exterior", "plant_type": "Aromática"
    },
    "epipremnum-aureum": {
        "common_name": "Poto", "scientific_name": "Epipremnum aureum", "family": "Araceae", "sunlight": "Luz indirecta",
        "watering": "Medio", "placement": "Interior", "plant_type": "Trepadora"
    },
    "zamioculcas-zamiifolia": {
        "common_name": "Zamioculca", "scientific_name": "Zamioculcas zamiifolia", "family": "Araceae", "sunlight": "Sombra parcial",
        "watering": "Bajo", "placement": "Interior", "plant_type": "Follaje"
    },
    "spathiphyllum-wallisii": {
        "common_name": "Cuna de Moisés", "scientific_name": "Spathiphyllum wallisii", "family": "Araceae", "sunlight": "Sombra parcial",
        "watering": "Medio", "placement": "Interior", "plant_type": "Floración"
    },
    "chlorophytum-comosum": {
        "common_name": "Mala madre", "scientific_name": "Chlorophytum comosum", "family": "Asparagaceae", "sunlight": "Luz indirecta",
        "watering": "Medio", "placement": "Interior", "plant_type": "Follaje"
    },
    "crassula-ovata": {
        "common_name": "Árbol de jade", "scientific_name": "Crassula ovata", "family": "Crassulaceae", "sunlight": "Mucho sol",
        "watering": "Bajo", "placement": "Interior/Exterior", "plant_type": "Suculenta"
    },
    "ficus-lyrata": {
        "common_name": "Ficus lyrata", "scientific_name": "Ficus lyrata", "family": "Moraceae", "sunlight": "Luz indirecta",
        "watering": "Medio", "placement": "Interior", "plant_type": "Árbol de interior"
    },
    "calathea-orbifolia": {
        "common_name": "Calathea orbifolia", "scientific_name": "Goeppertia orbifolia", "family": "Marantaceae", "sunlight": "Sombra parcial",
        "watering": "Frecuente", "placement": "Interior", "plant_type": "Tropical"
    },
}

BASE_RATINGS = {
    "aloe-vera": [5, 5, 4, 5, 4, 5],
    "monstera-deliciosa": [5, 4, 5, 5, 5, 4],
    "dracaena-trifasciata": [5, 5, 5, 4, 5, 5],
    "lavandula-angustifolia": [4, 5, 4, 4, 5],
    "salvia-rosmarinus": [5, 4, 5, 4, 4],
    "epipremnum-aureum": [5, 5, 4, 5, 5],
    "zamioculcas-zamiifolia": [5, 4, 5, 5, 4],
    "spathiphyllum-wallisii": [4, 4, 5, 3, 4],
    "chlorophytum-comosum": [5, 4, 4, 5, 5],
    "crassula-ovata": [5, 5, 4, 5, 4],
    "ficus-lyrata": [4, 4, 3, 5, 4],
    "calathea-orbifolia": [4, 3, 4, 4, 5],
}

COMMENTS = [
    "Llegó en buen estado y bien protegida.",
    "El tamaño corresponde con la descripción.",
    "Buena relación entre precio y presentación.",
    "La planta se adaptó bien después de unos días.",
    "Empaque correcto; volvería a comprar.",
    "La condición general fue buena al recibirla.",
]

REVIEWS = []
review_counter = 1
for product_id, ratings in BASE_RATINGS.items():
    for i, rating in enumerate(ratings):
        REVIEWS.append({
            "review_id": f"R{review_counter:04d}",
            "product_id": product_id,
            "rating": rating,
            "comment": COMMENTS[i % len(COMMENTS)],
            "created_at": f"2026-09-{10 + (i % 10):02d}T12:00:00Z",
        })
        review_counter += 1
