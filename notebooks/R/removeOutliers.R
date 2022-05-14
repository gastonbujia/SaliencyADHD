removeOutliers <- function(D, vid){
  
  library(sjmisc)
  IDs <- getOutlierList(vid)
  D = D[!(str_contains(IDs, D$ID)),]
  
  return(D)
}