cat("Extracting PCRA data for Python reproduction...\n")

library(PCRA)
library(data.table)
library(xts)
library(PerformanceAnalytics)
library(PortfolioAnalytics)
library(foreach)
library(CVXR)

# Run from project root (ProfDM_Rproject)
out_dir <- file.path("pcra", "python", "data")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

stockItems <- c("Date","TickerLast","CapGroupLast","Return","MktIndexCRSP")
dateRange  <- c("1997-01-31","2010-12-31")
stocksDat  <- PCRA::selectCRSPandSPGMI("monthly", dateRange = dateRange,
                                       stockItems = stockItems,
                                       factorItems = NULL,
                                       subsetType = "CapGroupLast",
                                       subsetValues = "SmallCap",
                                       outputType = "xts")

returns10Mkt <- stocksDat[, c(21:30, 107)]
names(returns10Mkt)[11] <- "Market"

df10 <- data.frame(Date = index(returns10Mkt), coredata(returns10Mkt))
write.csv(df10, file.path(out_dir, "returns10Mkt.csv"), row.names = FALSE)
cat("Exported returns10Mkt.csv:", dim(df10), "\n")

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

dfWts <- data.frame(Date = index(wtsGmvLS), coredata(wtsGmvLS))
write.csv(dfWts, file.path(out_dir, "wtsGmvLS.csv"), row.names = FALSE)
cat("Exported wtsGmvLS.csv:", dim(dfWts), "\n")

dfComb <- data.frame(Date = index(ret.comb), coredata(ret.comb))
write.csv(dfComb, file.path(out_dir, "ret_comb.csv"), row.names = FALSE)
cat("Exported ret_comb.csv:", dim(dfComb), "\n")

data(edhec, package = "PerformanceAnalytics")
hfnames <- c("CA", "CTA", "DIS", "EM", "EMN", "ED", "FIA",
             "GM", "LSE", "MA",  "RV", "SS",  "FOF")
names(edhec) <- hfnames
dfEdhec <- data.frame(Date = index(edhec), coredata(edhec))
write.csv(dfEdhec, file.path(out_dir, "edhec.csv"), row.names = FALSE)
cat("Exported edhec.csv:", dim(dfEdhec), "\n")

data(FRBinterestRates, package = "PCRA")
dfFRB <- data.frame(Date = index(FRBinterestRates), Rate = coredata(FRBinterestRates))
write.csv(dfFRB, file.path(out_dir, "FRBinterestRates.csv"), row.names = FALSE)
cat("Exported FRBinterestRates.csv:", dim(dfFRB), "\n")

cat("\nDone. Files in:", out_dir, "\n")
