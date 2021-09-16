"""
2020

@author: Eric Vansteenberghe

https://www.kaggle.com/johnolafenwa/us-census-data/data
http://johnolafenwa.blogspot.fr/2017/07/machine-learning-tutorial-1-wage.html?m=1
https://www.kaggle.com/johnolafenwa/wage-prediction
I would like to thank Pierre P. who help me a lot getting started with Machine Learning techniques
age: continuous. 
workclass: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked. 
fnlwgt: continuous. 
education: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool. 
education-num: continuous. 
marital-status: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse. 
occupation: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces. 
relationship: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried. 
race: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black. 
sex: Female, Male. 
capital-gain: continuous. 
capital-loss: continuous. 
hours-per-week: continuous. 
native-country: United-States, Cambodia, England, Puerto-Rico, Canada, Germany, Outlying-US(Guam-USVI-etc), India, Japan, Greece, South, China, Cuba, Iran, Honduras, Philippines, Italy, Poland, Jamaica, Vietnam, Mexico, Portugal, Ireland, France, Dominican-Republic, Laos, Ecuador, Taiwan, Haiti, Columbia, Hungary, Guatemala, Nicaragua, Scotland, Thailand, Yugoslavia, El-Salvador, Trinadad&Tobago, Peru, Hong, Holand-Netherlands.
"""

import pandas as pd
import numpy as np
import os

#We set the working directory (useful to chose the folder where to export output files)
os.chdir('/Users/skimeur/Google Drive/empirical_finance')

# indicate the localisation of your files
train_file = "data/adult-training.csv"
test_file = "data/adult-test.csv"

#DEFINE COLUMNS
COLUMNS = ["age", "workclass", "fnlwgt", "education","education_num","marital_status", "occupation", "relationship", "race","gender","capital_gain", "capital_loss", "hours_per_week","native_country","income_bracket"]
LABEL_COLUMN = "label"
CATEGORICAL_COLUMNS = ["workclass", "education", "marital_status", "occupation","relationship", "race", "gender", "native_country"]
CONTINUOUS_COLUMNS = ["age", "education_num", "capital_gain", "capital_loss","hours_per_week"]

df_train = pd.read_csv(train_file, names = COLUMNS, skipinitialspace = True, engine= "python")
df_test = pd.read_csv(test_file,names = COLUMNS, skipinitialspace = True, skiprows=1, engine = "python")

del train_file, test_file

#%% work on the data assurance quality
df_train = df_train.sort_values(by='fnlwgt')

# change the question marks "?" as np.NaN
df_train = df_train.replace({'?': np.NaN})
df_test = df_test.replace({'?': np.NaN})

# describe the data set
df_train.describe()

# show where the missing values are
df_train.count()-len(df_train)

# list the possible native countries
nativecountries = list(df_train.native_country.dropna().unique())
nativecountries.sort()
# not sure which country "South" is refering to
# Trying to find out which country South could be
# we have three candidates: https://www.state.gov/misc/list/#s
# South Africa, South Korea, South Sudan
southc = df_train.loc[df_train.native_country == 'South',:]
southc.race.describe()
# 77 are Asian Pacifique Island, we could consider it to be South Korea
df_train.loc[(df_train.native_country == 'South')&(df_train.race =='Asian-Pac-Islander'),'native_country'] = 'South Korea'
df_test.loc[(df_test.native_country == 'South')&(df_test.race =='Asian-Pac-Islander'),'native_country'] = 'South Korea'

del nativecountries, southc

# see what the features of NaN for occupation are
occupationnan = df_train.loc[df_train['occupation'].isnull(),:]
occupationnan.count() - len(occupationnan)

workclassnan = list(occupationnan.workclass.unique())
salarynan = list(occupationnan.fnlwgt.unique())
# the NaN in occupation correspond to Never Worked only for 7 observation, for mosst there is salary information
# we are facing missing values (instead of non-existing ones)
# we will have to resort to dropna if we use workclass and occupation in our model
del occupationnan, salarynan, workclassnan

#create a new variable: capital = capital gain - capital loss
df_train['capital'] = df_train['capital_gain'] - df_train['capital_loss']
df_test['capital'] = df_test['capital_gain'] - df_test['capital_loss']

# categories reduction
# marital status: single or couple
df_train.marital_status.unique()
singlelist = ['Never-married','Divorced', 'Widowed','Separated']
couplelist = ['Married-civ-spouse','Married-AF-spouse']
df_train.loc[df_train.marital_status.isin(singlelist),'couple'] = 'single'
df_train.loc[df_train.marital_status.isin(couplelist),'couple'] = 'couple'
df_test.loc[df_test.marital_status.isin(singlelist),'couple'] = 'single'
df_test.loc[df_test.marital_status.isin(couplelist),'couple'] = 'couple'

del singlelist, couplelist

# Exercise: perform
# Cluster with K-means
# Hierarchical clustering
# Plot and set a threshold for the Dendogram
# Apply a logit model
# Check if you overfit the data with a Lasso logit
# Random Forest
# Boosting


#%% From here below, this is taken directly from: http://johnolafenwa.blogspot.fr/2017/07/machine-learning-tutorial-1-wage.html?m=1
# you can do it as an optional HOMEWORK
#Remove NaN

df_train.dropna(how="any",axis = 0)
df_test.dropna(how="any", axis = 0)

#Set LABEL COLUMN
df_train[LABEL_COLUMN] = (df_train["income_bracket"].apply(lambda x: ">50K" in x)).astype(int)
df_test[LABEL_COLUMN] = (df_test["income_bracket"].apply(lambda x: ">50K" in x)).astype(int)

#CREATE CONTINUOS COLUMNS
# homework

