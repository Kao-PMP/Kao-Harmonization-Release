# HF-ACTION variable dependence

df = read.csv("hfaction.csv", na.strings="NA")

ignore=c('MLHF', "Bill", "Tota", "RVEF", "WBC", "Albu", "AST", "ALT", "ABBB", "HF.d", "Valv", "Time", 
         "AID",   "plcb", "dthd", "Transplant", "Hospitalization", "DeathStatus", "Pump.Failure", "Non.CV.Death", "CV.Death.2", "study")
do_these=names(df)
print(do_these)
for (i in do_these) {
  if (!(i  %in% ignore)) {
    for (j in do_these) {
      if  (!(j %in% ignore)) {
        if (i != j) {
          cort = cor.test(df[,i], df[,j])
          chisq_p <- chisq.test(table(df[,i], df[,j]))
          if ( !is.nan(cort$p.value) &  cort$p.value < 0.00000000000000000001 )  {
            print(paste("small cor:", i, j, cort$statistic, cort$p.value))
            #print(paste("small  x2:", i, j, chisq_p$p.value))
          }
          #if ( !is.nan(cort$p.value) &  cort$p.value > 0.1 )  {
          #  print(paste("large:", i, j, cort$statistic, cort$p.value))
          #}
          
          #
          #if ( !is.nan(chisq_p$p.value) &  chisq_p$p.value < 0.0001 )  {
          #  print(paste("small  x2:", i, j, chisq_p$p.value))
          #}
          #if ( !is.nan(chisq_p$p.value) &  chisq_p$p.value > 0.1 )  {
          #  print(paste("large:", i, j, chisq_p$statistic, chisq_p$p.value))
          #}
        }
      }
    }
  }
}
  
  
