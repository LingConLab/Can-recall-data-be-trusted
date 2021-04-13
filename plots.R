# Loading packages
library(ggplot2)
library(dplyr)
library(sjPlot)
library(grid)
library(ggpubr)
library(rstudioapi)

v1 <- 1922:1980

current_path <- getActiveDocumentContext()$path
setwd(dirname(current_path))
data <- read.csv('data/all.csv')
data[data$type == 1,]$type = 'Direct'
data[data$type == 0,]$type = 'Indirect'
data$born = 0
data[data$year_of_birth <= 1922,]$born = 'Before 1922'
data[data$year_of_birth >= 1922,]$born = 'After 1922'
levels(data$sex) <- c('Female', 'Male')
val <- max(data$year_of_birth)-min(data$year_of_birth)

# Fig. 1 ------------------------------------------------------------

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

ggsave('plots/fig1.pdf', width = 10, height = 2, dpi=320)

# Fig. 2 ------------------------------------------------------------

russian_group <- read.csv('data/scatter_русский.csv')
russian_pred <- read.csv('data/line_русский.csv')
russian_group$collected.datab <- 0
russian_group[russian_group$collected.data == 'direct',]$collected.datab <- 'Direct'
russian_group[russian_group$collected.data == 'indirect',]$collected.datab <- 'Indirect'
russian_pred$model.predictionb <- 0
russian_pred[russian_pred$model.prediction == 'indirect',]$model.predictionb <- 'Indirect'
russian_pred[russian_pred$model.prediction == 'direct',]$model.predictionb <- 'Direct'
ITM_group <- read.csv('data/scatter_number of lang.csv')
ITM_pred <- read.csv('data/line_number of lang.csv')
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
  geom_line(data=russian_pred_group, aes(x=year_of_birth, y=pred, linetype=model.predictionb), size=1, color='red')+
  theme_bw()+
  scale_color_manual(values=c("#f78e30", "#4581a9"))+
  labs(y = "P(Russian)", size=' Number\n of observations', x='Year of birth', color='Collected data', linetype='Predicted data')+
  scale_size_continuous(range = c(1, 3))+
  guides(color = guide_legend(override.aes = list(size=5)))+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  guides(linetype = guide_legend(keywidth = 1.5, keyheight = 1))

ITM <- ggplot()+
  geom_point(data=ITM_group, aes(x=year_of_birth, y=mean, size=count, color=collected.datab))+
  geom_line(data=ITM_pred_group, aes(x=year_of_birth, y=pred, linetype=model.predictionb), size=1, color='red')+
  theme_bw()+
  scale_color_manual(values=c("#f78e30", "#4581a9"))+
  labs(y = "ITM", size=' Number\n of observations', x='Year of birth', color=' Collected data', linetype=' Predicted data')+
  scale_size_continuous(range = c(1, 3))+
  guides(color = guide_legend(override.aes = list(size=5)))+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  guides(linetype = guide_legend(keywidth = 1.5, keyheight = 1))

arr <- ggarrange(ITM, russian, ncol=2, common.legend = TRUE, legend="bottom", label.y=TRUE)
ggsave('plots/fig2.pdf', width = 10, height = 3, arr, dpi=320)


# Fig. 3 ------------------------------------------------------------------

russ <- read.csv('data/russian.csv')
bins <- length(unique(russ$year_of_birth))
russ[russ$type == 1,]$type = 'Direct'
russ[russ$type == 0,]$type = 'Indirect'
delta_russian <- read.csv('data/delta_russian.csv')
delta_russian_ci <- read.csv('data/delta_russian_conf.csv')
delta_russian_perm <- read.csv('delta_russian_perm_gbr_splitted.csv')
delta_russian$X <- sort(unique(russ$year_of_birth))
delta_russian_ci$X <- sort(unique(russ$year_of_birth))
delta_itm <- read.csv('data/delta_ITM.csv')
delta_itm_ci <- read.csv('data/delta_ITM_conf.csv')
delta_itm_perm <- read.csv('delta_itm_perm_gbr_splitted.csv')
delta_itm$X <- sort(unique(russ$year_of_birth))
delta_itm_ci$X <- sort(unique(russ$year_of_birth))

length(delta_russian$X)


russian_p <- ggplot()+
  geom_ribbon(data=delta_russian_ci, aes(x=X, ymin=low, ymax=high), alpha=0.2)+
  geom_line(data=delta_russian, aes(x=X, y=delta, color='Russian, log-odds'), color='red', size = 1)+
  theme_bw()+
  theme(axis.title.y = element_blank())+
  labs(x='Year of birth')+
  ggtitle('Russian (log odds)')+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  ylim(-2.5, 2.5)+
  geom_hline(yintercept = 0, size=0.5, linetype='dashed', color='blue' )

ITM_p <- ggplot()+
  geom_ribbon(data=delta_itm_ci, aes(x=X, ymin=low, ymax=high), alpha=0.2)+
  geom_line(data=delta_itm, aes(x=X, y=delta), color='red', size = 1)+
  theme_bw()+
  labs(y='Indirect - Direct', x='Year of birth')+
  ggtitle('ITM')+
  scale_x_discrete(breaks=1922:1980, limits=c(1922, v1[(!v1%%10)]))+
  ylim(-0.6, 0.6)+
  geom_hline(yintercept = 0, size=0.5, linetype='dashed', color='blue' )

arr <- ggarrange(ITM_p, russian_p, ncol=2, common.legend = FALSE, align = "h")
ggsave('plots/fig3.pdf', width = 10, height = 2, arr, dpi=320)
