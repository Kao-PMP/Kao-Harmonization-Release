#!/usr/local/bin/Rscript

install.packages("haven")
library(haven)

argv <- commandArgs(trailingOnly = FALSE)
CSV_FILE <- argv[length(argv) ]


df <- read_sas(CSV_FILE)
for (n in names(df)) {
    print(attr(df[[n]], 'label'))
}
