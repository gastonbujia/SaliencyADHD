readDataTable <- function(tablesPath, str){
  
  D <- read.csv(paste(tablesPath, str, sep=''), sep=";")
  
  D$Sex <- as.factor(D$Sex)
  D$samplingRate <- as.factor(D$samplingRate)
  D$ADHDCategory <- as.factor(as.character(D$ADHDCategory))
  D$ADHDCategory <- relevel(D$ADHDCategory, ref = "NoADHD")

  D$EHQ_Total <- as.factor(as.character(D$EHQ_Total))
  D$EHQ_Total[D$EHQ_Total == ""] <- NA
  D$EHQ_Total <- droplevels(D$EHQ_Total)
  D$EHQ_Total <- relevel(D$EHQ_Total, ref = "Righthanded")
  
  D$Age <- as.numeric(as.character(D$Age))
  D$SWAN_HY <- as.numeric(as.character(D$SWAN_HY))
  D$SWAN_IN <- as.numeric(as.character(D$SWAN_IN))
  D$SWAN_Total <- as.numeric(as.character(D$SWAN_Total))
  
  return(D)
}