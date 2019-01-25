
install.packages("readstata13")
library(readstata13)
dat <- read.dta13("test.dta")
write.csv(dat, "test.csv")

