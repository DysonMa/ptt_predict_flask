# -*- coding: utf-8 -*-
"""
Madi

PTT Classifier
"""

#%%
# Basic
import pandas as pd
import numpy as np

# sqlite
import sqlite3 as DB
from sqlalchemy import create_engine

# Words Process
import jieba
import jieba.posseg as pseg
# stopwords = [line.rstrip() for line in open('./斷詞分析/stopWords.txt' , encoding='utf8') ]

# ML/DL
import tensorflow
import keras

# Sklearn
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.neighbors import KNeighborsClassifier  ## KNN
from sklearn.svm import SVC  ## SVM
from sklearn.ensemble import RandomForestClassifier ## RFC

# Xgboost
import xgboost
from  xgboost import XGBClassifier  ## xgboost
from xgboost import plot_importance

# imblearn
from imblearn.over_sampling import SMOTE

# analyze
from sklearn.metrics import classification_report  # 全部指標的report
from sklearn.metrics import confusion_matrix

#繪圖
import seaborn as sns
import matplotlib.pyplot as plt

#%%

# 定義資料庫位置
def get_DB(DB_path):
    conndb = DB.connect(DB_path) # 若有則讀取，沒有則建立
    curr = conndb.cursor()  
    return [conndb,curr]

# 查詢資料
def queryData(sqlite_path,webName):
    [conndb,curr] = get_DB(sqlite_path)
    try:
        results = curr.execute("SELECT * FROM {} ORDER BY Date DESC;".format(webName))
    except DB.OperationalError:
        return 'No Such Table'
    return results

# 查詢各版名
def queryBoardName(sqlite_path):
    [conndb,curr] = get_DB(sqlite_path)
    boardList = []
    try:
        results = curr.execute("SELECT name FROM sqlite_master")
        for row in results:
            boardList.append(row[0])
    except DB.OperationalError:
        return 'No Tables'
    return boardList

#%%

sqlite_path = 'D:\ptt_flask.db'
engine = create_engine('sqlite:///'+sqlite_path)

boardName = queryBoardName(sqlite_path)

df = pd.DataFrame()

for each in boardName:
    sql = f"SELECT ArticleID,Author,Title,Content,Comment_Content FROM {each} ORDER BY Date DESC;"
    df_each = pd.read_sql(sql, con=engine)
    df_each['boardName'] = each
    df = df.append(df_each)
    
df = df[['boardName','Title']]

#%%
# 觀察資料分布
groups = df.groupby('boardName')
groups.size().plot(kind='bar')

#%%

# SMOTE

# sm = SMOTE(sampling_strategy='minority', random_state=87)
# X_res, Y_res = sm.fit_sample(X_train, Y_train)



#%%
# 去掉 Soft_Job
df = df[df['boardName']!='Soft_Job'].reset_index()
df.drop(columns='index',inplace=True)

# 去除[新聞]...等字樣
regex = r'[[\w]*]'
df['Title'].replace(to_replace=regex, value='', regex=True, inplace=True)




#%%
TRAIN_TEST_RATIO = 0.8  # Train Test Split Ratio

df_train = df.sample(frac=TRAIN_TEST_RATIO, random_state=914)
df_test_origin = df.drop(df_train.index)

print('Ratio of Train: ',round(df_train.shape[0]/(df.shape[0]),2))
print('Ratio of Test: ',round(df_test_origin.shape[0]/(df.shape[0]),2))


#%%
def jieba_tokenizer(text):
  words = pseg.cut(text)
  return ' '.join([
      word for word, flag in words if flag != 'x'])

df_train['Title Tokenized'] = df_train['Title'].apply(jieba_tokenizer)

#%%
# 為了訓練需要，將類別轉化為數字類別(1-N類)
kind_mapping = {}
for num, kind in enumerate(set(df_train['boardName'])):
    kind_mapping[kind] = num

# 預測時，要將預測出的結果翻譯為原先的類別所使用
inversed_kind_mapping = {}
for kind, idx in kind_mapping.items():
    inversed_kind_mapping[idx] = kind

print('kind_mapping: ',kind_mapping)
print('inversed_kind_mapping: ',inversed_kind_mapping)

#%%
# 準備排序的文字list(keywordindex)
total_words = ' '.join(df_train['Title Tokenized'])
vectorterms = list(set(total_words))

## 轉化每個問題變成向量
def vectorize(words):
    self_main_list = [0] * len(vectorterms)
    for term in words:
        if term in vectorterms:  ## 測試資料集當中的字不一定有出現在訓練資料集中
            idx = vectorterms.index(term)
            self_main_list[idx] += 1
    return np.array(self_main_list)

X_train = np.concatenate(df_train['Title Tokenized'].apply(vectorize).values).reshape(-1, len(vectorterms))
Y_train = df_train['boardName'].apply(kind_mapping.get)

print('Shape of X_train: ', X_train.shape)
print('Shape of Y_train: ', Y_train.shape)

#%%
TRAIN_VALID_RATIO = 0.2  # Train Valid Split Ratio

x_train, x_valid, y_train, y_valid = train_test_split(X_train, Y_train, test_size=TRAIN_VALID_RATIO, random_state=914)

print('Shape of X_train: ', x_train.shape)
print('Shape of X_Valid: ', x_valid.shape)
print('Shape of Y_train: ', y_train.shape)
print('Shape of Y_Valid: ', y_valid.shape)

#%%
# 定義函式，輸入分類器，輸出準確率
def get_accuracy(clf, *args):
    if args:
        clf = clf(kernel=args[0])
    else:
        clf = clf()
    clf = clf.fit(x_train, y_train)
    y_pred = clf.predict(x_valid)
    return (str(sum(y_valid == y_pred)/y_valid.shape[0]))

#%%
# clf = RandomForestClassifier()
# clf = SVC(kernel='linear',probability=True)
# clf = KNeighborsClassifier()
clf = XGBClassifier()
clf = clf.fit(X_train, Y_train)

#%%
# TODO:
    # 比較各分類器的準確度
    
print('RandomForest: ', get_accuracy(RandomForestClassifier))
print('SVC(linear):', get_accuracy(SVC,'linear'))
print('KNN:', get_accuracy(KNeighborsClassifier))
print('XGboost', get_accuracy(XGBClassifier))


#%%
# 機率
def predict(review,clf):  ## 定義預測函數
    words = jieba_tokenizer(review)
    vector = vectorize(words)
    prob = (clf.predict_proba(vector.reshape(1, -1)))*100
    return prob

# 找predict_proba出來的機率array中最大的，反映射為kind
def find_maxProb(prob):
  max_kind = np.argmax(prob)
  return inversed_kind_mapping.get(max_kind)

#%%
df_test = df_test_origin
df_test['ML_Classify_prob'] = df_test['Title'].apply(predict,args=(clf,))
df_test['ML_Classify'] = df_test['ML_Classify_prob'].apply(find_maxProb)
df_test = df_test[['Title','boardName','ML_Classify','ML_Classify_prob']]

correct_cnt = df_test[df_test_origin['boardName']==df_test['ML_Classify']].count()[0]
acc = correct_cnt/len(df_test)
print('Accuracy: ',acc)


#%%
# 統計指標
print(classification_report(df_test['boardName'], df_test['ML_Classify']))


# 計算混淆矩陣
lbl = list(kind_mapping.keys())
arr = confusion_matrix(df_test['boardName'], df_test['ML_Classify'], labels=lbl)

# 繪熱圖
df_cm = pd.DataFrame(arr, index = [i for i in lbl], columns = [i for i in lbl])
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 顯示中文
plt.figure(figsize = (8,5))  

sns.heatmap(df_cm, annot=True, cmap="YlGnBu");

plt.ylabel('y_true')
plt.xlabel('y_pred');
plt.tight_layout()
#%%
d = df_test[df_test['boardName']!=df_test['ML_Classify']]




#%%
# TODO:
    # 1. 混淆矩陣統計指標 ok
    # 2. 調參讓分類效果更好，目前是83.1%
    # 3. cross_validation -> RepeatedKFold

#%%

# xgboost + cv

# Set our parameters for xgboost
params = {}
params['objective'] = 'multi:softprob'
# params['eval_metric'] = 'logloss'
# params['eta'] = 0.04
# params['max_depth'] = 3
# params['learning_rate'] = 0.01
params['num_class'] = len(df_test_origin['boardName'].unique())

d_train = xgboost.DMatrix(x_train, label=y_train)
d_valid = xgboost.DMatrix(x_valid, label=y_valid)

watchlist = [(d_train, 'train'), (d_valid, 'valid')]

bst = xgboost.train(params, d_train, 100, watchlist, early_stopping_rounds=100, verbose_eval=10)
y_pred = bst.predict(xgboost.DMatrix(x_valid))

#%%

cnt = 0
for i in range(len(y_valid)):
    if y_valid.iloc[i] == kind_mapping[find_maxProb(y_pred[i])]:
       cnt+=1                                                   

acc2 = cnt/len(y_valid)
print('Accuracy: ',acc2)


# df_test_origin.iloc[i]['boardName']

# find_maxProb(y_pred[i])







