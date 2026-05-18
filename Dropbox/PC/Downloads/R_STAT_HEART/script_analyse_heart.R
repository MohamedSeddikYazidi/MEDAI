# =============================================================================
# MINI-PROJET – ANALYSE MULTIVARIÉE
# Dataset : Heart Disease (UCI / Kaggle)
# Module  : Méthodes statistiques et étude de données
# Par: Achref Boukadi et Mohamed Seddik Yazidi
# =============================================================================

# -----------------------------------------------------------------------------
# 0. CHARGEMENT DES PACKAGES
# -----------------------------------------------------------------------------

library(tidyverse)    # manipulation & visualisation
library(FactoMineR)   # ACP, AFC, ACM
library(factoextra)   # visualisation des méthodes factorielles
library(cluster)      # classification (K-means, CAH, silhouette)
library(ggplot2)      # graphiques
library(corrplot)     # matrice de corrélation
library(gridExtra)    # disposition des graphiques
library(dendextend)   # dendrogrammes stylisés
library(knitr)        # tableaux
library(conflicted)

# -----------------------------------------------------------------------------
# 1. CHARGEMENT ET EXPLORATION INITIALE
# -----------------------------------------------------------------------------

heart <- read.csv("heart.csv")

# Dimensions
dim(heart)        # 1025 lignes, 14 colonnes
head(heart)       # aperçu
str(heart)        # types de variables
summary(heart)    # statistiques descriptives

# Distribution de la variable cible
table(heart$target)           # 499 sains (0), 526 malades (1)
prop.table(table(heart$target)) # proportions (~50/50)

# -----------------------------------------------------------------------------
# 2. PRÉPARATION DES DONNÉES
# -----------------------------------------------------------------------------

## 2.1 Valeurs manquantes et doublons
sum(is.na(heart))           # 0 valeur manquante
sum(duplicated(heart))      # vérification des doublons

heart_clean <- heart %>% distinct()  # suppression des doublons éventuels
dim(heart_clean)

## 2.2 Détection des outliers (boxplots visuels)
vars_cont <- c("age", "trestbps", "chol", "thalach", "oldpeak")

heart_clean %>%
  select(all_of(vars_cont)) %>%
  pivot_longer(everything(), names_to = "variable", values_to = "valeur") %>%
  ggplot(aes(x = variable, y = valeur, fill = variable)) +
  geom_boxplot(alpha = 0.8, outlier.colour = "red") +
  labs(title = "Détection des outliers") +
  theme_minimal() + theme(legend.position = "none")

## 2.3 Winsorisation (traitement des outliers extrêmes)
winsorize <- function(x, probs = c(0.01, 0.99)) {
  bounds <- quantile(x, probs, na.rm = TRUE)
  pmin(pmax(x, bounds[1]), bounds[2])
}

heart_clean <- heart_clean %>%
  mutate(
    chol     = winsorize(chol),
    trestbps = winsorize(trestbps),
    oldpeak  = winsorize(oldpeak)
  )

## 2.4 Recodage des variables catégorielles (pour analyses descriptives)
heart_labeled <- heart_clean %>%
  mutate(
    sex_f     = factor(sex,     labels = c("Femme","Homme")),
    cp_f      = factor(cp,      labels = c("Asymptomatique","Angine atypique",
                                            "Douleur non-anginale","Angine typique")),
    fbs_f     = factor(fbs,     labels = c("Non","Oui")),
    exang_f   = factor(exang,   labels = c("Non","Oui")),
    target_f  = factor(target,  labels = c("Sain","Malade"))
  )

## 2.5 Normalisation (Z-score) pour ACP et clustering
# On retient les 6 variables numériques continues
vars_num <- c("age", "trestbps", "chol", "thalach", "oldpeak", "ca")

heart_scaled <- heart_clean %>%
  select(all_of(vars_num)) %>%
  scale() %>%
  as.data.frame()

# Vérification : moyennes ≈ 0, écarts-types ≈ 1
round(colMeans(heart_scaled), 4)
round(apply(heart_scaled, 2, sd), 4)

## 2.6 Matrice de corrélation
cor_mat <- cor(heart_clean[, vars_num])
corrplot(cor_mat,
         method      = "color",
         type        = "upper",
         addCoef.col = "black",
         tl.col      = "black",
         title       = "Corrélations des variables numériques",
         mar         = c(0,0,2,0))

# -----------------------------------------------------------------------------
# 3. ANALYSE EN COMPOSANTES PRINCIPALES (ACP)
# -----------------------------------------------------------------------------

## 3.1 Calcul de l'ACP
res.pca <- PCA(heart_scaled, graph = FALSE, scale.unit = FALSE)

## 3.2 Valeurs propres et variance expliquée
eig <- get_eigenvalue(res.pca)
print(round(eig, 3))

# Graphique des éboulis
fviz_eig(res.pca, addlabels = TRUE,
         barfill = "#3498DB", barcolor = "white",
         main = "Scree plot – Variance expliquée")

## 3.3 Analyse des variables
# Cercle des corrélations
fviz_pca_var(res.pca,
             col.var = "contrib",
             gradient.cols = c("#00AFBB","#E7B800","#FC4E07"),
             repel   = TRUE,
             title   = "Cercle des corrélations")

# Contributions aux axes
fviz_contrib(res.pca, choice = "var", axes = 1,
             fill = "#3498DB", title = "Contributions – Axe 1")
fviz_contrib(res.pca, choice = "var", axes = 2,
             fill = "#E74C3C", title = "Contributions – Axe 2")

## 3.4 Projection des individus colorés par statut cardiaque
ind_coord <- as.data.frame(res.pca$ind$coord[, 1:2])
ind_coord$target <- factor(heart_clean$target, labels = c("Sain","Malade"))

ggplot(ind_coord, aes(x = Dim.1, y = Dim.2, color = target)) +
  geom_point(alpha = 0.5, size = 1.5) +
  stat_ellipse(aes(fill = target), geom = "polygon", alpha = 0.15) +
  scale_color_manual(values = c("Sain" = "#2ECC71", "Malade" = "#E74C3C")) +
  scale_fill_manual(values  = c("Sain" = "#2ECC71", "Malade" = "#E74C3C")) +
  labs(title = "ACP – Individus selon statut cardiaque",
       x = paste0("Dim 1 (", round(eig[1,2],1),"%)"),
       y = paste0("Dim 2 (", round(eig[2,2],1),"%)")) +
  theme_minimal()

# -----------------------------------------------------------------------------
# 4. CLASSIFICATION NON SUPERVISÉE
# -----------------------------------------------------------------------------

## 4.1 K-MEANS

# Choix du nombre de clusters – méthode du coude
set.seed(42)
fviz_nbclust(heart_scaled, kmeans, method = "wss", k.max = 10,
             linecolor = "#E74C3C") +
  labs(title = "Méthode du coude")

# Choix du nombre de clusters – méthode de la silhouette
fviz_nbclust(heart_scaled, kmeans, method = "silhouette", k.max = 10,
             linecolor = "#3498DB") +
  labs(title = "Méthode de la silhouette")

# Application K-means avec k = 3
set.seed(42)
km3 <- kmeans(heart_scaled, centers = 3, nstart = 25, iter.max = 100)

# Résultats
table(km3$cluster)
cat("Ratio BSS/TSS :", round(km3$betweenss / km3$totss * 100, 1), "%\n")

# Ajout des clusters au dataset
heart_clean$cluster_km <- factor(km3$cluster)

# Visualisation des clusters
fviz_cluster(km3,
             data         = heart_scaled,
             palette      = c("#E74C3C","#2ECC71","#3498DB"),
             geom         = "point",
             ellipse.type = "convex",
             ggtheme      = theme_minimal(),
             main         = "K-means (k=3)")

# Profils des clusters
vars_profil <- c("age","trestbps","chol","thalach","oldpeak","ca")
profils_km <- heart_clean %>%
  group_by(cluster_km) %>%
  summarise(across(all_of(vars_profil), mean),
            n          = n(),
            pct_malade = round(mean(target) * 100, 1))
print(profils_km)

## 4.2 CLASSIFICATION ASCENDANTE HIÉRARCHIQUE (CAH)

# Échantillon pour lisibilité du dendrogramme
set.seed(42)
idx  <- sample(nrow(heart_scaled), 150)
samp <- heart_scaled[idx, ]

# Matrice de distances + CAH Ward
dist_mat   <- dist(samp, method = "euclidean")
res.hclust <- hclust(dist_mat, method = "ward.D2")

# Dendrogramme
dend <- as.dendrogram(res.hclust)
dend %>%
  color_branches(k = 3) %>%
  color_labels(k = 3) %>%
  plot(main = "Dendrogramme CAH (Ward, n=150)", leaflab = "none")
rect.hclust(res.hclust, k = 3,
            border = c("#E74C3C","#2ECC71","#3498DB"))

# Clusters CAH sur l'ensemble complet
cluster_cah_full <- cutree(
  hclust(dist(heart_scaled, method = "euclidean"), method = "ward.D2"),
  k = 3
)
heart_clean$cluster_cah <- factor(cluster_cah_full)
table(cluster_cah_full)

# Visualisation CAH
fviz_cluster(list(data = heart_scaled, cluster = cluster_cah_full),
             palette      = c("#E74C3C","#2ECC71","#3498DB"),
             geom         = "point",
             ellipse.type = "convex",
             ggtheme      = theme_minimal(),
             main         = "CAH (k=3)")

## 4.3 COMPARAISON K-MEANS vs CAH
table(KMeans = heart_clean$cluster_km,
      CAH    = heart_clean$cluster_cah)

# -----------------------------------------------------------------------------
# 5. ANALYSE COMBINÉE – ACP + CLASSIFICATION
# -----------------------------------------------------------------------------

biplot_data <- as.data.frame(res.pca$ind$coord[, 1:2])
biplot_data$cluster <- heart_clean$cluster_km
biplot_data$target  <- factor(heart_clean$target, labels = c("Sain","Malade"))

ggplot(biplot_data, aes(x = Dim.1, y = Dim.2,
                         color = cluster, shape = target)) +
  geom_point(alpha = 0.6, size = 2) +
  stat_ellipse(aes(group = cluster, color = cluster),
               type = "t", linetype = "dashed", size = 1) +
  scale_color_manual(values = c("1"="#E74C3C","2"="#2ECC71","3"="#3498DB")) +
  scale_shape_manual(values = c("Sain"=1,"Malade"=16)) +
  labs(title = "ACP + K-means : vue combinée",
       x = paste0("Dim 1 (", round(eig[1,2],1),"%)"),
       y = paste0("Dim 2 (", round(eig[2,2],1),"%)"),
       color = "Cluster", shape = "Statut") +
  theme_minimal()

# -----------------------------------------------------------------------------
# 6. INTERPRÉTATION DES PROFILS
# -----------------------------------------------------------------------------

# Résumé des profils par cluster avec % de malades
heart_clean %>%
  group_by(cluster_km) %>%
  summarise(
    n           = n(),
    age_moy     = round(mean(age), 1),
    thalach_moy = round(mean(thalach), 1),
    oldpeak_moy = round(mean(oldpeak), 2),
    ca_moy      = round(mean(ca), 2),
    pct_malade  = round(mean(target) * 100, 1)
  ) %>%
  print()

# =============================================================================
# FIN DU SCRIPT
# =============================================================================
