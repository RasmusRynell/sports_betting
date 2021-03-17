import sys
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict


###############################################
def pred_XGB(file_name, pred):
    pred_this_over = "shots_this_game_O" + pred
    pred_this_under = "shots_this_game_U" + pred
    res = {}
    for i in range(2):
        if(i == 1):
            pred_this = pred_this_over
            pos_label = 1
        else:
            pred_this = pred_this_under
            pos_label = 0

        data = pd.read_csv(file_name)

        drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5",]
        drop_this = [x for x in drop_this if x != pred_this]
        data.drop(drop_this,1, inplace=True)

        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns])
        #This is the information about the game we want to predict.
        X_pred_info = X_all.head(1)
        Y_pred_info = Y_all.head(1)
        X_all = X_all.iloc[1:]
        Y_all = Y_all.iloc[1:]

        X_train, X_test, Y_train, Y_test = train_test_split(X_all, Y_all, test_size=50, random_state=2, stratify=Y_all)


        # Optimize the XGB model
        parameters = {"learning_rate" : [0.1], \
                "n_estimators" : [40], \
                "max_depth" : [1,2,3,4,5], \
                "min_child_weight" : [3], \
                "gamma" : [0.0001, 0.001, 0.01, 0.1, 0.2, 0.4, 0.5, 0.8], \
                "subsample" : [0.8], \
                "colsample_bytree" : [0.8], \
                "scale_pos_weight" : [1], \
                "reg_alpha" : [1e-5], \
                }

        clf = xgb.XGBClassifier(seed=82, use_label_encoder=False, eval_metric="error")
        f1_scorer = make_scorer(f1_score, pos_label=1)
        grid_obj = GridSearchCV(clf, scoring=f1_scorer, param_grid=parameters, cv=5)
        grid_obj = grid_obj.fit(X_train, Y_train)

        clf = grid_obj.best_estimator_

        # cross validation
        f_scores_test = cross_val_score(clf, X_test, Y_test, scoring="f1", cv=5)
        f_test_error = f_scores_test.mean()
        f_test_std = f_scores_test.std()
        
        scores_test = cross_val_score(clf, X_test, Y_test, cv=5)
        test_error = scores_test.mean()
        test_std = scores_test.std()

        # Predict for our game
        Y_pred = clf.predict_proba(X_pred_info)

        #Fit using CV
        #fit = cross_val_predict(clf, X_train, Y_train, cv=5)
        

        if(pred_this == pred_this_over):
            res["pred_over"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":Y_pred}
        else:
            res["pred_under"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":Y_pred}
    return res
###############################################
"""
file_name = sys.argv[1]
pred = sys.argv[2]

res = pred_XGB(file_name, pred)
print(res)
"""