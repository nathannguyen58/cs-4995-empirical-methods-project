Means <- aggregate(RedditDataEMDS,by=list(SchoolType=RedditDataEMDS$SchoolType, TimePeriod=RedditDataEMDS$TimePeriod),data=RedditDataEMDS[-c(1,2)],FUN=mean)
Means <- Means[-c(3,4)]
Means <- Means[order(rev(Means$TimePeriod)),]
View(Means)
MeansType <- aggregate(RedditDataEMDS,by=list(SchoolType=RedditDataEMDS$SchoolType),data=RedditDataEMDS[-c(1,2)],FUN=mean)
MeansType <- MeansType[-c(2,3)]
View(MeansType)

MeansPeriod <- aggregate(RedditDataEMDS,by=list(TimePeriod=RedditDataEMDS$TimePeriod),data=RedditDataEMDS[-c(1,2)],FUN=mean)
MeansPeriod <- MeansPeriod[-c(2,3)]
View(MeansPeriod)

#------------------------------------------------------------------------------

uSub <- subset(RedditDataEMDS, SchoolType %in% 'Urban')
rSub <- subset(RedditDataEMDS, SchoolType %in% 'Rural')

peakSub <- subset(RedditDataEMDS, TimePeriod %in% 'Peak')
preSub <- subset(RedditDataEMDS, TimePeriod %in% 'Pre')
openSub <- subset(RedditDataEMDS, TimePeriod %in% 'Opening')

uOpenSub <- subset(RedditDataEMDS, TimePeriod %in% 'Opening' & SchoolType %in% 'Urban')
uPreSub <- subset(RedditDataEMDS, TimePeriod %in% 'Pre' & SchoolType %in% 'Urban')
uPeakSub <- subset(RedditDataEMDS, TimePeriod %in% 'Peak' & SchoolType %in% 'Urban')

rOpenSub <- subset(RedditDataEMDS, TimePeriod %in% 'Opening' & SchoolType %in% 'Rural')
rPreSub <- subset(RedditDataEMDS, TimePeriod %in% 'Pre' & SchoolType %in% 'Rural')
rPeakSub <- subset(RedditDataEMDS, TimePeriod %in% 'Peak' & SchoolType %in% 'Rural')

#---------------------------------------------------------------------------
#library(dplyr)
#library(tidyverse)
#library(ggpubr)
library(rstatix)
library(tidyr)
library(xlsx)
manovaBoth <- manova(cbind(Anger, Joy, Disgust, Fear, Surprise, Sadness, Neutral) ~ RedditDataEMDS$TimePeriod + RedditDataEMDS$SchoolType, data = RedditDataEMDS)
#Doesn't work - summary.manova(manovaBoth)
#summary(manovaBoth)
sum <- summary.aov(manovaBoth)
sum

sessionInfo()
mydata.long <- rSub %>%
        pivot_longer(-TimePeriod & -SchoolType, names_to = "variables", values_to = "value")
stat.test <- mydata.long %>%
        group_by(variables) %>%
        t_test(value ~ TimePeriod) %>%
        adjust_pvalue(method = "BH") %>%
        add_significance()
print(stat.test, n=25)
write.xlsx(as.data.frame(stat.test), file = "ttest2.xlsx")
#--------------------------------------------------------------------------
library(MASS)
library(ggplot2)
attach(iris)
scaled <- scale(RedditDataEMDS[3:9])
sample <- sample(c(TRUE, FALSE), nrow(RedditDataEMDS), replace=TRUE, prob=c(0.7,0.3))
train <- RedditDataEMDS[sample, ]
test <- RedditDataEMDS[!sample, ] 
View(train)
model <- lda(TimePeriod~., data=train[-1])
model
predicted <- predict(model, test)
names(predicted)
mean(predicted$class==test$TimePeriod)
