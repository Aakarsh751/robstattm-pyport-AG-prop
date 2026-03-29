library(RobStatTM)

# lmrobdetMM — mineral, mopt, eff=0.95
data(mineral)
ctrl <- lmrobdet.control(family='mopt', efficiency=0.95)
fit  <- lmrobdetMM(zinc ~ copper, data=mineral, control=ctrl)
cat("lmrobdetMM intercept:", round(coef(fit)[1], 4), "\n")
cat("lmrobdetMM slope:",     round(coef(fit)[2], 4), "\n")
cat("lmrobdetMM scale:",     round(fit$scale, 4), "\n")
cat("lmrobdetMM r.squared:", round(fit$r.squared, 4), "\n")

# covRobMM — wine
data(wine)
set.seed(42)
cov_mm <- covRobMM(wine)
cat("covRobMM center[1..5]:", round(cov_mm$center[1:5], 2), "\n")
cat("covRobMM max dist:",     round(max(cov_mm$dist), 2), "\n")

# covRobRocke — wine
set.seed(42)
cov_rocke <- covRobRocke(wine)
cat("covRobRocke center[1..5]:", round(cov_rocke$center[1:5], 2), "\n")
cat("covRobRocke max dist:",     round(max(cov_rocke$dist), 2), "\n")

# pcaRobS — bus
data(bus)
set.seed(42)
pca <- pcaRobS(bus, ncomp=3, desprop=0.99)
cat("pcaRobS propSPC[1]:", round(pca$propSPC[1], 4), "\n")
cat("pcaRobS propex:",     round(pca$propex, 4), "\n")
