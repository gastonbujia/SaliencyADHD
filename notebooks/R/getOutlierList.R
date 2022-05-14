getOutlierList <- function(vid){
  
  tablesPath = '/Volumes/methlab/Students/Sabine Dziemian/Eye Movements in ADHD/Data/Tables/';
  D <- readDataTable(tablesPath, paste(vid, '/FinalTableH1', vid, '.csv', sep=""))

  thresh <- 3
  
  mnFix <- mean(D$nFix)
  snFix <- sd(D$nFix)*thresh
    
  mtFixDur <- mean(D$totalFixDur)
  stFixDur <- sd(D$totalFixDur)*thresh
    
  mmFixDur <- mean(D$meanFixDur)
  smFixDur <- sd(D$meanFixDur)*thresh
    
  msFixDur <- mean(D$skewnessFixDur)
  ssFixDur <- sd(D$skewnessFixDur)*thresh
    
  IDnFix <- D$ID[!(D$nFix > mnFix-snFix & D$nFix < mnFix+snFix)]
  IDtFixDur <- D$ID[!(D$totalFixDur > mtFixDur-stFixDur & D$totalFixDur < mtFixDur+stFixDur)]
  IDmFixDur <- D$ID[!(D$meanFixDur > mmFixDur-smFixDur & D$meanFixDur < mmFixDur+smFixDur)]
  IDsFixDur <- D$ID[!(D$skewnessFixDur > msFixDur-ssFixDur & D$skewnessFixDur < msFixDur+ssFixDur)]
  
  IDs <- unique(c(as.character(IDnFix), as.character(IDtFixDur), as.character(IDmFixDur), as.character(IDsFixDur)))

  return(IDs)
}