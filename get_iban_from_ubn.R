get_IBAN_from_UBN <- function(ubn_input, 
                              url="http://52.166.163.47:80"
                              ) {
  
  #REQUIRED PACKAGES
  require(jsonlite)
  require(httr)
  require(data.table)
  
  #GET CHAIN
  req <- GET(paste0(url,"/chain"))
  chain <- fromJSON(content(req, "text",encoding = "UTF-8"))
  
  #GET NUMBER OF BLOCKS
  len<-chain$length
  
  #LOOP THROUGH BLOCKS STARTING FROM END TO FIND UBN
  found<-FALSE
  for (i in (len:1)){
    dt<-data.table(chain$chain$transactions[[i]])
    if (nrow(dt)==0) next      #else error if no transactions (first block)
    subdt <- dt[ubn==ubn_input,]
    if (nrow(subdt)>0) {
                        output<-subdt
                        found<-TRUE
                        break
                        }
  }
  
  #RETURN IF FOUND
  if (found==TRUE) return(output[,newiban]) else stop("UBN NOT FOUND")
  
}
