* Diane-jbc.do 
* Stata version 15

* 1: DATA SET

* (3) PANEL DATA estimators and TIME-INVARIANT variables:
* Endogeneity with alpha(i) time invariant country(i) random effects
* 3A: DATA STEP: within and between transformed variables
* 3B: PANEL DATA UNIVARIATE STATISTICS 
* 3C: WITHIN and BETWEEN SIMPLE BIVARIATE CORRELATIONS
* 3D: FIRST DIFF, WITHIN, BETWEEN, MUNDLAK ESTIMATOR
*     UPWARD TESTING PROCEDURE OF EXOGENOUS REGRESSORS
* 3E: INSPECTION OF RESIDUALS: BOXPLOT per medapolicy
* 3F: PRETEST Hausman Taylor ESTIMATOR: endogenous time invariant ICRGE

* (2) POOLED OLS REGRESSIONS and SPURIOUS INTERACTION TERM
* 2A: REPLICATION OF BD (4) and CR (2) OLS REGRESSIONS
* 2B: REPLICATION OF CR GRAPHS p-values from N=275 to N=269
* 2C: DFBETA*LEVERAGE 
* 2D: SPURIOUS PAIR of regressors with interaction term
* 2E: VIF PIF highly collinear pair
* 2F: Contribution to R2 and power
* 2G: Robust regressions Quantile regressions



********** CAPTURE la LOG **********
* CAPTURE LA LOG: PROGRAMME ET RESULTAT  probleme de chemin d'acces
* OUVRIR d'abord en lançant un DO file du repertoire utilisé comme référence
* par la suite.
capture log close
log using Diane.txt, text replace
********** SETUP **********
*set more off
clear all
set linesize 90
set scheme s1mono  /* Graphics scheme */
* DATA=diane
use C:\Users\jbchatelai\Documents\Panel\diane\diane.dta, clear


/******* 1: XTDESCRIBE
sorted siren year
N=955913 firms balanced T=5 years 2014-2018
36 + 32 + 1 only one observation
   Freq.  Percent    Cum. |  Pattern
 ---------------------------+---------
   955913     99.99   99.99 |  11111
       36      0.00  100.00 |  ...1.
       32      0.00  100.00 |  ..1..
        1      0.00  100.00 |  .1...
 ---------------------------+---------
   955982    100.00         |  XXXXX
k=93 variables
N=1834 HT haute technologie
   */

* PROC CONTENTS, number of variables
describe, short
describe, simple
describe, fullnames

* Panel description of dataset: CHECK IF BALANCED (10111...)
*sort siren year
xtset siren year
xtdescribe if (totalassets>=1)& (totalassets != .), patterns(50)


/**** 2: CHECK ACCOUNTING VARIABLES

*** ASSETS ***

totalassets
totalfixedassets

*** long term assets ***

	NetIntangible
    goodwill   
	othIntangAs     
	
	nettangible 
	land    
	buildings
	plantAequip 
	other_tangible 
	PropPlEq_inPRG 
    prepay_tangibleAs
	
****short run assets ***
*** Inventories are detailed
**** Trade receivable are creditors ??

currentas

inventory    
rawmaterials  
workinprogr  
ServINprogr  
semifinNfinGoods
goodforsales
customerprepay 

creditors

marketable_sec 
cashNbank   


*** LIABILITIES
**** Tradedebt is trade payable?
**** Retained earnings is missing?
**** Taxes: are they short run taxes in liabilities

financialdebtequity
debttosupplier_tangAs

totalDebt  

sharecapital

netincome   
convertibleloans
otherdebentureloans
bankborrowings
otherborrowings
tradedebts
taxes 
otherdebts  


**** RATIOS

captem_fa   (capital employed to fixed assets).
wc_currentas
currentratio


**** INCOME STATEMENT

netsales
purch_good  
purch_raw  
wage_salaries 
fincharges
totalrevenues 
totalexpenses 
netincome   

WHAT IS "consolidated investment"
conso_insvestm  



*** PERFORMANCE SOLVENCY ***

roa
solvencyratio
InterestR


*** AVERAGE SIZE period not known ***

effectifmoyendupersonnel

*/


/**** 3. FILTER ON SME vs BIG vs DOT
SME: 
Less than 250 employees, 
Turnover below Euros 50M 
Total Assets 43Million Euros 
Definition 2016
https://ec.europa.eu/regional_policy/sources/conferences/state-aid/sme/smedefinitionguide_en.pdf
Unite de compte DIANE: kEur, 43Millions Euros =43000
*/

* SIZE1 employees: Not enough observations 7780000 given with 761000 below 250 employees 16.000 over 250 employees
* just remove BIG1
tabstat effectifmoyendupersonnel, stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p90 p95 p99) col(stat), 
gen SME1 = ((effectifmoyendupersonnel<=250) & (effectifmoyendupersonnel>0) & (effectifmoyendupersonnel != .))
tabulate SME1 if (effectifmoyendupersonnel != .)
gen BIG1 = ((effectifmoyendupersonnel>250) & (effectifmoyendupersonnel != .))
tabulate BIG1 if (netsales != .)


/* SIZE2 netsales < 50 000 kE: Big 1.18% 31000+2.661.811  
Annual turnover is determined by calculating the income that an enterprise received during the year in question 
from the sale of products and provision of services falling within the company’s ordinary activities,
after deducting any rebates. 
Turnover should not include value added tax (VAT) or other indirect taxes (3).
*/
tabstat netsales , stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p90 p95 p99) col(stat)
gen SME2 = ((netsales<=50000) & (netsales>=0) & (netsales != .))
tabulate SME2 if (netsales != .)
gen BIG2 = ((netsales>50000) & (netsales != .))
tabulate BIG2 if (netsales != .)

* SIZE3 totalassets < 43 000 kE: 1.6% (43700+2.680.556)
* strictly positive for ratio and for log(totalassets) for size: eliminate 5034+139 observations
* No observations 0<TA<1 so OK for log(TA)
* 5000 à TA<1 (0.11%) (toujours éliminées dans les régressions avec ln(TA)).
tabstat totalassets , stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p90 p95 p99) col(stat)
gen SME3 = ((totalassets<=43000) & (totalassets>=1) & (totalassets != .))
tabulate SME3 if (totalassets != .)
gen BIG3 = ((totalassets>43000) & (totalassets != .))
tabulate BIG3 if (totalassets != .)
gen zerota = (totalassets==0)
tabulate zerota
gen negta = (totalassets<0)
tabulate negta
gen inf1ta = ((totalassets>0)  & (totalassets<1) & (totalassets != .))
tabulate inf1ta


* Synthesis NT=2.424.836 for SMEs
gen SME123 = (BIG1==0) & (SME2==1) & (SME3==1)
tabulate SME123 
xtdescribe if (SME123==1) , patterns (50)	
xtset siren year

xtdescribe if (totalassets>=1)& (totalassets != .), patterns(50)



/**** 4. FILTERS ON ODD NEGATIVE SIGNS
UNRELIABLE accounting negative values:
599 à Cash<0 (0.01%), 15000 à Cash=0
265 à marketable_sec<0 (0.01%).
79 à totaldebt<0
1119 à netsales<0 (net can be negative)
247.000 avec zero net sales (5%)
BALANCED: eliminate single observations: LAGS and GROWTH do exist
REMOVE p1 and p99 for all variables
MISSING VALUES in the variable of the model.
*/
* FILTER INSTRUCTIONS IN STATA
* keep if year==2014|year==2015
* drop if p2p==1 & year==2014

gen Fmarketable_sec = ((marketable_sec>=0) & (marketable_sec !=.) )
gen FcashNbank = ((cashNbank>=0) & (cashNbank != .))
gen FtotalDebt = ((totalDebt>=0) & (totalDebt != .))

tabulate Fmarketable_sec

gen F123 = (Fmarketable_sec ==1) & (FcashNbank ==1) & (FtotalDebt==1)

tabulate Fmarketable_sec if F123 == 1 & SME123 == 1


/**** 6.DIVIDE BY TOTAL ASSETS, LAG and GROWTH
*/
*Stats for existing data

tabstat totalassets cashNbank marketable_sec netincome, stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p90 p95 p99) col(stat)
tabstat wc_currentas currentratio currentas creditors inventory, stat (count mean p50 skew min max sd variance kurt p10 p90 ) col(stat)    

* GEN Compute and cash equivalent as marketable securities
* Compute and cash equivalent as marketable securities

gen Dum14 = (year==2014)
gen Dum15 = (year==2015)
gen Dum16 = (year==2016)
gen Dum17 = (year==2017)
gen Dum18 = (year==2018)
gen lnta = ln(totalassets) if F123 == 1 & SME123 == 1
gen netincometa = netincome/totalassets if F123 == 1 & SME123 == 1
gen tdta = totalDebt/totalassets if F123 == 1 & SME123 == 1 
* compute working capital: inventories + trade receivable(creditor) + (cash) - trade payables (tradedebts) - tax 
gen NWC = (inventory + creditors - tradedebts - taxes - otherdebts)/totalassets  
gen inventoryTA = inventory/totalassets  
gen creditorsTA = creditors/totalassets  
gen tradedebtsTA = tradedebts/totalassets  
gen taxesTA = taxes/totalassets  
gen otherdebtsTA = otherdebts/totalassets  

tabstat NWC inventoryTA creditorsTA tradedebtsTA taxesTA otherdebtsTA , stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p25 p50 p75 p90 p95 p99 ) col(stat)


/**** 5. Panel LAGS CASH and GROWTH SALES, TANGIBLES  
Compute and cash equivalent as marketable securities
by siren: gen LcashTA = cashTA[_n-1] if year==year[_n-1]+1
OLS: R2=67.53% lag cash only
*/

gen cashta  = (marketable_sec + cashNbank)/totalassets if F123 == 1 & SME123 == 1
tabstat cashta, by (year) stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p25 p75 p90 p95 p99 ) col(stat)
xtset siren year
gen Lcashta1 = L.cashta if cashta<0.95
* 553 549 firms, 64.000 balanced firms (13%).
xtdescribe if ((SME123==1) & (LcashTA != .) & (F123==1) ) , patterns (50)	

tabstat cashta Lcashta1 if ((LcashTA != .) & (cashta<0.95)), by (year) stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p25 p75 p90 p95 p99 ) col(stat)

tabstat NWC inventoryTA creditorsTA tradedebtsTA taxesTA otherdebtsTA , stat (count mean p50 skew min max sd variance kurt p1 p5 p10 p25 p50 p75 p90 p95 p99 ) col(stat)

* GROWTH OF SALES
* beaucoup moins d'outlier avec la version continue de la croissance
* mediane GCsales .0228966

gen Lsales = L.netsales
gen Gsales = (netsales - Lsales )/ Lsales
gen GCsales = log(netsales) - log(Lsales)
list siren  year netsales Lsales Gsales GCsales in 1/100, clean
list cashTA L.cashTA netsales Lsales Gsales in 1/20, clean
tabstat Gsales GCsales DGCsales , stat (count mean p50 skew min max sd variance kurt p10 p90 ) col(stat), by year


/* Dummies for medians to interact with lag(cash)
********
(high) sales growth
(high) increase in fixed assets (not growth?)
(small) ln(ta) (size)
(low) cash-flow
(D-low?) coverage ratio
(D-low?) Z-score
*******
medians for dummies
lnta  6.028278
tdta .5635711 
netincometa .0444444
*/

gen DSMALL = (lnta<6.028278)
gen DLOWCFLOW = (netnicometa<.0444444)
gen DGCsales = (GCsales>0.0228966)
tabstat Gsales GCsales DGCsales , stat (count mean p50 skew min max sd variance kurt p10 p90 ) col(stat)

* Dummies interaction terms
gen DGCsalesLcashTA = DGCsales*LcashTA 

list siren  year cashTA DSMALL DLOWCFLOW Dum14-Dum18 in 1/20, clean


**** 6. SAVE SMALLER DATABASE OLD FORMAT for Exercises
SELECT SUBSAMPLES 
keep if year==2014
drop if p2p_pre==0 & p2p_total==1
deprtcode
regioncode
*/

tabulate regioncode
tabulate deprtcode
tabulate nafrev2primarycodecode
tabulate nacerev2primarycodecode
tabulate noofshareholders
tabulate numberofbranches
tabulate region regioncode
tabulate bankname
tabulate man trade 
tabulate elec_eau agr
tabulate trans ict
tabulate real cons 
tabulate services
tabulate HT_all KIS_all
tabulate FKIS OKIS
tabulate KIS HTKIS 
tabulate HT MHT
tabulate MLT LT


keep if SME123==1 & F123==1  
drop ÿþmarquée
saveold DianeSME123










/**** 7. ECONOMETRICS AR(1) PANEL
Pas d'effet 1,3 million, N=574000 firms, T=2.3 average observations (no winsorize)
The large AR(1) is only average of crbetween subspace
R2 between = 79%, Beta = 0.9, dimension between: N=574.000
R2 random= ?, Beta=0.6
R2 fixed effects = 0.02% Beta=-0.04, dimension within: N(T-1)=574.000 * 2.3 
AR Bond, IV Beta=-0.04 Instrument D.LCashTA 406.973, T=1.8 Number of observations
First diff= first diff lag= lose t-1, t-2 THEN Lag(t-2): lose 
note: LcashTA dropped because of collinearity

Arellano-Bond dynamic panel-data estimation     Number of obs     =    756,346
Group variable: siren                           Number of groups  =    406,973
Time variable: year
                                                Obs per group:
                                                              min =          1
                                                              avg =   1.858467
                                                              max =          3

Number of instruments =      8                  Wald chi2(1)      =       0.42
                                                Prob > chi2       =     0.5190
Two-step results
                                  (Std. Err. adjusted for clustering on siren)
------------------------------------------------------------------------------
             |              WC-Robust
      cashTA |      Coef.   Std. Err.      z    P>|z|     [95% Conf. Interval]
-------------+----------------------------------------------------------------
      cashTA |
         L1. |  -.0399895   .0620057    -0.64   0.519    -.1615184    .0815395
             |
       _cons |   .2369249   .0138914    17.06   0.000     .2096982    .2641516
------------------------------------------------------------------------------
Instruments for differenced equation
        GMM-type: L(2/.).cashTA
        Standard: D.LcashTA
Instruments for level equation
        Standard: _cons
DOWNLOAD xtabond2: in the stata command line:
search xtabond2
nomata: without using mata (if your version has mata, go on with mata)
noleveleq = Arellano Bond first diff equation only
Very lengthy estimation
*/

/* Code 
keep if var == 1
reg y x
*/

pwcorr cashTA LcashTA if SME123==1

reg cashTA LcashTA Dum14-Dum17 if SME123==1
xtreg cashTA LcashTA if SME126==1 , be
xtreg cashTA LcashTA , re
xtreg cashTA LcashTA , fe
xtabond cashTA LcashTA , twostep vce(robust)

* does not converge
* xtabond2 cashTA L.(cashTA) , gmm (L.(cashTA),collapse) noleveleq robust nomata twostep 


reg cashTA LcashTA DGCsalesLcashTA DGCsales GCsales lnta NWC tdta netincometa

xtreg cashTA LcashTA DGCsalesLcashTA DGCsales GCsales lnta NWC tdta netincometa ,fe

xtreg cashTA LcashTA DGCsalesLcashTA DGCsales GCsales lnta NWC tdta netincometa , be

* 1,6 million observations.
reg netsales Lsales

* 1,5 million observations
reg netsales Gsales














/**** 6. Compute WITHIN BETWEEN TWO-WAY projections
*/
* TO BE ADAPTED Detecting time invariant variables in the sample 
* before computing within: within and between variation
* NOT THE CORRECT NUMBER OF OBSERVATIONS FOR WITHIN, VARIANCE MISSING
xtsum ident icrge ssa easia lgdp2 ethnf 
xtsum year gdpg eda policy gdp lgdp govc assas m2_1 lpop bb infl sacw 


* Declare individual identifier and time identifier (PROC SORT ident year)
* Already sorted by siren year:
* xtset siren year
* compute the BETWEEN Transformed variables

by ident: egen mgdpg    = mean(gdpg)
by ident: egen mmeda    = mean(eda)
by ident: egen mpolicy  = mean(policy)
by ident: egen mm2_1    = mean(m2_1)
by ident: egen mlgdp    = mean(lgdp)
by ident: egen massas   = mean(assas)
by ident: egen methnfassas   = mean(ethnfassas)
by ident: egen medapolicy    = mean(edapolicy)
by ident: egen meda2policy    = mean(eda2policy)

* compute the WITHIN tranformed variables
gen wgdpg   =   gdpg   - mgdpg
gen weda    =   eda    - mmeda
gen wpolicy =   policy - mpolicy
gen wm2_1   =   m2_1   - mm2_1
gen wlgdp   = lgdp - mlgdp
gen wassas  =   assas  - massas
gen wethnfassas = ethnfassas - methnfassas
gen wedapolicy  = edapolicy - medapolicy
gen weda2policy = eda2policy - meda2policy

* LABEL
label variable mgdpg "gdpg(i.)"

correlate gdpg mgdpg wgdpg
* PROBLEM for within transformed time invariant
* WITH WEIGHTS FOR UNBALANCED PANEL WITH TIME INVARIANT
* OR ROUNDING 
* icrge and ethnf: NON ZERO CORRELATION IN WITHIN wicrge micrge  
correlate icrge wicrge wgdpg micrge methnf ethnf

*list country year micrge wicrge icrge
* problem Argentina 3 missing data govc
*list country year govc mgovc wgovc in 1/30 

* Create a set of indicator variables
xi i.ident, noomit
* DID NOT WORK: varlist p.49
xi i.ident*eda, noomit
xi i.ident*policy, noomit
* DID NOT WORK p.49
*xi j.year, noomit prefix(j)
*quietly tabulate ident, generate(IDdummy)

*/

/**** 7. Descriptive statistics WITHIN BETWEEN TWO-WAY projections WINSORIZE
*/

/**** 8. Correlation matrix WITHIN BETWEEN TWO-WAY projections
*/

/**** 9. Estimations Mundlak and IV
*/

/**** 10. Dfbetas dummies, correlation matrix and logit/probit.
*/


******************************
END OF CODE
***************************************



* PROC BOXPLOT: too much time consuming
graph box cashta marketsecta cashbta totalassets lnta, over(year) 
graph box gdpg, over(ident)
graph box gdpg, over(mgdpg)
graph box eda, over(country3)
graph box eda gdpg, over(mmeda) 
graph box policy, over(country3) 
graph box policy gdpg, over(mpolicy)

* PREPARING THE SPURIOUS OUTLIER DRIVEN EFFECTS
graph box eda , over(mmeda)
graph box policy, over(mpolicy) 
graph box edapolicy , over(medapolicy)
graph box eda2policy , over(meda2policy)



**** DESCRIPTIVE STATISTICS WITHOUT PANEL DATA STRUCTURE ****

* PROC PRINT... (OBS=10) Organization of dataset
list siren sirenID year companyname in 1/20, clean
* PROC FREQ: number of periods per country
* xttab similar result
tabulate region
tabulate deprtcode
tabulate year
tabulate bankname
tabulate HT year
tabulate typeofbusiness 



* PROC UNIVARIATE: tabstat
tabstat brevet, stat (mean p50 sd count) col(var)
tabstat roa , stat (count mean p50 skew min max sd variance  kurt ) col(stat)

tabstat effectifmoyendupersonnel totalassets , stat (count mean p50 skew min max sd variance  kurt ) col(stat)

correlate effectifmoyendupersonnel totalassets netsales

list siren sirenID year companyname in 1/20, clean

************************************************
************************************************
************************************************


* gdpg is multiplied by 100: 6 is for 6%
list country year gdpg lgdp in 1/100


sort country year
list country3 year country
sort edapolicy
list country3 year country edapolicy eda2policy





reg taxes totalDebt netincome brevet
correlate taxes totalDebt netincome brevet


* Panel description of dataset: CHECK IF BALANCED (10111...)
*sort siren year
xtset siren year
xtdescribe
 
* Panel tabulation for (ONLY ONE?) QUALITATIVE variable : PROC FREQ
xttab year
xttab ident
xttab icrge 
xttab ssa
xttab easia 
* Transition probabilities for a variable: PROC FREQ X LagX
xttrans year, freq

* Detecting time invariant variables in the sample 
* before computing within: within and between variation
* NOT THE CORRECT NUMBER OF OBSERVATIONS FOR WITHIN, VARIANCE MISSING
xtsum ident icrge ssa easia lgdp2 ethnf 
xtsum year gdpg eda policy gdp lgdp govc assas m2_1 lpop bb infl sacw 



***** 2A: REPLICATION OF BD DESCRIPTIVE STATISTICS

* TABLE 2, p.853: descriptive statistics
* PROC UNIVARIATE: tabstat
tabstat gdpg eda policy gdp, stat (mean p50 sd count) col(var)
tabstat gdpg eda policy gdp, stat (count mean p50 skew min max sd variance  kurt ) col(stat)
* gdpg is multiplied by 100: 6 is for 6%
list country year gdpg lgdp in 1/100

* TABLE A2 Country specific statistics
* Ordered per GDP growth Ordered per Aid





//////////prepare data to regress p2p borrowing dummy by firms charactersitics a year before borrowing//////////////////
keep if year==2014|year==2015

drop if p2p==1 & year==2014

/////save as 2014-2015.dta

/////mark in 2014 firms that borrow in 2015//
sort siren year
by siren: egen p2p_pre=total(p2p)
tab year if p2p_pre==1

keep if year==2014
drop if p2p_pre==0 & p2p_total==1

//////save as 2015-preptreat ////
///repeat this process with 2015-2016 & 2016-2017 ///
//// append 2015-pretreat 2016-pretreat 2017-pretreat ////
/// I winsorized all variables at (1 99)//
/// balance sheet variables are scaled by total assets//
/// trade is industry///
/// departdummy is dummy for geographical department ////

//// our final model probit/////
probit p2p_pre age size size2 roe growthTA growthsales tangible_TA patent_TA Goodwill_TA currentratio cashMKTsec_TA inventory_TA totalDebt_TA bankborr_TA InterestRate trade departdummy6 departdummy7 departdummy11 departdummy13 departdummy15 departdummy24 departdummy25 departdummy29 departdummy30 departdummy32 departdummy33 departdummy34 departdummy35 departdummy36 departdummy37 departdummy43 departdummy53 departdummy55 departdummy56 departdummy58 departdummy59 departdummy63 departdummy65 departdummy68 departdummy71 departdummy72 departdummy73 departdummy74 departdummy75 departdummy76 departdummy77 departdummy80 departdummy82 departdummy83 departdummy85 departdummy88 departdummy90 departdummy91 departdummy92 departdummy93



******* 3A. DATA step: BETWEEN and WITHIN transformed variables

* Detecting time invariant variables in the sample 
* before computing within: within and between variation
* NOT THE CORRECT NUMBER OF OBSERVATIONS FOR WITHIN, VARIANCE MISSING
xtsum ident icrge ssa easia lgdp2 ethnf 
xtsum year gdpg eda policy gdp lgdp govc assas m2_1 lpop bb infl sacw 


* Declare individual identifier and time identifier (PROC SORT ident year)
xtset ident year
* compute the BETWEEN Transformed variables
by ident: egen mgdpg    = mean(gdpg)
by ident: egen mmeda    = mean(eda)
by ident: egen mpolicy  = mean(policy)
by ident: egen mm2_1    = mean(m2_1)
by ident: egen mlgdp    = mean(lgdp)
by ident: egen massas   = mean(assas)
by ident: egen methnfassas   = mean(ethnfassas)
by ident: egen medapolicy    = mean(edapolicy)
by ident: egen meda2policy    = mean(eda2policy)

* USELESS
by ident: egen mgovc    = mean(govc)
by ident: egen micrge   = mean(icrge)
by ident: egen methnf   = mean(ethnf)
* compute the WITHIN tranformed variables
gen wgdpg   =   gdpg   - mgdpg
gen weda    =   eda    - mmeda
gen wpolicy =   policy - mpolicy
gen wm2_1   =   m2_1   - mm2_1
gen wlgdp   = lgdp - mlgdp
gen wassas  =   assas  - massas
gen wethnfassas = ethnfassas - methnfassas
gen wedapolicy  = edapolicy - medapolicy
gen weda2policy = eda2policy - meda2policy

* USELESS
gen wgovc   =   govc   - mgovc
gen wicrge   =  icrge   - micrge
gen wethnf   =  ethnf   - methnf
* LABEL
label variable mgdpg "gdpg(i.)"

correlate gdpg mgdpg wgdpg
* PROBLEM for within transformed time invariant
* WITH WEIGHTS FOR UNBALANCED PANEL WITH TIME INVARIANT
* OR ROUNDING 
* icrge and ethnf: NON ZERO CORRELATION IN WITHIN wicrge micrge  
correlate icrge wicrge wgdpg micrge methnf ethnf

*list country year micrge wicrge icrge
* problem Argentina 3 missing data govc
*list country year govc mgovc wgovc in 1/30 

* Create a set of indicator variables
xi i.ident, noomit
* DID NOT WORK: varlist p.49
xi i.ident*eda, noomit
xi i.ident*policy, noomit
* DID NOT WORK p.49
*xi j.year, noomit prefix(j)
*quietly tabulate ident, generate(IDdummy)

*summarize _i*
* DID not work: other interaction terms

* PROC CONTENTS
describe

* CREATE IDENT2, ordering countries by MEANS of LNCARN(i.)

* Dataset: PROC PRINT var1 var2 (OBS=40)
list country ident gdpg eda in 1/40, clean
* Overall Dataset: PROC PRINT (OBS=3)
list in 1/3, clean

***** 3A: Not useful yet
 
* Summary of dataset: PROC MEANS
sort country year
by country: summarize gdpg eda policy edapolicy icrge 

* Summary of dataset: PROC MEANS
sort country
by country: summarize country gdpg eda policy edapolicy icrge 

* PROC FREQ: number of periods per country
tabulate mmeda
tabulate medapolicy
tabulate meda2policy

* PROC PRINT OLS outliers edapolicy
sort edapolicy
list country year edapolicy medapolicy in 1/132 
list country year edapolicy medapolicy in 133/275 

* PROC PRINT Between outliers edapolicy
sort medapolicy edapolicy
list country year edapolicy medapolicy 

* PROC UNIVARIATE: tabstat
sort country year
by country: tabstat gdpg eda policy icrge, stat (count mean p50 skew min max sd variance kurt) col(stat) 

* PROC BOXPLOT
graph box gdpg eda policy, over(year) 
graph box gdpg, over(ident)
graph box gdpg, over(mgdpg)
graph box eda, over(country3)
graph box eda gdpg, over(mmeda) 
graph box policy, over(country3) 
graph box policy gdpg, over(mpolicy)

* PREPARING THE SPURIOUS OUTLIER DRIVEN EFFECTS
graph box eda , over(mmeda)
graph box policy, over(mpolicy) 
graph box edapolicy , over(medapolicy)
graph box eda2policy , over(meda2policy)


**** 3B: PANEL DATA UNIVARIATE HISTOGRAMS AND STATISTICS

* PROC UNIVARIATE, HISTOGRAM
* time series operators not allowed
* Non normality of Between distributions including dependent
histogram gdpg, width(0.25) kdensity normal
kdensity gdpg, bwidth(0.20) normal n(4000)
kdensity eda, bwidth(0.20) normal n(4000)
kdensity policy, bwidth(0.20) normal n(4000)
kdensity mgdpg, bwidth(0.20) normal n(4000)
kdensity meda, bwidth(0.20) normal n(4000)
kdensity mpolicy, bwidth(0.20) normal n(4000)
kdensity wgdpg, bwidth(0.20) normal n(4000)
kdensity weda, bwidth(0.20) normal n(4000)
kdensity wpolicy, bwidth(0.20) normal n(4000)

histogram gdpg, width(0.25) kdensity normal
histogram mgdpg, width(0.25) kdensity normal
histogram wgdpg, width(0.25) kdensity normal
histogram eda, width(0.25) kdensity normal
histogram mmeda, width(0.25) kdensity normal
histogram weda, width(0.25) kdensity normal
histogram policy, width(0.25) kdensity normal
histogram mpolicy, width(0.25) kdensity normal
histogram wpolicy, width(0.25) kdensity normal
histogram edapolicy, width(0.25) kdensity normal
histogram medapolicy, width(0.25) kdensity normal
histogram wedapolicy, width(0.25) kdensity normal
histogram eda2policy, width(0.25) kdensity normal
histogram meda2policy, width(0.25) kdensity normal
histogram weda2policy, width(0.25) kdensity normal
histogram mlgdp, width(0.25) kdensity normal
histogram wlgdp, width(0.25) kdensity normal
histogram mm2_1, width(0.25) kdensity normal
histogram wm2_1, width(0.25) kdensity normal

* PROC UNIVARIATE: tabstat ANALYSIS of variance Within Between
tabstat gdpg wgdpg mgdpg policy wpolicy mpolicy lgdp wlgdp mlgdp m2_1  wm2_1 mm2_1 ///
eda weda mmeda edapolicy wedapolicy medapolicy eda2policy weda2policy meda2policy  ///
assas wassas massas ethnfassas wethnfassas methnfassas ///
icrge wicrge ssa easia ethnf wethnf , ///
stat (count variance sd mean ) col(stat)

* PROC UNIVARIATE: tabstat Within
tabstat wgdpg wpolicy wlgdp wm2_1 weda wedapolicy weda2policy ///
wassas wethnfassas, ///
stat (count mean sd min p5 p95 max p50 skew variance kurt ) col(stat)

* PROC UNIVARIATE: tabstat Between
tabstat mgdpg mpolicy mlgdp mm2_1 meda medapolicy meda2policy ///
massas methnfassas ethnf icrge ssa easia, ///
stat (count mean sd min p5 p95 max  p95 p50 skew variance kurt ) col(stat)



*** 3C: WITHIN BETWEEN OLS bivariate correlations and graphs

* Autocorrelation Within transformed: double trait: pas retardé, L1 premier retard
xtset ident year
sort ident year 
correlate wgdpg L.wgdpg weda L.weda ///
wpolicy L.wpolicy wlgdp L.wlgdp wm2_1 L.wm2_1 year

* Between Within Correlation matrix Pairwise Comparisons
* Repeated (weighted) between 275 observations instead of 56
* PROC CORR GRAPH ODS see outliers Comparison Between Within

graph matrix wgdpg wpolicy wlgdp wm2_1 year
graph matrix mgdpg mpolicy mlgdp mm2_1 
correlate wgdpg wpolicy wlgdp wm2_1 year
correlate mgdpg mpolicy mlgdp mm2_1 

graph matrix wgdpg wassas wethnfassas
graph matrix mgdpg massas methnfassas
correlate wgdpg wassas wethnfassas
correlate mgdpg massas methnfassas

graph matrix wgdpg weda wedapolicy weda2policy
graph matrix mgdpg meda medapolicy meda2policy
correlate wgdpg weda wedapolicy weda2policy 
correlate mgdpg meda medapolicy meda2policy 


* PROC GPLOT BIVARIATE LINEAR QUADRATIC LINE PROC LOWESS
* WITHIN transformed
graph twoway (scatter wgdpg weda, msize(small) msymbol(o))              ///
(lfit wgdpg weda, clstyle(p3) lwidth(medthick))      ///
(qfit wgdpg weda, clstyle(p5) lwidth(medthick))     ///
(lowess wgdpg weda, bwidth(0.4) clstyle(p1) lwidth(medthick)),        ///
  plotregion(style(none))                                              ///
  title("Bivariate Within tranformed: Aid/GDP versus GDP Growth")               ///
  xtitle("Within transformed Aid/GDP", size(medlarge)) xscale(titlegap(*5))   /// 
  ytitle("Within transformed GDP growth", size(medlarge)) yscale(titlegap(*5))       ///
  legend(pos(4) ring(0) col(1)) legend(size(small))                    ///
  legend(label(1 "Actual Data") label(2 "Linear fit") label(3 "Quadratic fit") label(4 "Lowess"))
graph export mus08gasscatterplot.eps, replace


* PROC GPLOT BIVARIATE LINEAR QUADRATIC LINE PROC LOWESS
* Weighted BETWEEN transformed
graph twoway (scatter mgdpg meda, msize(small) msymbol(o))              ///
(lfit mgdpg meda, clstyle(p3) lwidth(medthick))      ///
(qfit mgdpg meda, clstyle(p5) lwidth(medthick))     ///
(lowess mgdpg meda, bwidth(0.4) clstyle(p1) lwidth(medthick)),        ///
  plotregion(style(none))                                              ///
  title("Weighted repeated Between tranformed: Aid/GDP versus GDP Growth")               ///
  xtitle("Between transformed Aid/GDP", size(medlarge)) xscale(titlegap(*5))   /// 
  ytitle("Between transformed GDP growth", size(medlarge)) yscale(titlegap(*5))       ///
  legend(pos(4) ring(0) col(1)) legend(size(small))                    ///
  legend(label(1 "Actual Data") label(2 "Linear fit") label(3 "Quadratic fit") label(4 "Lowess"))
graph export mus08gasscatterplot.eps, replace

* Within (fixed effects) estimation with relevant regressors
reg wgdpg wpolicy wlgdp wm2_1 
xtreg gdpg policy lgdp m2_1 , fe
xtreg gdpg policy lgdp m2_1 , fe vce(cluster ident)

* Between estimation
xtreg gdpg policy , be
xtreg gdpg policy lgdp m2_1 , be
xtreg gdpg policy lgdp m2_1 icrge ethnf, be
xtreg gdpg policy lgdp m2_1 icrge ssa easia ethnf, be
* Repeated between: Wrong (too small) standard error
reg mgdpg mpolicy mlgdp mm2_1 

* Mundlak estimation (weights on between?)	
xtreg gdpg policy lgdp m2_1 mpolicy mlgdp mm2_1 ///
micrge ssa easia ethnf, re
* same parameters with reg
reg gdpg policy lgdp m2_1 mpolicy mlgdp mm2_1 ///
micrge ssa easia ethnf

*** 3D PRETEST HAUSMAN TAYLOR
*** FOR ENDOGENOUS TIME INVARIANT: HERE: ICRGE
*** CHATELAIN RALF (2010) PRETEST 

* STEP1: MUNDLAK ALL 
xtreg gdpg eda policy lgdp m2_1 assas ethnfassas ///
mmeda mpolicy mlgdp mm2_1 massas methnfassas ///
icrge ssa easia ethnf , re
* ENDOGENOUS TIME VARYING ARE: lgdp m2_1
* STEP2A: USUAL RESTRICTED HAUSMAN TAYLOR
* for icrge
* COMPARE parameters with MUNDLAK
* for time varying and time invariant
xthtaylor gdpg ///
eda policy lgdp m2_1 assas ethnfassas ///
icrge ssa easia ethnf , ///
endog (lgdp m2_1 icrge)
* HAUSMAN CONTRAST
* STEP2B: UNRESTRICTED HAUSMAN TAYLOR for icrge
xthtaylor gdpg ///
eda policy lgdp m2_1 assas ethnfassas ///
mlgdp mm2_1 ///
icrge ssa easia ethnf , ///
endog (lgdp m2_1 icrge)
* STEP2C: FULLY UNRESTRICTED HAUSMAN TAYLOR for icrge
xthtaylor gdpg ///
eda policy lgdp m2_1 assas ethnfassas ///
mmeda mpolicy mlgdp mm2_1 massas methnfassas ///
icrge ssa easia ethnf , ///
endog (lgdp m2_1 icrge)
* STEP3A: WEAK INSTRUMENTS FOR ICRGE? 
correlate icrge eda policy assas ethnfassas
correlate icrge meda mpolicy massas methnfassas
* STEP3B: R2 WEAK INSTRUMENTS 1st step IV
regress icrge eda policy assas ethnfassas
regress icrge meda mpolicy massas methnfassas


*** 3E FIRST DIFF, WITHIN, BETWEEN, MUNDLAK ESTIMATOR
*** UPWARD TESTING PROCEDURE OF EXOGENOUS REGRESSORS and VOID OF TREND SPURIOUS


* Within of FE estimator with cluster-robust standard errors
* PROVIDES ALSO THE R2 for BETWEEN and for OLS
* PROVIDES ALSO THE VARIANCE of ALPHA(i), here (u(i)) in total variance RHO
* OF RESIDUALS
* PROVIDES CORR(u(i), Xbeta=linear combination of X 
* and not specific X(it) for each regressor
* First-differences estimator with cluster-robust standard errors
* UPWARD TESTING SELECTION OF EXOGENOUS REGRESSORS

* 1st STEP PROC REG: regress PROC PANEL: xtreg
* EDA
regress D.(gdpg eda), vce(cluster id) noconstant
xtreg gdpg eda            , fe vce(cluster ident)
xtreg gdpg eda            , be
xtreg gdpg eda mmeda      , re vce(cluster ident)
* POLICY
regress D.(gdpg policy), vce(cluster id) noconstant
xtreg gdpg policy            , fe vce(cluster ident)
xtreg gdpg policy            , be
xtreg gdpg policy mpolicy    , re vce(cluster ident)
* POLICY WITH FOUR TIME INVARIANT VARIABLES
xtreg gdpg policy icrge ssa easia ethnf     , be
xtreg gdpg policy mpolicy icrge ssa easia ethnf , re
xtreg gdpg policy mpolicy icrge ssa easia ethnf , re vce(cluster ident)
regress gdpg policy mpolicy icrge ssa easia ethnf , vce(cluster ident)
* EDA POLICY 2nd Step with 2 regressors 
regress D.(gdpg eda policy), vce(cluster id) noconstant
xtreg gdpg eda policy            , fe vce(cluster ident)
xtreg gdpg eda policy            , be
xtreg gdpg eda policy mmeda mpolicy   , re vce(cluster ident)
regress gdpg eda policy mmeda mpolicy , vce(cluster ident)
* EDA POLICY WITH FOUR TIME INVARIANT VARIABLES
xtreg gdpg eda policy icrge ssa easia ethnf     , be
xtreg gdpg eda policy mmeda mpolicy icrge ssa easia ethnf , re
xtreg gdpg eda policy mmeda mpolicy icrge ssa easia ethnf , re vce(cluster ident)
* EDA dependent variable and SSA: change of signs above
xtreg eda policy ssa icrge easia ethnf , be
xtreg eda policy mpolicy ssa icrge easia ethnf , re

* MUNDLAK ALL 
xtreg gdpg eda policy lgdp m2_1 assas ethnfassas mmeda mpolicy mlgdp mm2_1 massas methnfassas icrge ssa easia ethnf , re
xtreg gdpg eda policy mmeda mpolicy icrge ssa easia ethnf , re vce(cluster ident)

* MUNDLAK removing spurious: assas ethnf ethnfassas 
xtreg gdpg eda policy lgdp m2_1 mmeda mpolicy mlgdp mm2_1 icrge ssa easia, re
xtreg gdpg eda policy mmeda mpolicy icrge ssa easia ethnf , re vce(cluster ident)

* OTHER ESTIMATOR WITH NEAR-MULTICOLLINEARITY
xtivreg gdpg ///
eda policy lgdp m2_1 assas ethnfassas ///
mmeda mpolicy mlgdp mm2_1 massas methnfassas ///
ssa easia ethnf ///
(icrge = meda mpolicy massas methnfassas), re






***** 2A: REPLICATION OF BD OLS REGRESSIONS

* TABLE 3 EQUATION 1-OLS with BB INFL SACW without Aid/GDP
* Not the same Robust White standard errors. Rounding OK * N=275
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa easia bb100 infl100 sacw year2-year7, vce(robust)
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa easia bb100 infl100 sacw year2-year7, vce(cluster ident)

* Sachs Warner correlated with Easia 0.5, R2=25%
correlate gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa easia bb100 infl100 sacw year2-year7

* TABLE 3 EQUATION 2-OLS with BB INFL SACW and Aid/GDP
* Not the same White standard errors. Rounding OK * N=275
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa easia bb100 infl100 sacw eda year2-year7, vce(cluster ident)

* TABLE 4 EQUATION 3-OLS with policy and Aid/GDP
* Not the same White standard errors. Rounding OK * N=275
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa easia policy eda year2-year7, vce(cluster ident)

* TABLE 4 EQUATION 3-OLS order: 6 time varying then 4 time invariant
regress gdpg eda policy lgdp m2_1 assas ethnfassas icrge ssa easia ethnf100 year2-year7, vce(cluster ident)

* TABLE 4 EQUATION 4-OLS N=275 with edapolicy eda2policy
* NOT THE WHITE STANDARD ERRORS: not statistically significant.
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy eda2policy year2-year7, ///
vce(robust)

* Chatelain Ralf replication without GMB6
* TABLE 4 EQUATION 4-OLS N=274 with edapolicy eda2policy
* NOT THE WHITE STANDARD ERRORS: not statistically significant.
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy eda2policy year2-year7, ///
vce(robust), if (countryyear != "GMB6")

* TABLE 4 EQUATION 5-OLS N=270 edapolicy without eda2policy 
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7, ///
vce(robust), ///
if (countryyear != "GMB6") & (countryyear !="GMB7") ///
&  (countryyear != "NIC7") & (countryyear !="GUY7") ///
&  (countryyear != "NIC6") 

* Chatelain Ralf replication without BWA6-5-4
* TABLE 4 EQUATION 5-OLS N=267 edapolicy without eda2policy 
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7, ///
vce(robust), ///
if (countryyear != "GMB6") & (countryyear !="GMB7") ///
&  (countryyear != "NIC7") & (countryyear !="GUY7") ///
&  (countryyear != "NIC6") & (countryyear !="BWA6") ///
&  (countryyear != "BWA5") & (countryyear !="BWA4") 


****** 2B: Chatelain Ralf replication N=274 to 260
* Cumulative removal of observations by their order of leverage

* Etape DATA: STANDARDIZED values edapolicy: high leverage outliers
egen stdedapolicy = std(edapolicy)
gen absstdedapolicy = abs(stdedapolicy)
* PROC PRINT high leverage observations for Aid/GDP*Policy
sort absstdedapolicy
list countryyear absstdedapolicy stdedapolicy edapolicy 

* Add in columns of the following table 
* the following estimated parameter (beta) and its p-value H:beta=0
* for eda2policy and edapolicy in specification table 4, equation 2-OLS
* for edapolicy in specification table 4, equation 3-OLS
* plot the graph (p-value, beta ; value of last outlier in sample)
* Check the maximisation of beta and the minisation of p-value 
* in BD paper over the set of 15 outliers with leverage for edapolicy
* do not include MWI7, 1.27 standard error 
* from mean with 275 observations
/*
258. |     MWI7   1.271171    1.271171    7.803890328 |
259. |     BOL6   1.452372    1.452372    8.685857145 |
260. |     SLV7   1.470234    1.470234     8.77279425 |
     |------------------------------------------------|
261. |     HND7   1.489809    1.489809    8.868071908 |
262. |     GHA7   1.521734    1.521734    9.023460406 |
263. |     GUY5   1.586419   -1.586419   -6.104952024 |
264. |     BOL5   1.663999   -1.663999   -6.482559714 |
265. |     BOL7   1.821823    1.821823    10.48409696 |
     |------------------------------------------------|
266. |     GHA6   1.996045    1.996045    11.33209259 |
267. |     MLI6   2.724066    2.724066    14.87561402 |
268. |     BWA4   3.230281    3.230281    17.33953152 |
269. |     BWA5   3.454745    3.454745    18.43207233 |
270. |     BWA6   3.796316    3.796316    20.09460956 |
     |------------------------------------------------|
271. |     NIC6   4.074426   -4.074426   -18.21490773 |
272. |     GUY7   5.652469    5.652469    29.12912178 |
273. |     NIC7   5.790557   -5.790557   -26.56788798 |
274. |     GMB7   6.312735    6.312735    32.34285655 |
275. |     GMB6   7.873881    7.873881    39.94147304 |
*/

* TABLE 4 EQUATION 4-OLS N=275 to 259 with edapolicy eda2policy
* remove the 3 bars after the last outlier selected 
* and select upwards and run the regression
regress gdpg eda2policy edapolicy eda policy lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia year2-year7, ///
vce(robust), ///
if (countryyear != "GMB6") ///
& (countryyear !="GMB7")  ///
& (countryyear != "NIC7") /// 
& (countryyear !="GUY7")  ///
& (countryyear != "NIC6")  /// 
& (countryyear !="BWA6") ///
& (countryyear !="BWA5") ///
& (countryyear !="BWA4") ///
& (countryyear != "MLI6")  /// 
& (countryyear !="GHA6") ///
& (countryyear != "BOL7")  /// 
& (countryyear !="BOL5") ///
& (countryyear != "GUY5") /// 
& (countryyear !="GHA7")  ///
& (countryyear != "HDN7") ///
& (countryyear !="SLV7")  ///
& (countryyear != "BOL6")


* TABLE 4 EQUATION 5-OLS N=275 to 259  
* with edapolicy without eda2policy
* remove the 3 bars after the last outlier selected 
* and select upwards and run the regression
regress gdpg edapolicy eda policy lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia year2-year7, ///
vce(robust), ///
if (countryyear != "GMB6") ///
& (countryyear !="GMB7")  ///
& (countryyear != "NIC7") /// 
& (countryyear !="GUY7")  ///
& (countryyear != "NIC6")  /// 
& (countryyear !="BWA6") ///
& (countryyear !="BWA5") ///
& (countryyear !="BWA4") ///
& (countryyear != "MLI6")  /// 
& (countryyear !="GHA6") ///
& (countryyear != "BOL7")  /// 
& (countryyear !="BOL5") ///
& (countryyear != "GUY5") /// 
& (countryyear !="GHA7")  ///
& (countryyear != "HDN7") ///
& (countryyear !="SLV7")  ///
& (countryyear != "BOL6")


***** 2C OUTLIERS STATISTICS: DFBETAxLEVERAGE edapolicy figures

* REPLICATE FIGURE1 p.858 DFbeta(edapolicy) function of edapolicy 
* TABLE 4 EQUATION 5-OLS N=275 with edapolicy without eda2policy
* DFBETA are divided by a standard error range: 
* -0.61 GMB6 -0.53 GMB7 to +0.186 BWA4 +0.189 BWA6
* BD difference of slopes figure1 is the NUMERATOR of dfbeta 
* range -0.04/+0.02 on edapolicy slope.
* ADDITIONAL PLOTS: lvr2plot: leverage (of which variable?)
* versus square residuals plots 
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7
rvfplot
rvpplot edapolicy
lvr2plot
sort edapolicy
predict dfbedapolicy, dfbeta(edapolicy)
sort dfbedapolicy
list dfbedapolicy edapolicy countryyear
quietly twoway (scatter dfbedapolicy edapolicy) ///
(lowess dfbedapolicy edapolicy) 
* SAME GRAPH With standardized value (N=275) of horizontal axis
quietly twoway (scatter dfbedapolicy stdedapolicy) ///
(lowess dfbedapolicy stdedapolicy) 


* Figure including quadratic interaction term
* TABLE 4 EQUATION 4-OLS N=275 with edapolicy with eda2policy
*  DFBETA are divided by a standard error range: 
* -0.16 ECU7 -0.15 GMB7 to +0.27 BWA5 +0.32 BWA4 +0.33 GMB6 !
* THIS TIME, GMB6 is pushing the parameter upwards whereas
* in the other specification it is pushing the parameter downwards
* GMB6 = additional "dummy effect" of the interaction term
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy eda2policy year2-year7
sort edapolicy
predict dfbedapolicyB, dfbeta(edapolicy)
sort dfbedapolicyB
list dfbedapolicyB dfbedapolicy edapolicy countryyear
quietly twoway (scatter dfbedapolicyB edapolicy) ///
(lowess dfbedapolicyB edapolicy) 
* SAME GRAPH With standardized value (N=275) of horizontal axis
quietly twoway (scatter dfbedapolicyB stdedapolicy) ///
(lowess dfbedapolicyB stdedapolicy) 


* FIGURE for N=270 BD "best regression" without eda2policy
* DFBETA are divided by a standard error range: 
* -0.16 ECU2 EGY3 to MLI6 +0.23 BWA5 +0.40 BWA4
* BD difference of slopes figure1 is the NUMERATOR of dfbeta 
* range -0.04/+0.02 on edapolicy slope.
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7 /// 
if (countryyear != "GMB6") & (countryyear !="GMB7") ///
&  (countryyear != "NIC7") & (countryyear !="GUY7") ///
&  (countryyear != "NIC6") 
sort edapolicy
predict dfbedapolicy270, dfbeta(edapolicy)
sort dfbedapolicy270 dfbedapolicy
list dfbedapolicy270 dfbedapolicy edapolicy stdedapolicy countryyear
quietly twoway (scatter dfbedapolicy270 edapolicy) ///
(lowess dfbedapolicy270 edapolicy) 
* SAME GRAPH With standardized value of horizontal axis
quietly twoway (scatter dfbedapolicy270 stdedapolicy) ///
(lowess dfbedapolicy270 stdedapolicy) 

* FIGURE for N=266 without eda2policy 
* N=267: MLI6: +0.59 quite large
* DFBETA are divided by a standard error range: 
* -0.16 ECU2 EGY3 to MLI6 +0.23 BWA5 +0.40 BWA4
* BD difference of slopes figure1 is the NUMERATOR of dfbeta 
* range -0.04/+0.02 on edapolicy slope.
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7 /// 
if (countryyear != "GMB6") & (countryyear !="GMB7") ///
&  (countryyear != "NIC7") & (countryyear !="GUY7") ///
&  (countryyear != "NIC6") & (countryyear !="BWA4") ///
&  (countryyear != "BWA5") & (countryyear !="BWA6") ///
&  (countryyear != "MLI6")
sort edapolicy
predict dfbedapolicy266, dfbeta(edapolicy)
sort dfbedapolicy266 dfbedapolicy
list dfbedapolicy266 dfbedapolicy edapolicy stdedapolicy countryyear
quietly twoway (scatter dfbedapolicy266 edapolicy) ///
(lowess dfbedapolicy266 edapolicy) 
* SAME GRAPH With standardized value of horizontal axis
quietly twoway (scatter dfbedapolicy266 stdedapolicy) ///
(lowess dfbedapolicy266 stdedapolicy) 

* 259 observations
regress gdpg lgdp ethnf100 assas ethnfassas icrge m2_1 ssa  ///
easia policy eda edapolicy year2-year7 /// 
if (countryyear != "GMB6") ///
& (countryyear !="GMB7")  ///
& (countryyear != "NIC7") /// 
& (countryyear !="GUY7")  ///
& (countryyear != "NIC6")  /// 
& (countryyear !="BWA6") ///
& (countryyear !="BWA5") ///
& (countryyear !="BWA4") ///
& (countryyear != "MLI6")  /// 
& (countryyear !="GHA6") ///
& (countryyear != "BOL7")  /// 
& (countryyear !="BOL5") ///
& (countryyear != "GUY5") /// 
& (countryyear !="GHA7")  ///
& (countryyear != "HDN7") ///
& (countryyear !="SLV7")  ///
& (countryyear != "BOL6")
sort edapolicy
predict dfbedapolicy259, dfbeta(edapolicy)
sort dfbedapolicy259 dfbedapolicy
list dfbedapolicy259 dfbedapolicy edapolicy stdedapolicy countryyear
quietly twoway (scatter dfbedapolicy259 edapolicy) ///
(lowess dfbedapolicy259 edapolicy) 
* SAME GRAPH With standardized value of horizontal axis
quietly twoway (scatter dfbedapolicy259 stdedapolicy) ///
(lowess dfbedapolicy259 stdedapolicy) 


* OTHER STATISTICS RESIDUS STUDENTISES
*predict estu, rstudent
*lvr2plot
*list estu countryyear


******* 2D: The 2-step mechanics of spurious interaction terms

* Is there erroneous inference to all developing countries 
* from a single observation (Here, Gambia6)
* First step: eda2policy=beta.edapolicy + residual
* residual is the variance added by the interaction term
* with respect to the regression without this interaction term
* Second step: residual = eda2policy-beta.edapolicy= beta2.dummy
* Third step: remove this observation from the regression (cf. 2B)
* (equivalent to add this dummy in the regression)
* CHECKS whether a single country dummy  
* is a good substitute to an "all countries" interaction term

* highly correlated pairs of classical suppressors
* for which do not reject the null of zero simple correlation 
* with dependent, for example, simple correlation<0.1 N small.
correlate gdpg eda2policy edapolicy eda policy m2_1 assas icrge ssa easia ethnf year2-year7 
correlate gdpg eda2policy edapolicy
correlate gdpg ethnfassas assas ethnf

* First step: the residual uhat1 is the contribution 
* of the interaction term
* to the explanation of the variance of the per capita GDP growth
regress eda2policy edapolicy
predict double uhat1, resid
* PROC UNIVARIATE for uhat1
* GAMBIA6 (168) is 10 standard errors (17) far from the mean=0 of uhat1
* GAMBIA6 inflates skewness and kurtosis of uhat1
tabstat uhat1 edapolicy eda2policy gdpg, stat (count mean p50 skew min max sd variance kurt) col(stat)
histogram uhat1, width(0.25) kdensity normal
kdensity uhat1, bwidth(0.20) normal n(4000)

* Etape DATA: STANDARDIZED (different from Studentized residuals)
egen stduhat1 = std(uhat1)
gen absstduhat1 = abs(stduhat1)
generate double absuhat1=abs(uhat1)

* PROC PRINT high leverage Aid/GDP2*Policy-beta.aid/GDP*Policy
* comparison with high leverage observations for edapolicy
sort absstduhat1
list countryyear absstduhat1 stduhat1 absstdedapolicy uhat1 edapolicy

quietly twoway (scatter stduhat1 edapolicy) (lowess stduhat1 edapolicy) ///
(lfit stduhat1 edapolicy) (qfit stduhat1 edapolicy)
quietly twoway (scatter absstduhat1 edapolicy)(lowess absstduhat1 edapolicy)
* PROC BOXPLOT RESIDUALS BY COUNTRY
graph box stduhat1  , over(year) 
graph box stduhat1 , over(ident) 
sort countryyear
graph box stduhat1 , over(country3), in 1/70


* STEP 1: PROC GPLOT BIVARIATE LINEAR QUADRATIC LINE PROC LOWESS
* GRAPH with Country3 
* interaction term on the more correlated term
graph twoway (scatter eda2policy edapolicy, msize(small) msymbol(o))              ///
(lfit eda2policy edapolicy, clstyle(p3) lwidth(medthick))      ///
(qfit eda2policy edapolicy, clstyle(p5) lwidth(medthick))     ///
(lowess eda2policy edapolicy, bwidth(0.4) clstyle(p1) lwidth(medthick)),        ///
  plotregion(style(none))                                              ///
  title("(Aid/GDP)2*Policy versus Aid/GDP*Policy")               ///
  xtitle("(Aid/GDP)*Policy", size(medlarge)) xscale(titlegap(*5))   /// 
  ytitle("(Aid/GDP)2*Policy", size(medlarge)) yscale(titlegap(*5))       ///
  legend(pos(4) ring(0) col(1)) legend(size(small))                    ///
  legend(label(1 "Actual Data") label(2 "Linear fit") label(3 "Quadratic fit") label(4 "Lowess"))
graph export mus08gasscatterplot.eps, replace


* STEP 2: R2=32.5% of variance of the interaction term 
* explained with one dummy for GAMBIA6
regress uhat1 gambia6
* R2 simple regression 0.325 = square of simple correlation 0.570
correlate uhat1 gambia6

* STEP 2: PROC GPLOT BIVARIATE LINEAR QUADRATIC LINE PROC LOWESS
* GRAPH with Country3 ?
graph twoway (scatter uhat1 gambia6, msize(small) msymbol(o))              ///
(lfit uhat1 gambia6, clstyle(p3) lwidth(medthick))      ///
(qfit uhat1 gambia6, clstyle(p5) lwidth(medthick))     ///
(lowess uhat1 gambia6, bwidth(0.4) clstyle(p1) lwidth(medthick)),        ///
  plotregion(style(none))                                              ///
  title("(Aid/GDP)2*Policy-beta*Aid/GDP*Policy versus Gambia6")               ///
  xtitle("Gambia6", size(medlarge)) xscale(titlegap(*5))   /// 
  ytitle("(Aid/GDP)2*Policy-beta*Aid/GDP*Policy ", size(medlarge)) yscale(titlegap(*5))       ///
  legend(pos(4) ring(0) col(1)) legend(size(small))                    ///
  legend(label(1 "Actual Data") label(2 "Linear fit") label(3 "Quadratic fit") label(4 "Lowess"))
graph export mus08gasscatterplot.eps, replace


******* 2E: VIF PIF simple correlation coefficient tests 

* Pair with opposite standardized beta 
* PIF and VIF: measures of highly correlated pairs
* 1-(1/VIF): R2 of the auxiliary regression: 
* dependent is one of the regressor linear function of all others
* R2=39.81%  adjR2=35.83% 17 variables
regress gdpg eda2policy edapolicy ethnfassas assas  ///
eda policy icrge ssa easia lgdp ethnf100 m2_1  year3-year7, beta
estat vif

* p-value tests of null hypothesis pwcorr=0
pwcorr gdpg eda2policy edapolicy, obs sig
* PROC CORR GRAPH ODS see outliers
graph matrix gdpg eda2policy edapolicy
pwcorr gdpg ethnfassas assas, obs sig
graph matrix gdpg ethnfassas assas

* Compute PIF is ratio of standardized beta / simple correlation
* -4.62 and -3.41
gen PIFeda2policy = -0.2452853/0.053
list PIFeda2policy in 1/1 
gen PIFethnfassas = 0.1342474/-0.0393 
list PIFethnfassas in 1/1 


*** 2F Contribution to R2 and POWER of t-test computations

* R2=39.81%  adjR2=35.83% 17 variables
regress gdpg eda2policy edapolicy ethnfassas assas  ///
eda policy icrge ssa easia lgdp ethnf100 m2_1  year3-year7, beta
estat vif
 
* R2=37.92%  adjR2=36.05% 7 variables
stepwise, pe(0.05): regress gdpg eda2policy edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year3-year7

* SAMPSI (sample size and power determination)
* STPOWER

*** 2G Robust regressions Quantile regressions and spurious pair

* Robust regression: default rreg (huber) does not change
* median (quantile) regression: no variable stat. significant
* the pair of classical suppressors still pending with rreg qreg

regress gdpg eda2policy edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year2-year7

rreg gdpg eda2policy edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year2-year7

qreg gdpg eda2policy edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year2-year7

sqreg gdpg eda2policy edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year2-year7, ///
quantile(0.25 0.5 0.75) reps(100)

sqreg gdpg edapolicy eda policy lgdp ///
ethnf100 assas ethnfassas icrge m2_1 ssa easia year2-year7, ///
quantile(0.25 0.5 0.75) reps(100)

