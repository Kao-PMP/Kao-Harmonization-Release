#!/usr/bin/env Rscript
# convert_sas.R
# Writes convert_sas.csv to the current working directory.
# usage: path/to/convert_sas.R <file>
#
#install.packages("sas7bdat")
#
library(sas7bdat)
args <- commandArgs(trailingOnly = TRUE)
file <- args[1]
short_file  <- strsplit(basename(file), "\\.")[[1]][1]
csv_file <- paste(short_file, "csv", sep = ".")
csv_path <- file.path(getwd(), csv_file)
print("converting...")
print(csv_path)
df <- read.sas7bdat(file)
write.csv(df, csv_path)
