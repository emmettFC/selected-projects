require(R.utils)
library(Rcpp)
library(rvest)
library(XML)
library(XBRL)
options(stringsAsFactors = TRUE)


args   <- commandArgs(trailingOnly = TRUE)

newdir    <-file.path(paste('/home/ubuntu/sec/filings__', args[1], '__', args[2], sep=''))

zippedFiles  <-list.files(newdir)
finalDir     <-file.path(paste('/home/ubuntu/sec/parsed_min__', args[1], '__', args[2], sep=''))
unzippedDir  <-file.path(paste('/home/ubuntu/sec/unzipped__', args[1], '__', args[2], sep=''))
print(finalDir)
dir.create(finalDir, showWarnings = FALSE) 



buildFrame <- function(name, xbrl.vars) {
        x                   <- name
        name                <- as.data.frame(xbrl.vars[name])
        colnames(name)      <- c(gsub(paste('^', x, '.', sep = ""), '', colnames(name)))
        return(name)
}


parseDoc <- function(u, newdir, finalDir, unzippedDir) {
    tryCatch({
            for(m in list.files(unzippedDir)){
                if(length(grep(pattern="[[:digit:]].xml", x=m))==1) { 
                    print(m) 
                    inst      <- file.path(unzippedDir, m)
                    xbrl.vars <- xbrlDoAll(inst, verbose=FALSE)
                    
                    # build frames
                    fact    <- buildFrame('fact', xbrl.vars)
                    context <- buildFrame('context', xbrl.vars)
                    # joins tables to fact 
                    join1   <- merge(x = fact, y = context, by = "contextId", all.x = TRUE)
                    # write out file          
                    title   <-gsub("-|.xml", "", m)  
                    print(title)
                    loc    <- file.path(finalDir,paste0(title,'.csv'))
                    print(loc) 
                    write.table(join1, file = loc, sep = "," , append = TRUE)    
                    unlink(paste(unzippedDir, '/*', sep = ''))
                    unlink(file.path(newdir, u))
                }
            }
        }, 
        error = function(e) {unlink(paste(unzippedDir, '/*', sep = ''))}
        )
}


for(u in zippedFiles){
    print(u)
    unzip(file.path(newdir, u), list=FALSE, overwrite=TRUE, junkpaths=FALSE, exdir=unzippedDir,
             unzip = "internal", setTimes=FALSE)
    tryCatch(
        expr = {
            evalWithTimeout(
                {parseDoc(u, newdir, finalDir, unzippedDir)}, 
                    timeout = 300)
            },
        TimeoutException = function(ex) cat("Timeout. Skipping.")
    )
}


unlink(paste(unzippedDir, '/*', sep = ''))









