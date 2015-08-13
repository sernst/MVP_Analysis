#Total Bases       7    19     25
#Slugging Pct.    10    18     23
#Runs              9    16     23
#OPS               8    17     22
#Batting Avg.      3    11     21
#Home Runs         7    19     21
#Runs Batted In    6    18     20
#Intentional BB    7    13     20
#On-Base Pct.      6    11     18
#Hits              2    10     16
#Bases on Balls    6     8     12
#Stolen Bases      1     3      5

# SLG = (1B + 2*2B + 3*3B + 4*HR)/AB
# OBP = (H+BB+HBP)/(AB+BB+HBP+SF)
# OPS = SLG + OBP

# install.packages("dplyr")
# install.packages("Lahman")
library(dplyr)
library(Lahman)

# Load Data
a_batting <- Batting %>% 
  dplyr::filter(yearID >= 1965, AB >= 0) 

a_teams <- Teams %>% 
  dplyr::filter(yearID >= 1965) %>% 
  dplyr::arrange(yearID, lgID, Rank) %>% 
  dplyr::mutate(
    win_record = ifelse(W >= L, 1, 0), 
    win_100 = ifelse(W >= 100, 1, 0),
    playoff = ifelse((DivWin == "Y"|LgWin == "Y"|WCWin == "Y"), 1, 0) ) 

p_teams <- a_teams %>% 
  dplyr::select(teamID, lgID, yearID, win_record, win_100, playoff)

a_fielding <- Fielding %>% 
  dplyr::filter(yearID >= 1965) 

mvps <- AwardsPlayers %>% 
  dplyr::filter(yearID >= 1965, awardID == "Most Valuable Player") 

gg <- AwardsPlayers %>% 
  dplyr::filter(yearID >= 1965, awardID == "Gold Glove") 

# Summary table and split-year determination
f_batting <- a_batting %>% 
  dplyr::group_by(playerID, yearID) %>% 
  dplyr::summarise(G = sum(G),  
                  AB = sum(AB),
                  R = sum(R),
                  H = sum(H),
                  X2B = sum(X2B),
                  X3B = sum(X3B),
                  HR = sum(HR),
                  RBI = sum(RBI),
                  SB = sum(SB),
                  BB = sum(BB),
                  HBP = sum(HBP),
                  SF = sum(SF),
                  GIDP = sum(GIDP))

team_selection <- a_batting %>% 
  dplyr::select(playerID, yearID, lgID, teamID, G) %>% 
  dplyr::arrange(playerID, yearID, desc(G)) %>% 
  dplyr::group_by(playerID, yearID) %>% 
  dplyr::filter(rank(G, ties.method="first")==1) %>% 
  dplyr::select(-G)

p_final_batting <- f_batting %>% 
  dplyr::filter(AB > 24 ) %>% 
  dplyr::left_join(team_selection, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(BA = H/AB,
                X1B = H - X2B - X3B - HR,
                obp = (H + BB + HBP)/(AB + BB + HBP + SF),
                tb = (X1B + 2*X2B + 3*X3B + 4*HR ),
                slg = (X1B + 2*X2B + 3*X3B + 4*HR )/AB,
                ops = obp + slg) 

m <- mvps %>% dplyr::mutate(mvp2 = 1) %>% dplyr::select(playerID, yearID, mvp2)
g <- gg %>% dplyr::mutate(gg2 = 1) %>% dplyr::select(playerID, yearID, gg2)

final_batting <- p_final_batting %>% 
  dplyr::left_join(m, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(mvp = ifelse(!is.na(mvp2), 1, 0)) %>% 
  dplyr::left_join(g, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(gg = ifelse(!is.na(gg2), 1, 0)) %>% 
  dplyr::select(-mvp2, -gg2) %>% 
  dplyr::left_join(p_teams, by=c("teamID", "yearID", "lgID")) %>% 
  dplyr::select(-X2B, -X1B)

al_final_batting <- final_batting %>% dplyr::filter(lgID=="AL")
nl_final_batting <- final_batting %>% dplyr::filter(lgID=="NL")

# Feature 1: Total HRs
al_final_batting$hrlv <- cut(al_final_batting$HR, c(-.001, 10, 20, 30, 35, 40, 45, 50, max(al_final_batting$HR)))
al_final_batting$hrlv <- cut(al_final_batting$HR, 
                             c(-.001, 30, 35, 40, 45, max(al_final_batting$HR)), labels = c(1:5))

biv_al_hr <- al_final_batting %>% 
  dplyr::group_by(hrlv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(hrlv)

# Feature 2: Batting Average (BA)
al_final_batting$balv <- cut(al_final_batting$BA, c(-.001, .10, .20, .250, .275, .30, .325, .35, .375,  max(al_final_batting$BA)))
al_final_batting$balv <- cut(al_final_batting$BA, c(-.001, .30, .325,   max(al_final_batting$BA)), labels = c(1:3))

biv_al_ba <- al_final_batting %>% 
  dplyr::group_by(balv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(balv)

z <- al_final_batting %>% dplyr::filter(mvp == 1, BA < .201)

# Feature 3: On-Base Percentage (OBP)
al_final_batting$obplv <- cut(al_final_batting$obp, c(-.001, .10, .20, .250, .275, .30, .325, .35, .375,  max(al_final_batting$obp)))
al_final_batting$obplv <- cut(al_final_batting$obp, c(-.001, .375,   max(al_final_batting$obp)), c(0:1))

biv_al_obp <- al_final_batting %>% 
  dplyr::group_by(obplv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(obplv)

# Feature 4: Total Bases (TB)
al_final_batting$tblv <- cut(al_final_batting$tb, c(-.001, 50, 100, 200, 300, 400, 500, max(al_final_batting$tb)))
al_final_batting$tblv <- cut(al_final_batting$tb, c(-.001, 300,  350, max(al_final_batting$tb)), labels = c(1:3))

biv_al_tb <- al_final_batting %>% 
  dplyr::group_by(tblv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(tblv)

# Feature 5: Runs Batted In (RBI)
al_final_batting$rbilv <- cut(al_final_batting$RBI, c(-.001, 25, 50, 75, 100, 125, max(al_final_batting$RBI)))
al_final_batting$rbilv <- cut(al_final_batting$RBI, c(-.001, 100,  125, max(al_final_batting$RBI)), labels = c(1:3))

biv_al_rbi <- al_final_batting %>% 
  dplyr::group_by(rbilv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(rbilv)

z <- al_final_batting %>% dplyr::filter(RBI == 165)

# Feature 6: On-Base Percentage + Slugging (OPS)
al_final_batting$opslv <- cut(al_final_batting$ops, c(-.001, .10, .20, .250, .300, .325, .375, .500, .750, 1., 1.25, 2, 3, 4, max(al_final_batting$ops)))
al_final_batting$opslv <- cut(al_final_batting$ops, c(-.001, 1, max(al_final_batting$ops)), labels = c(0:1))

biv_al_ops <- al_final_batting %>% 
  dplyr::group_by(opslv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(opslv)

# Feature #3 Slugging
al_final_batting$slglv <- cut(al_final_batting$slg, c(-.001, .10, .20, .250, .300, .325, .375, .500, .750, max(al_final_batting$slg)))
al_final_batting$slglv <- cut(al_final_batting$slg, c(-.001,  .500, max(al_final_batting$slg)), labels = c(0:1))

biv_al_slg <- al_final_batting %>% 
  dplyr::group_by(slglv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(slglv)

# Feature #3 Stolen Bases (SB)
al_final_batting$sblv <- cut(al_final_batting$SB, c(-.001, 25, 50, 75, 100, 125, max(al_final_batting$SB)))
al_final_batting$sblv <- cut(al_final_batting$SB, c(-.001, 50, max(al_final_batting$SB)), labels = c(0:1))

biv_al_sb <- al_final_batting %>% 
  dplyr::group_by(sblv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(sblv)

# Feature #3 Double Plays (GIDP)
al_final_batting$dplv <- cut(al_final_batting$GIDP, c(-.001, 10, 20, 30, max(al_final_batting$GIDP)))
al_final_batting$dplv <- cut(al_final_batting$SB, c(-.001, 50, max(al_final_batting$SB)), labels = c(0:1))

biv_al_dp <- al_final_batting %>% 
  dplyr::group_by(dplv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(dplv)

z <- al_final_batting %>%  dplyr::filter(mvp == 1, GIDP > 30)


biv_al_wr <- al_final_batting %>% 
  dplyr::group_by(win_record) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(win_record)

biv_al_wh <- al_final_batting %>% 
  dplyr::group_by(win_100) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(win_100)

biv_al_po <- al_final_batting %>% 
  dplyr::group_by(playoff) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(playoff)
# FIELDING FEATURES

f_fielding <- a_fielding %>% 
  dplyr::group_by(playerID, yearID) %>% 
  dplyr::summarise(G = sum(G),  
                  InnOuts = sum(InnOuts),
                  PO = sum(PO),
                  A = sum(A),
                  E = sum(E) )

team_selection <- a_fielding %>% 
  dplyr::select(playerID, yearID, lgID, teamID, G) %>% 
  dplyr::arrange(playerID, yearID, desc(G)) %>% 
  dplyr::group_by(playerID, yearID) %>% 
  dplyr::filter(rank(G, ties.method="first")==1) %>% 
  dplyr::select(-G)

p_final_fielding <- f_fielding %>% 
  dplyr::left_join(team_selection, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(def = (PO + A)/ InnOuts)

final_fielding <- p_final_fielding %>% 
  dplyr::left_join(m, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(mvp = ifelse(!is.na(mvp2), 1, 0)) %>% 
  dplyr::left_join(g, by = c("playerID", "yearID")) %>% 
  dplyr::mutate(gg = ifelse(!is.na(gg2), 1, 0)) %>% 
  dplyr::select(-mvp2, -gg2) %>% 
  dplyr::left_join(p_teams, by=c("teamID", "yearID", "lgID")) %>% 
  dplyr::filter(!is.na(InnOuts))

final_fielding$deflv <- cut(final_fielding$def, c(-.001,  .05, .075,  .15, max(final_fielding$def)))


fit.1 <- glm(mvp ~ balv + hrlv + obplv + rbilv + tblv+ win_100, data=al_final_batting, family = binomial(logit)); summary(fit.1)
fit.2 <- glm(mvp ~ BA  + RBI + tb  +  win_record, data=al_final_batting, family = binomial()); summary(fit.2)
fit.3 <- glm(mvp ~ balv + hrlv + obplv + rbilv + slglv, data=al_final_batting, family = binomial()); summary(fit.3) 
fit.4 <- glm(mvp ~ balv + hrlv + rbilv + slglv, data=al_final_batting, family = binomial()); summary(fit.4)
str(al_final_batting)
as.factor(al_final_batting$mvp)

al_final_batting <- al_final_batting %>% 
  dplyr::mutate(pr = 1/(1+exp(-(-19.37878 + BA*18.08606 + RBI*.02565 + tb*.01948 + 2.15797*win_record))))

al_final_batting$prlv <- cut(al_final_batting$pr, seq(0,1,.1))

biv_al_pr <- al_final_batting %>% 
  dplyr::group_by(prlv) %>% 
  dplyr::summarise(ct = n(), mvp = sum(mvp), m = mean(mvp)) %>% 
  dplyr::arrange(prlv)


