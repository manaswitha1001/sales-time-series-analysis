import datetime
import numpy as np
import math

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

import pandas as pd

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


from sklearn.preprocessing import MinMaxScaler


__author__ = "Sreejith Sreekumar"
__email__ = "sreekumar.s@husky.neu.edu"
__version__ = "0.0.1"


def build_model_and_evaluate(X_train, y_train, X_test, y_test, sc):

    regressor = Sequential()
    regressor.add(LSTM(units = 3, input_shape = (None, 1)))
    regressor.add(Dense(units = 1))
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    history = regressor.fit(X_train,
                            y_train,
                            epochs = 100,
                            batch_size = 32,
                            verbose=0)
    
    inputs = np.array(X_test)
    inputs = np.reshape(inputs, (inputs.shape[0], inputs.shape[1], 1))
    predicted = regressor.predict(inputs)
    predicted_prices = sc.inverse_transform(predicted)

    rmse = math.sqrt(mean_absolute_error(y_test, predicted))
    return regressor, predicted_prices.reshape(len(predicted_prices),), rmse

    
def validate(train, test, sc):

    X_train = []
    y_train = []
    for i in range(7, len(train)):
        X_train.append(train[i-7:i, 0])
        y_train.append(train[i][0])
        
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Test data
    X_test = []
    y_test = []
    full_data = np.append(train, test)
    full_data = full_data.reshape(len(full_data),1)
    for i in range(len(train)-7, len(full_data)-7):
        X_test.append(full_data[i-7:i])
    y_test = test.reshape(len(test),)
    X_test = np.array(X_test)

    return build_model_and_evaluate(X_train, y_train, X_test, y_test, sc)


def predict(model, sc, full_data, train_end_date):

    train_ = full_data[full_data.date_ <= train_end_date].iloc[:,2:3].values
    test_ = full_data[full_data.date_ > train_end_date].iloc[:,2:3].values
    full_data = full_data.iloc[:,2:3].values

    X_pred = []
    for i in range(len(train_)-7, len(full_data)-7):
        X_pred.append(full_data[i-7:i])

    X_pred = np.array(X_pred)
    pred = model.predict(X_pred)
    prices = sc.inverse_transform(pred)
    return prices
        

def walk_forward_validation(full_data_, train_end_date):

    data_ = full_data_[full_data_.date_ <= train_end_date]

    ## val model 1
    stop_date = train_end_date + datetime.timedelta(-150)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date_ > stop_date].iloc[:,2:3].values
    sc1 = MinMaxScaler(feature_range = (0, 1))

    train_ = sc1.fit_transform(train)
    test_ = sc1.transform(test)
    
    model1, predicted1, rmse1 = validate(train_, test_, sc1)

    
    ## val model 2
    stop_date = train_end_date + datetime.timedelta(-120)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date_ > stop_date].iloc[:,2:3].values
    sc2 = MinMaxScaler(feature_range = (0, 1))

    train_ = sc2.fit_transform(train)
    test_ = sc2.transform(test)
    model2, predicted2, rmse2 = validate(train_, test_, sc2)
    

    ## val model 3
    stop_date = train_end_date + datetime.timedelta(-90)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date_ > stop_date].iloc[:,2:3].values
    sc3 = MinMaxScaler(feature_range = (0, 1))

    train_ = sc3.fit_transform(train)
    test_ = sc3.transform(test)
    model3, predicted3, rmse3 = validate(train_, test_, sc3)
    

    ## val model 4
    stop_date = train_end_date + datetime.timedelta(-60)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date_ > stop_date].iloc[:,2:3].values
    sc4 = MinMaxScaler(feature_range = (0, 1))

    train_ = sc4.fit_transform(train)
    test_ = sc4.transform(test)
    model4, predicted4, rmse4 = validate(train_, test_, sc4)
    

    ## val model 5
    stop_date = train_end_date + datetime.timedelta(-30)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date_ > stop_date].iloc[:,2:3].values
    sc5 = MinMaxScaler(feature_range = (0, 1))

    train_ = sc5.fit_transform(train)
    test_ = sc5.transform(test)
    model5, predicted5, rmse5 = validate(train_, test_, sc5)
    
    ## choose the model with the best rmse here
    index = np.argmin([rmse1, rmse2, rmse3, rmse4, rmse5])
    predictions = [predicted1, predicted2, predicted3, predicted4, predicted5][index]
    model = [model1, model2, model3, model4, model5][index]
    scaler = [sc1, sc2, sc3, sc4, sc5][index]

    ## write predictions for each day
    return model, scaler, predictions
    
       


def do_walk_forward_validation_and_get_best_models(data,
                                                  train_end_date,
                                                  learning_rate,
                                                  optimizer):

    stores = data.Store.unique()
    result = []
    
    for store in stores[:1]:
        store_res = {}
        store_res["store"] = store
        
        print("Training model for store: ", store)
        data_ = data[data.Store == store]
        model, scaler, predictions = walk_forward_validation(data_, train_end_date)

        store_res["model"] = model
        store_res["scaler"] = scaler
        store_res["test_predictions"] = predictions

        result.append(store_res)

    return result
        
