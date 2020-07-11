# Loading packages
library(ggplot2)
library(dplyr)
library(wesanderson)
library(ggrepel)
library(lme4)
library(sjPlot)
library(lmerTest)
library(ggmap)
library(maps)
library(mapdata)
library(gganimate)
library(ggpubr)
library(grid)
library(fitdistrplus)
library(rstudioapi)

v1 <- 1922:1980

current_path <- getActiveDocumentContext()$path 
setwd(dirname(current_path))

# Fig. 4 ------------------------------------------------------------

russian_group <- read.csv('data_plots/scatter_русский.csv')
russian_pred <- read.csv('data_plots/line_русский.csv')
russian_group$collected.datab <- 0
russian_group[russian_group$collected.data == 'direct',]$collected.datab <- 'Direct'
russian_group[russian_group$collected.data == 'indirect',]$collected.datab <- 'Indirect'
russian_pred$model.predictionb <- 0
russian_pred[russian_pred$model.prediction == 'indirect',]$model.predictionb <- 'Indirect'
russian_pred[russian_pred$model.prediction == 'direct',]$model.predictionb <- 'Direct'
ITM_group <- read.csv('data_plots/scatter_number of lang.csv')
ITM_pred <- read.csv('data_plots/line_number of lang.csv')
ITM_group$collected.datab <- 0
ITM_group[ITM_group$collected.data == 'direct',]$collected.datab <- 'Direct'
ITM_group[ITM_group$collected.data == 'indirect',]$collected.datab <- 'Indirect'
ITM_pred$model.predictionb <- 0
ITM_pred[ITM_pred$model.prediction == 'indirect',]$model.predictionb <- 'Indirect'
ITM_pred[ITM_pred$model.prediction == 'direct',]$model.predictionb <- 'Direct'

russian_pred_group <- dplyr::select(russian_pred, year_of_birth, model.predictionb, pred) %>% 
  group_by(year_of_birth, model.predictionb) %>% 
  summarise(pred = mean(pred))

ITM_pred_group <- dplyr::select(ITM_pred, year_of_birth, model.predictionb, pred) %>% 
  group_by(year_of_birth, model.predictionb) %>% 
  summarise(pred = mean(pred))

russian <- ggplot()+
  geom_point(data=russian_group, aes(x=year_of_birth, y=mean, size=count, color=collected.datab))+
  geom_line(data=russian_pred_group, aes(x=year_of_birth, y=pred, linetype=model.predictionb), size=0.8, color='red')+
  theme_bw()+
  scale_color_manual(values=c("#f78e30", "#4581a9"))+
  labs(y = "P(Russian)", size=' Number\n of observations', x='Year of birth', color='Collected data', linetype='Predicted data')+
  scale_size_continuous(range = c(2, 5))+
  guides(color = guide_legend(override.aes = list(size=5)))+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  guides(linetype = guide_legend(keywidth = 1.5, keyheight = 1))

ITM <- ggplot()+
  geom_point(data=ITM_group, aes(x=year_of_birth, y=mean, size=count, color=collected.datab))+
  geom_line(data=ITM_pred_group, aes(x=year_of_birth, y=pred, linetype=model.predictionb), size=0.8, color='red')+
  theme_bw()+
  scale_color_manual(values=c("#f78e30", "#4581a9"))+
  labs(y = "ITM", size=' Number\n of observations', x='Year of birth', color=' Collected data', linetype=' Predicted data')+
  scale_size_continuous(range = c(2, 5))+
  guides(color = guide_legend(override.aes = list(size=5)))+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  guides(linetype = guide_legend(keywidth = 1.5, keyheight = 1))

arr <- ggarrange(ITM, russian, nrow=2, common.legend = TRUE, legend="bottom", label.x=TRUE)
ggsave('plots/fig4.pdf', width = 10, height = 7, arr, dpi=320)


# Fig. 5 ------------------------------------------------------------------

russian_p <- ggplot()+
  geom_ribbon(data=delta_russian_ci, aes(x=X, ymin=low, ymax=high), alpha=0.2)+
  geom_line(data=delta_1, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_7, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_12, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_1000, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_66, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_russian, aes(x=X, y=delta, color='Russian, log-odds'), color='red', size = 1)+
  theme_bw()+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(y='Indirect - Direct')+
  ggtitle('Russian (log odds)')+
  # scale_x_discrete(breaks=1922:1980, limits=1922:1980)
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  ylim(-2, 2)+
  geom_hline(yintercept = 0, size=1, linetype='dashed', color='blue' )

ITM_p <- ggplot()+
  geom_ribbon(data=delta_itm_ci, aes(x=X, ymin=low, ymax=high), alpha=0.2)+
  geom_line(data=delta_2, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_8, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_17, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_1001, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_68, aes(y=delta, x=delta_russian$X), alpha=0.3, size = 1)+
  geom_line(data=delta_itm, aes(x=X, y=delta), color='red', size = 1)+
  theme_bw()+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+
  labs(y='Indirect - Direct')+
  ggtitle('ITM')+
  # scale_x_discrete(breaks=1922:1980, limits=1922:1980)
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  ylim(-0.7, 0.7)+
  geom_hline(yintercept = 0, size=1, linetype='dashed', color='blue' )

hist <- ggplot(russ, aes(x=year_of_birth, fill=type))+
  geom_histogram(position="dodge", bins = length(1922:1980))+
  theme_bw()+
  scale_fill_manual(values=c("#f78e30", "#4581a9"))+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  labs(y = "Number of observations", x='Year of birth', fill='Type')+
  theme(legend.position=c(1,1),legend.justification=c(1,1),
        legend.direction="vertical",
        legend.box="horizontal",
        legend.box.just = c("top"), 
        legend.background = element_rect(fill=alpha('transparent', 0)))

arr <- ggarrange(ITM_p, russian_p, hist, nrow=3, common.legend = FALSE, align = "v")
ggsave('plots/fig5.pdf', width = 10, height = 7, arr, dpi=320)



# Fig. 1 ------------------------------------------------------------------

data <- read.csv('data/all.csv')
data[data$type == 1,]$type = 'Direct'
data[data$type == 0,]$type = 'Indirect'
data$born = 0
data[data$year_of_birth <= 1922,]$born = 'Before 1922'
data[data$year_of_birth >= 1922,]$born = 'After 1922'
levels(data$sex) <- c('Female', 'Male')
val <- max(data$year_of_birth)-min(data$year_of_birth)

data_t <- read.csv('data/all.csv')
new <- dplyr::select(data_t, residence, type, village.population)
new <- group_by(new, residence, village.population)
new_type <- new %>% summarise(mean=mean(type), count=n())


ggplot(new_type, aes(x=count, y=mean))+
  geom_point()+
  # geom_point()+
  labs(y = "Percentage of direct data", x='Number of observations', size=' Village\n population', color='Born')+
  # facet_grid(cols=vars(born))+
  geom_text_repel(aes(label=residence))+
  theme_bw()+
  scale_y_continuous(labels = scales::percent)+
  geom_hline(color='red', yintercept = mean(new_type$mean), linetype='dashed')+
  geom_vline(color='red', xintercept = mean(new_type$count), linetype='dashed')

ggsave('plots/fig1.pdf', width = 8, height = 4, dpi=320)



# Fig. 3 ------------------------------------------------------------------

ggplot(data, aes(x=year_of_birth, fill=type))+
  geom_histogram(bins=val/3, position="dodge")+
  theme_bw()+
  scale_fill_manual(values=c("#f78e30", "#4581a9"))+
  labs(y = "Number of observations", x='Year of birth', fill='Type')+
  # facet_grid(sex ~ .)+
  # geom_point(stat="bin", aes(y=..count..), bins=val)+
  theme(legend.position=c(1,1),legend.justification=c(1,1),
        legend.direction="vertical",
        legend.box="horizontal",
        legend.box.just = c("top"), 
        legend.background = element_rect(fill=alpha('transparent', 0)))

ggsave('plots/fig3.pdf', width = 8, height = 4, dpi=320)



# Fig. 2 ------------------------------------------------------------------

new <- dplyr::select(data, residence, number.of.lang.strat, born, village.population)
new <- group_by(new, residence, born, village.population)
new_c <- new %>% summarise(mean=mean(number.of.lang.strat), count=n())
new_c$mean_count <- 0
new_c[new_c$born == 'After 1922',]$mean_count <- mean(new_c[new_c$born == 'After 1922',]$count)
new_c[new_c$born == 'Before 1922',]$mean_count <- mean(new_c[new_c$born == 'Before 1922',]$count)
new_c$mean_itm <- 0
new_c[new_c$born == 'After 1922',]$mean_itm <- mean(new_c[new_c$born == 'After 1922',]$mean)
new_c[new_c$born == 'Before 1922',]$mean_itm <- mean(new_c[new_c$born == 'Before 1922',]$mean)

new_c$born_т = factor(new_c$born, levels=c('Before 1922','After 1922'))

ggplot(new_c, aes(x=count, y=mean))+
  geom_point()+
  labs(y = "Mean ITM", x='Number of observations', size=' Village\n population')+
  facet_wrap(vars(born_т), scales = "free" )+
  geom_text_repel(aes(label=residence),hjust=0, vjust=0)+
  theme_bw()+
  theme(legend.position=c(1,1),legend.justification=c(1,1),
        legend.direction="vertical",
        legend.box="horizontal",
        legend.box.just = c("top"), 
        legend.background = element_rect(fill=alpha('transparent', 0)))+
  geom_vline(aes(xintercept = mean_count), linetype = "dashed",
             colour = "red")+
  geom_hline(aes(yintercept = mean_itm), linetype = "dashed",
             colour = "red")+
  theme(strip.text=element_text(size=16),
        axis.title=element_text(size=16))+
  theme(legend.key = element_blank(), 
        strip.background = element_rect(colour="transparent", fill="transparent") ) 

ggsave('plots/fig2.pdf', width = 14, height = 7, dpi=320)
