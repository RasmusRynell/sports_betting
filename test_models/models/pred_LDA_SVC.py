
import pandas as pd
import numpy as np

from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict

def pred(file_name, pred, gamePk):    
    pred_this_over = "shots_this_game_O" + str(pred)
    pred_this_under = "shots_this_game_U" + str(pred)
    res = {}
    tmp = {}
    for i in range(2):
        if(i == 1):
            pred_this = pred_this_over
            pos_label = 1
        else:
            pred_this = pred_this_under
            pos_label = 0

        data = pd.read_csv(file_name)
        data = data.replace(np.nan, 0)

        drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
        #drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5","date"]
        
        drop_this = [x for x in drop_this if x != pred_this]
        data.drop(drop_this,1, inplace=True)


        pred_this_game = data.loc[data["gamePk"] == gamePk]
        game_index = data.loc[data["gamePk"] == gamePk].index[0]
        #data = data.iloc[:game_index]

        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns]) 

        lda = LinearDiscriminantAnalysis(n_components=1)
        lda = lda.fit(X_all, Y_all)
        X_lda = lda.transform(X_all)

        X_lda_test = X_lda[game_index:]
        Y_all_test = Y_all[game_index:]

        X_lda = X_lda[:game_index]
        Y_all = Y_all[:game_index]

        clf_SVC_test = SVC(random_state=912, kernel='rbf', probability=True)
        clf_SVC_test.fit(X_lda, Y_all)
        pred = clf_SVC_test.predict(X_lda_test)
        
        print(pred_this)
        counter = 0
        for i in data[game_index:].gamePk:
            """
            if pred_this == pred_this_over:
                if pred[counter] == 1:
                    tmp[str(i)] = "O"
            if pred_this == pred_this_under:
                if pred[counter] == 1:
                    tmp[str(i)] = "U"
            """
            print(str(i) + ": {}".format(pred[counter]))            
            counter += 1

        clf_SVC = SVC(random_state=912, kernel='rbf', probability=True)        
        # cross validation
        f_scores_test = cross_val_score(clf_SVC, X_lda, Y_all, scoring="f1", cv=5)
        f_test_error = round(f_scores_test.mean(),3)
        f_test_std = round(f_scores_test.std(), 3)

        scores_test = cross_val_score(clf_SVC, X_lda, Y_all, cv=5)
        test_error = round(scores_test.mean(), 3)
        test_std = round(scores_test.std(), 3)

        clf_SVC.fit(X_lda, Y_all) 
        pred_this_game = pred_this_game.drop([pred_this],1)
        pred_this_game_LDA = lda.transform(pred_this_game)
        Y_pred = clf_SVC.predict_proba(pred_this_game_LDA)     


        if(pred_this == pred_this_over):
            res["pred_over"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(round(Y_pred[0][1], 3)), "num_games_train" : len(X_all)}
        else:
            res["pred_under"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(round(Y_pred[0][1], 3)), "num_games_train" : len(X_all)}
    print(tmp)
    return res  
