# Export RobStatTM-master/data .RData files to CSV for Python use.
# Run from project root: Rscript robstattm/r/export_robstattm_data.R

data_dir <- file.path("robstattm", "RobStatTM-master", "data")
out_dir <- file.path("robstattm", "python", "data")
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

rdata_files <- list.files(data_dir, pattern = "\\.RData$", full.names = TRUE)
for (f in rdata_files) {
  name <- sub("\\.RData$", "", basename(f))
  env <- new.env()
  load(f, envir = env)
  obj <- get(name, envir = env)
  out_path <- file.path(out_dir, paste0(name, ".csv"))
  if (is.vector(obj) && !is.list(obj)) {
    write.csv(data.frame(x = obj), out_path, row.names = FALSE)
  } else {
    write.csv(obj, out_path, row.names = FALSE)
  }
  message("Exported: ", name, " -> ", out_path)
}
message("Done. CSVs written to ", out_dir)
