
import pandas as pd
import numpy as np 
import scipy.stats as stats
from tqdm import tqdm

from models.eval_model import eval_model
from models.eval_model import print_eval

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.metrics import make_scorer, accuracy_score, precision_score


from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


def generate_model(file_name, pred_this, earliest_gamePk_index):
    data = pd.read_csv(file_name)
    data = data.replace(np.nan, 0)
    #pred_this = "shots_this_game_O2.5"
    
    drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
    
    drop_this = [x for x in drop_this if x != pred_this]
    data.drop(drop_this,1, inplace=True)

    pred_data = data.iloc[earliest_gamePk_index:].drop([pred_this],1)
    data = data.iloc[:earliest_gamePk_index]

    X_all = data.drop([pred_this],1)
    Y_all = data[pred_this]

    opts = ["normal", "GridSearchCV"]#, "RandomizedSearchCV"]
    evals = ["accuracy", "precision"]#, "f1", "recall", "roc_auc"]
    #print(file_name)
    #print(pred_this)
    best_res = None
    best_model = None
    best_precision = 0
    for opt in (opts):
        for eval in evals:
            if(opt == "normal"):
                pipeline = make_pipeline(StandardScaler(), SVC(class_weight="balanced"))
                res = eval_model(pipeline, X_all, Y_all, earliest_gamePk_index, pred_this)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res

                #print_eval(res, "SVC-"+opt+"-"+eval)  

            elif(opt == "GridSearchCV"):
                model = SVC(class_weight="balanced")
                param_grid = [
                    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
                    {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
                ]
                if(eval == "accuracy"):
                    scorer = make_scorer(accuracy_score)
                elif(eval == "precision"):
                    scorer = make_scorer(precision_score, zero_division=0.0)
                rand_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=None, scoring=scorer)
                pipeline = make_pipeline(StandardScaler(), rand_search)   
                res = eval_model(pipeline, X_all, Y_all, earliest_gamePk_index, pred_this)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res

                #print_eval(res, "SVC-"+opt+"-"+eval)     

            elif(opt == "RandomizedSearchCV"):
                model = SVC(class_weight="balanced")
                rand_list = {"C": stats.uniform(0.1, 1000), 
                    "kernel": ["rbf", "poly"],
                    "gamma": stats.uniform(0.01, 100)}

                if(eval == "accuracy"):
                    scorer = make_scorer(accuracy_score)
                elif(eval == "precision"):
                    scorer = make_scorer(precision_score, zero_division=0.0)

                rand_search = RandomizedSearchCV(model, param_distributions=rand_list, n_iter=5, n_jobs=None, cv=5, scoring=eval, refit=True)
                pipeline = make_pipeline(StandardScaler(), rand_search)   
                res = eval_model(pipeline, X_all, Y_all, earliest_gamePk_index, pred_this)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res
                #print_eval(res, "SVC-"+opt+"-"+eval)   

    return best_res