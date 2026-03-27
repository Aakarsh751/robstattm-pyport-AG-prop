cat("====================================================\n")
cat("  Running Ch_2_Foundations_Demo.R (non-interactive)\n")
cat("====================================================\n\n")

pdf(file.path("pcra", "output", "Ch2_Figures.pdf"), width = 10, height = 8)

library(PCRA)
library(data.table)
library(xts)
library(PerformanceAnalytics)
library(PortfolioAnalytics)
library(foreach)
library(CVXR)
library(RPESE)
library(RPEIF)
library(ggplot2)
library(reshape2)
library(lubridate)
library(dplyr)
library(RobStatTM)
library(hitandrun)
library(optimalRhoPsi)

cat("All libraries loaded successfully.\n\n")

tryCatch({
  ##  Figure 2.1
  cat("--- Figure 2.1: Two-asset efficient frontier (rho=0) ---\n")
  muVol <- c(.20, .10, .15, .04)
  wts   <- seq(0,1, .01)
  efront2Asset <- function(wts, rho, muVol = c(.20, .10, .15, .04)) {
    sigma1 <- muVol[1]; mu1 <- muVol[2]
    sigma2 <- muVol[3]; mu2 <- muVol[4]
    n <- length(wts)
    efront <- data.frame(matrix(rep(0, 3*n), ncol = 3))
    names(efront) <- c("SIGMA", "MU", "WTS")
    w <- wts
    for(i in 1:n) {
      mu <- w[i]*mu1 + (1 - w[i])*mu2
      var <- w[i]^2*sigma1^2 + 2*w[i]*(1 - w[i])*rho*sigma1*sigma2 + (1 - w[i])^2*sigma2^2
      sigma <- sqrt(var)
      efront[i,] <- c(sigma, mu, w[i])
    }
    return(efront)
  }
  ef   <- efront2Asset(wts, 0, muVol = muVol)
  gmv  <- ef[ef$SIGMA == min(ef$SIGMA),]
  xlab <- expression(sigma [P])
  ylab <- expression(mu [P])
  par(pty = "s")
  plot(ef$SIGMA, ef$MU, type = "l", xlab = xlab, ylab = ylab,
       xlim = c(0, .25), ylim = c(0.03, .11), lwd = 2, cex.lab = 1.5)
  points(muVol[c(1, 3)], muVol[c(2, 4)], pch = 19, cex = 1.3)
  points(gmv, pch = 19, cex = 1.3)
  text(.04, .10, expression(paste(rho, " = 0")), cex = 1.5)
  text(0.12, .0616, adj = c(1, NA), "MinRisk   ", cex = 1.1)
  text(0.13, .0616, adj = c(0,NA), "(.12, .0616)",cex = 1.1)
  text(0.2, .1, adj = c(0, NA), "  (.20, .10)", cex = 1.1)
  text(0.15, .04, adj = c(0, NA),"  (.15, .04)", cex = 1.1)
  cat("  GMV portfolio: sigma =", round(gmv$SIGMA, 4), ", mu =", round(gmv$MU, 4), "\n")
  cat("  Figure 2.1 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.1:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Figure 2.2
  cat("--- Figure 2.2: Efront with rho = -1, 0, +1 ---\n")
  muVol <- c(.20, .10, .15, .04)
  wts <- seq(0, 1, .01)
  ef  <- efront2Asset(wts,  0, muVol = muVol)
  ef1 <- efront2Asset(wts,  1, muVol = muVol)
  ef2 <- efront2Asset(wts, -1, muVol = muVol)
  gmv <- ef[ef$SIGMA == min(ef$SIGMA),]
  gmv2 <- ef2[ef2$SIGMA == min(ef2$SIGMA),]
  par(pty = "s")
  plot(ef$SIGMA, ef$MU, type = "l", xlab = expression(sigma[P]), ylab = expression(mu[P]),
       xlim = c(0, .25), ylim = c(0.03, .11), lwd = 2, cex.lab = 1.5)
  points(muVol[c(1, 3)], muVol[c(2, 4)], pch = 19, cex = 1.5)
  points(gmv, pch = 19, cex = 1.3)
  lines(ef1$SIGMA, ef1$MU, lty = 2, lwd = 2)
  lines(ef2$SIGMA, ef2$MU, lty = 2, lwd = 2)
  points(gmv2, pch = 19, cex = 1.3)
  text(.12, .07, expression(paste(rho, " = 0 ")),  adj = c(1, NA), cex = 1.5)
  text(.02, .08, expression(paste(rho, " = -1  ")), adj = c(0, NA), cex = 1.5)
  text(.18, .07, expression(paste(rho, " = +1 ")),  adj = c(0, NA), cex = 1.5)
  text(0.2,  .1,  adj = c(0, NA), "  (.20, .10)", cex = 1.1)
  text(0.15, .04, adj = c(0, NA), "  (.15, .04)", cex = 1.1)
  cat("  Figure 2.2 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.2:", conditionMessage(e), "\n\n"))

tryCatch({
  ##   Figure 2.3
  cat("--- Figure 2.3: Long-only vs short-selling ---\n")
  muVol <- c(.20, .10, .15, .04)
  wts   <- seq(0, 1, .01)
  efLO  <- efront2Asset(wts, 0, muVol = muVol)
  wts   <- seq(1, 1.25, .01)
  efSS  <- efront2Asset(wts, 0, muVol = muVol)
  gmv   <- efLO[efLO$SIGMA == min(efLO$SIGMA),]
  maxMu <- efLO[efLO$MU == max(efLO$MU),]
  maxMuSS <- efSS[efSS$MU == max(efSS$MU),]
  par(pty = "s")
  plot(efLO$SIGMA, efLO$MU, type = "l", xlab = expression(sigma[P]), ylab = expression(mu[P]),
       xlim=c(0, .40), ylim=c(.02, .13), lwd = 2, cex.lab = 1.5)
  lines(efSS$SIGMA, efSS$MU, lty = "dashed", lwd = 2)
  points(gmv[1:2], pch = 19, cex = 1.3)
  points(maxMu[1:2], pch = 19, cex = 1.3)
  points(maxMuSS[1:2], pch = 19, cex = 1.3)
  text(.04, .12, expression(paste(rho, " = 0")), cex = 1.5)
  text(gmv[1:2],    adj = c(0, NA), paste("  (", toString(round(gmv[1:2],    2)), ")"), cex = 1.1)
  text(maxMu[1:2],  adj = c(0, NA), paste("  (", toString(maxMu[1:2]),             ")"), cex = 1.1)
  text(maxMuSS[1:2],adj = c(0, NA), paste("  (", toString(round(maxMuSS[1:2],2)), ")"), cex = 1.1)
  cat("  Figure 2.3 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.3:", conditionMessage(e), "\n\n"))

tryCatch({
  ##   Figure 2.4
  cat("--- Figure 2.4: Three-asset pairwise efronts ---\n")
  volMu1 <- c(.20, .10)
  volMu2 <- c(.15, .04)
  volMu3 <- c(.10, .02)
  wts <- seq(0, 1, .01)
  ef1 <- efront2Asset(wts, 0, muVol = c(volMu1, volMu2))
  ef2 <- efront2Asset(wts, 0, muVol = c(volMu1, volMu3))
  ef3 <- efront2Asset(wts, 0, muVol = c(volMu2, volMu3))
  par(pty = "s")
  plot(ef1$SIGMA, ef1$MU, type = "l", xlab = expression(sigma[P]), ylab = expression(mu[P]),
       xlim=c(0,.25), ylim=c(0,.11), lwd = 2, cex.lab = 1.5)
  lines(ef2$SIGMA, ef2$MU, lty = 2, lwd = 2.0)
  lines(ef3$SIGMA, ef3$MU, lty = 3, lwd = 2.0)
  xy <- rbind(volMu1, volMu2, volMu3)
  points(xy, pch = 19, cex = 1.3)
  text(volMu1[1] + 0.01, volMu1[2], adj = c(0, NA), toString(volMu1), cex = 1.1)
  text(volMu2[1] + 0.01, volMu2[2], adj = c(0, NA), toString(volMu2), cex = 1.1)
  text(volMu3[1] + 0.01, volMu3[2], adj = c(0, NA), toString(volMu3), cex = 1.1)
  text(.04, .10, expression(paste(rho, " = 0")), cex = 1.5)
  cat("  Figure 2.4 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.4:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Figure 2.5
  cat("--- Figure 2.5: Random portfolios in risk-return space ---\n")
  volMu1 <- c(.20,.10); volMu2 <- c(.15,.04); volMu3 <- c(.10,.02)
  vol <- c(volMu1[1], volMu2[1], volMu3[1])
  mu  <- c(volMu1[2], volMu2[2], volMu3[2])
  corrMat0 <- matrix(rep(0, 9),nrow = 3) + diag(rep(1, 3))
  covMat0 <- diag(vol) %*% corrMat0 %*% diag(vol)
  n <- 500
  port <- matrix(rep(0, 2*n), ncol = 2)
  dimnames(port)[[2]] = c("SIG.P", "MU.P")
  set.seed(42)
  wts = hitandrun::simplex.sample(3, n)$samples
  for(i in 1:n) {
    x <- wts[i,]
    port[i, 1] <- sqrt(x%*%covMat0%*%x)
    port[i, 2] <- x%*%mu
  }
  plot(port[, 1], port[, 2], xlim = c(0, .25), ylim = c(0, .11),
       xlab = expression(sigma[P]), ylab = expression(mu[P]), pch = 20, cex = .7, cex.lab = 1.5)
  points(vol, mu, pch = 19, cex = 1.3)
  text(volMu1[1] + 0.01, volMu1[2], adj = c(0, NA), toString(volMu1), cex = 1.1)
  text(volMu2[1] + 0.01, volMu2[2], adj = c(0, NA), toString(volMu2), cex = 1.1)
  text(volMu3[1] + 0.01, volMu3[2], adj = c(0, NA), toString(volMu3), cex = 1.1)
  text(.04, .10, expression(paste(rho, " = 0")), cex = 1.5)
  cat("  Figure 2.5 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.5:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Example 2.3
  cat("--- Example 2.3: GMV from mu and cov ---\n")
  muRet   <- c(.10, .04, .02)
  volRet  <- c(.20, .15, .10)
  corrRet <- diag(c(1, 1, 1))
  result <- PCRA::mathGmvMuCov(muRet, volRet, corrRet, digits = 3)
  cat("  GMV weights:", result$wtsGmv, "\n")
  cat("  GMV mean:", result$muGmv, "\n")
  cat("  GMV vol:", result$sigmaGmv, "\n\n")
}, error = function(e) cat("ERROR in Example 2.3:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Figure 2.7
  cat("--- Figure 2.7: 10 SmallCap stocks + Market time series ---\n")
  stockItems <- c("Date","TickerLast","CapGroupLast","Return","MktIndexCRSP")
  dateRange  <- c("1997-01-31","2010-12-31")
  stocksDat  <- PCRA::selectCRSPandSPGMI("monthly", dateRange = dateRange,
                                         stockItems = stockItems,
                                         factorItems = NULL,
                                         subsetType = "CapGroupLast",
                                         subsetValues = "SmallCap",
                                         outputType = "xts")
  returns10Mkt <- stocksDat[, c(21:30,107)]
  names(returns10Mkt)[11] <- "Market"
  tsPlotMP(returns10Mkt, scaleType = "free", layout = c(2, 6), stripText.cex = .45,
           axis.cex = 0.4, lwd = 0.5)
  cat("  Stocks:", names(returns10Mkt)[1:10], "\n")
  cat("  Figure 2.7 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.7:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Figures 2.8 and 2.9
  cat("--- Figures 2.8 & 2.9: GmvLS optimization ---\n")
  returns <- returns10Mkt[, 1:10]
  Market  <- returns10Mkt[, 11]
  funds   <- colnames(returns)
  pspec       <- portfolio.spec(assets=funds)
  pspec.fi    <- add.constraint(pspec, type="full_investment")
  pspec.gmvLS <- add.objective(pspec.fi, type="risk", name="var")
  bt.gmvLS <- optimize.portfolio.rebalancing(returns, pspec.gmvLS,
                                             optimize_method = "CVXR",
                                             rebalance_on = "months",
                                             rolling_window = 60,
                                             trace = TRUE)
  wtsGmvLS <- extractWeights(bt.gmvLS)
  GmvLS <- Return.rebalancing(returns, wtsGmvLS)
  ret.comb <- na.omit(merge.xts(GmvLS, Market, all=FALSE))
  names(ret.comb) <- c("GmvLS", "Market")
  
  tsPlotMP(wtsGmvLS, layout = c(2,5), scaleType = "same", stripText.cex = 0.7, axis.cex = .7)
  cat("  Figure 2.8 done.\n")
  
  tsPlotMP(ret.comb, scaleType = "same", stripText.cex = .7, axis.cex = .7)
  cat("  Figure 2.9 done.\n\n")
}, error = function(e) cat("ERROR in Figures 2.8/2.9:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Figure 2.10
  cat("--- Figure 2.10: Cumulative returns & drawdowns ---\n")
  R <- ret.comb
  geometric <- TRUE
  c.xts <- if (geometric) cumprod(1+R) else 1 + cumsum(R)
  
  p <- plot.xts(c.xts[,1], col="black", main = "Cumulative Returns",
                     grid.ticks.lwd=1, grid.ticks.lty = "dotted", grid.ticks.on = "years",
                     labels.col="grey20", cex.axis=0.8, format.labels = "%b\n%Y",
                     ylim = c(min(c.xts), max(c.xts)))
  p <- addSeries(c.xts[,2], on=1, lwd=2, col="darkred", lty="dashed")
  p <- addLegend("topleft", on = 1,
                      legend.names = names(c.xts),
                      lty = c(1,2), lwd = rep(2, NCOL(c.xts)),
                      col = c("black", "darkred"),
                      bty = "o", box.col = "white",
                      bg=rgb(t(col2rgb("white")), alpha = 200, maxColorValue = 255))
  d.xts <- PerformanceAnalytics::Drawdowns(R)
  p <- xts::addSeries(d.xts[,1], col="darkblue", lwd=2, main="Drawdown",
                      ylim = c(min(d.xts), 0))
  p <- xts::addSeries(d.xts[,2], on=2, lwd=2, col="darkred", lty="dashed")
  print(p)
  cat("  Figure 2.10 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.10:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Table 2.1
  cat("--- Table 2.1: Drawdowns ---\n")
  dt2mat <- table.Drawdowns(ret.comb, top = 2)
  dt2mat[,4] <- round(dt2mat[,4], 2)
  dt2 <- data.frame(dt2mat)[, 1:5]
  names(dt2) <- c("Begin", "Minimum", "End", "Depth", "Months")
  dt2 <- dt2[, c(1:3, 5, 4)]
  print(dt2)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.1:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Table 2.2
  cat("--- Table 2.2: Risk measures with standard errors ---\n")
  SD12 <- SD.SE(ret.comb, se.method = "IFiid")
  SD12 <- printSE(SD12, round.digit = 4)
  SSD12 <- SemiSD.SE(ret.comb, se.method = "IFiid")
  SSD12 <- printSE(SSD12, round.digit = 4)
  ES12 <- ES.SE(ret.comb, se.method = "IFiid")
  ES12 <- printSE(ES12, round.digit = 4)
  VaR12 <- VaR.SE(ret.comb, se.method = "IFiid")
  VaR12 <- printSE(VaR12, round.digit = 4)
  RM <- 100*rbind(SD12,SSD12,ES12,VaR12)
  colnames(RM) <- c("Estimate (%)","StdError (%)")
  rownames(RM) <- c("GmvLS SD",  "Market SD",
                    "GmvLS SSD", "Market SSD",
                    "GmvLS ES",  "Market ES",
                    "GmvLS VaR", "Market VaR")
  RM <- as.data.frame(RM)
  print(RM)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.2:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Table 2.3
  cat("--- Table 2.3: Performance ratios ---\n")
  SR12  <- SR.SE(ret.comb, se.method = "IFiid")
  SR12  <- printSE(SR12, round.digit = 2)
  DSR12 <- DSR.SE(ret.comb, se.method = "IFiid")
  DSR12 <- printSE(DSR12, round.digit = 2)
  SoR12 <- SoR.SE(ret.comb, se.method = "IFiid")
  SoR12 <- printSE(SoR12, round.digit = 2)
  ESratio12 <- ESratio.SE(ret.comb, se.method = "IFiid")
  ESratio12 <- printSE(ESratio12, round.digit = 2)
  Ratios <- rbind(SR12,DSR12,SoR12,ESratio12)
  colnames(Ratios)  <- c("Estimate","StdError")
  rownames(Ratios) <- c("GmvLS SR", "Market SR",
                        "GmvLS DSR","Market DSR",
                        "GmvLS SOR","Market SOR",
                        "GmvLS ESR","Market ESR")
  Ratios <- as.data.frame(Ratios)
  print(Ratios)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.3:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.16
  cat("--- Figure 2.16: Efront with PCRA mathEfrontRiskyMuCov ---\n")
  muRet   <- c(.10, .04, .02)
  volRet  <- c(.20, .15, .10)
  corrRet <- diag(c(1, 1, 1))
  mathEfrontRiskyMuCov(muRet, volRet, corrRet, efront.only = FALSE)
  cat("  Figure 2.16 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.16:", conditionMessage(e), "\n\n"))

tryCatch({
  ##  Table 2.4
  cat("--- Table 2.4: Efront weights ---\n")
  muRet   <- c(.10, .04, .02)
  volRet  <- c(.20, .15, .10)
  corrRet <- diag(c(1, 1, 1))
  efront  <-  mathEfrontRiskyMuCov(muRet, volRet, corrRet, npoints = 5,
                                   values = TRUE, display = FALSE)
  mu.efront <- efront$mu.efront
  wtsEfront <- mathWtsEfrontRiskyMuCov(muRet, volRet, corrRet,
                                       mu.efront, digits = 3)
  print(wtsEfront)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.4:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.25
  cat("--- Figure 2.25: Leverage plot ---\n")
  rf        <- 0.03
  rf_lend   <- 0.04
  rf_borrow <- 0.06
  er_port   <- 0.07
  leverage  <- seq(0, 2, .1)
  er_rf <- rf + leverage * (er_port - rf)
  er_1  <- rf_lend   + leverage * (er_port - rf_lend)
  er_2  <- rf_borrow + leverage * (er_port - rf_borrow)
  df <- data.frame("Leverage" = leverage,
                   "Single Risk Free Rate for Borrowing and Lending" = er_rf,
                   "Different Risk Free Rates for Borrowing and Lending" = pmin(er_1, er_2))
  df_melt <- reshape2::melt(df, id.vars = "Leverage", variable.name = "Risk_Free_Rate")
  df_melt[["Risk_Free_Rate"]] <- gsub("\\.", " ", df_melt[["Risk_Free_Rate"]])
  p <- ggplot(df_melt, aes(x = Leverage, y = value)) +
    geom_line(aes(color = Risk_Free_Rate, linetype = Risk_Free_Rate), linewidth = 1) +
    labs(x = "Leverage", y = "Expected Return",
         color = "Risk Free Rate", linetype = "Risk Free Rate") +
    theme_bw()
  print(p)
  cat("  Figure 2.25 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.25:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.30 - Utility functions
  cat("--- Figure 2.30: Utility functions ---\n")
  par(mfrow = c(1,2))
  x <- seq(.01,3,.01)
  y <- log(x)
  plot(x, y, axes=FALSE, type = "l", ylim =c(-8, 2), lwd = 1.0, xlab = "v", ylab = "U(v)")
  axis(side = 1, pos = 0)
  axis(side = 2, pos = 0)
  gamma <- -0.5
  y <- (x^gamma - 1)/gamma
  lines(x, y, lty = 8, lwd = 1.0)
  gamma <- 0.5
  y <- (x^gamma - 1)/gamma
  lines(x, y, lty = 3, lwd = 1.0)

  v <- seq(0, 1.5, .01)
  u <- v - v^2
  plot(v, u, type = "l", ylim = c(-0.7, 0.4), xlab = "v", ylab = "U(v)", lwd = 1.5)
  abline(v = .50, lty = "dotted")
  abline(h = .25, lty = "dotted")
  par(mfrow = c(1,1))
  cat("  Figure 2.30 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.30:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.31 - CAPM SML
  cat("--- Figure 2.31: CAPM Security Market Line ---\n")
  rm1    <- 0.18
  Beta1  <- c(1.53, 1.36, 1.24, 1.17, 1.06, 0.92, 0.84, 0.76, 0.63, 0.48)
  Mu1    <- c(0.26, 0.22, 0.21, 0.21, 0.18, 0.17, 0.16, 0.15, 0.13, 0.12)
  SML1   <- rm1 * Beta1
  df1  <- data.frame(Beta1, Mu1, SML1)
  df1a <- data.frame(x=1, y = rm1)
  p1 <- ggplot(df1) +
    geom_point(aes(x = Beta1, y = Mu1), color = "black") +
    geom_line(aes(x = Beta1, y = SML1), color = "gray20") +
    labs(x = "Beta", y = "Mean Excess Return", title = "1931 - 1965")
  print(p1 + geom_point(data = df1a, aes(x = x, y = y), color = "dodgerblue4", shape = 17, size = 3))
  cat("  Figure 2.31 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.31:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Table 2.6
  cat("--- Table 2.6: Historical excess returns ---\n")
  df    <- data.frame(matrix(" ", nrow = 6, ncol = 4))
  df$X1 <- c("1/31--12/39",  "1/40--12/49", "1/50--12/59", "1/60--12/69", "1/70--12/79","1/80--12/91")
  df$X2 <- c(-0.05, 0.03, 0.08, 0.03, 0.01, 0.09)
  df$X3 <- c(0.17,  0.10, 0.06, 0.07, 0.10, 0.08)
  df$X4 <- c(-0.94, 1.06, 4.25, 1.32, 0.18, 3.90)
  colnames(df) <- c("Period", "Mean(Excess Return)", "Std. Dev(Excess Return)", "t(Mean(Excess Return))")
  print(df)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.6:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.36 - mOpt and Huber rho/psi
  cat("--- Figure 2.36: mOpt and Huber rho/psi functions ---\n")
  ccHuber <- 1.345
  ccModOpt <- computeTuningPsi_modOpt(0.95)
  rhoHuber <- function(x, cc = ccHuber) {
    ifelse(abs(x/ccHuber) < 1, 0.5*x^2, ccHuber*abs(x) - 0.5*ccHuber^2)
  }
  par(mfrow = c(1,2))
  x <- seq(-5, 5, 0.01)
  rhoMax <- rho_modOpt(3, cc = ccModOpt)
  plot(x, rho_modOpt(x, cc = ccModOpt)/rhoMax, ylim = c(0, 2), ylab = "rho(x)",
       type = "l", lwd = 1.3, cex.lab = 1.1)
  lines(x, rhoHuber(x, ccHuber)/rhoMax, col = "darkred", lty = "dashed", lwd = 1.3)
  legend("topleft", c("mOpt", "Huber"),
         lty = c("solid", "dashed"), lwd = c(1.3, 1.3), cex = 0.8,
         col = c("black", "darkred"), bty = "n")

  psiHuber <- function(x, ccHub = 1.345) {
    psi <- ifelse(abs(x/ccHub) < 1, x, ccHub)
    ifelse(x/ccHub <= -1, -ccHub, psi)
  }
  plot(x, psi_modOpt(x, cc = ccModOpt), ylim = c(-2.5, 2.5), ylab = "psi(x)",
       type = "l", cex.lab = 1.1, lwd = 1.3)
  lines(x, psiHuber(x), col = "darkred", lty = "dashed", lwd = 1.3)
  legend("topleft", c("mOpt", "Huber"),
         lty = c("solid", "dashed"), lwd = c(1.3, 1.3), cex = 0.8,
         col = c("black", "darkred"), bty = "n")
  par(mfrow = c(1,1))
  cat("  Figure 2.36 done.\n\n")
}, error = function(e) cat("ERROR in Figure 2.36:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Figure 2.38 and Table 2.7 - Robust mean for FIA
  cat("--- Figure 2.38 & Table 2.7: Robust vs sample mean for FIA ---\n")
  data(edhec)
  hfnames <- c("CA", "CTA", "DIS", "EM", "EMN", "ED", "FIA",
               "GM", "LSE", "MA",  "RV", "SS",  "FOF")
  names(edhec) <- hfnames
  retLongFIA <- edhec[, "FIA"]
  retFIA <- retLongFIA['1998-01-31/1999-12-31', ]
  index(retFIA) <- as.yearmon(index(retFIA))
  mu <- 100*mean(retFIA)
  se.mu <- 100*sd(retFIA)/sqrt(24)
  x <- locScaleM(retFIA, eff = .95)
  muRob <- 100*x$mu
  se.muRob <- 100*x$std.mu
  plot.zoo(retFIA, type ="b", xlab = "", ylab = "FIA Returns")
  abline(h = muRob/100, col = "blue")
  abline(h = mu/100, lty = "dashed", col ="red")
  legend(1999.2, -.03, legend = c("Robust Mean", "Sample Mean"), lwd = c(1, 2),
         lty = c("solid", "dashed"), col = c("blue", "red"), bty = "n", cex = 1.3)
  cat("  Figure 2.38 done.\n")

  tstat.mu <- mu/se.mu
  tstat.muRob <- muRob/se.muRob
  SR.classic <- tstat.mu/sqrt(24)
  SR.Rob <- tstat.muRob/sqrt(24)
  row1 <- round(c(mu, se.mu, tstat.mu, SR.classic), 2)
  row2 <- round(c(muRob, se.muRob, tstat.muRob, SR.Rob), 2)
  meanEsts <- data.frame(rbind(row1, row2))
  names(meanEsts) <- c("Estimate (%)", "Std. Error (%)", "t-Stat", "Sharpe Ratio")
  row.names(meanEsts) <- c("Sample Mean", "Robust Mean")
  cat("  Table 2.7:\n")
  print(meanEsts)
  cat("\n")
}, error = function(e) cat("ERROR in Figure 2.38 / Table 2.7:", conditionMessage(e), "\n\n"))

tryCatch({
  ## Table 2.8 - Scale estimators
  cat("--- Table 2.8: Scale estimators on edhec ---\n")
  data(edhec, package = "PerformanceAnalytics")
  hfnames <- c("CA", "CTA", "DIS", "EM", "EMN", "ED", "FIA",
               "GM", "LSE", "MA",  "RV",  "SS", "FOF")
  names(edhec) <- hfnames
  edhec <- edhec[ , 1:12]
  returns <- 100*edhec['1998-01-31/1999-12-31']
  StdDev <- apply(returns,2,sd)
  MADM <- apply(returns,2,mad)
  resid <- returns - median(returns)
  RobSD <- apply(resid, 2, scaleM, family = "mopt")
  SDestsMat <- cbind(StdDev, MADM, RobSD)
  SDestsMat <- round(SDestsMat,2)
  SDests <- data.frame(hfnames[1:12], SDestsMat)
  names(SDests) <- c("HFindex", "StdDev", "MADM", "RobSD")
  row.names(SDests) <- NULL
  print(SDests)
  cat("\n")
}, error = function(e) cat("ERROR in Table 2.8:", conditionMessage(e), "\n\n"))

dev.off()
cat("====================================================\n")
cat("  All figures saved to pcra/output/Ch2_Figures.pdf\n")
cat("  Script completed successfully!\n")
cat("====================================================\n")
