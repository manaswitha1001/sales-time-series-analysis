import datetime

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))


__author__ = "Sreejith Sreekumar"
__email__ = "sreekumar.s@husky.neu.edu"
__version__ = "0.0.1"


def build_model_and_evaluate(X_train, y_train, X_test, y_test):
    
    regressor = Sequential()
    regressor.add(LSTM(units = 3, input_shape = (None, 1)))
    regressor.add(Dense(units = 1))
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    history = regressor.fit(X_train, y_train, epochs = 100, batch_size = 32, verbose=0)
    
    inputs = np.array(X_test)
    inputs = np.reshape(inputs, (inputs.shape[0], inputs.shape[1], 1))
    predicted = regressor.predict(inputs)
    predicted_price = sc.inverse_transform(predicted)
    
    rmse = sqrt(mean_squared_error(y_test, predicted_price))
    return rmse

    
def validate(train, test):

    X_train = []
    y_train = []
    for i in range(7, len(train)):
        X_train.append(train[i-7:i, 0])
        y_train.append(train[i, 0])
        
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    
    # Test data
    full_data = np.append(train, test)
    for i in range(len(train)-7, len(full_data)):
        X_test.append(full_data[i-7:i, 0])
    y_test = test
    
    return build_model_and_evaluate(X_train, y_train, X_test, y_test)    



def walk_forward_validation(data_):

    ## val model 1
    stop_date = datetime.datetime.now() + datetime.timedelta(-150)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date > stop_date].iloc[:,2:3].values

    train_ = sc.fit_transform(train)
    test_ = sc.transform(test.iloc[:,2:3].values)
    rmse1 = validate(train_, test_)

    ## val model 2
    stop_date = datetime.datetime.now() + datetime.timedelta(-120)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date > stop_date].iloc[:,2:3].values

    train_ = sc.fit_transform(train)
    test_ = sc.transform(test.iloc[:,2:3].values)
    rmse2 = validate(train_, test_)
    

    ## val model 3
    stop_date = datetime.datetime.now() + datetime.timedelta(-90)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date > stop_date].iloc[:,2:3].values

    train_ = sc.fit_transform(train)
    test_ = sc.transform(test.iloc[:,2:3].values)
    rmse3 = validate(train_, test_)
    

    ## val model 4
    stop_date = datetime.datetime.now() + datetime.timedelta(-60)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date > stop_date].iloc[:,2:3].values

    train_ = sc.fit_transform(train)
    test_ = sc.transform(test.iloc[:,2:3].values)
    rmse4 = validate(train_, test_)
    

    ## val model 5
    stop_date = datetime.datetime.now() + datetime.timedelta(-30)
    train = data_[data_.date_ <= stop_date].iloc[:,2:3].values
    test = data_[data_.date > stop_date].iloc[:,2:3].values

    train_ = sc.fit_transform(train)
    test_ = sc.transform(test.iloc[:,2:3].values)
    rmse5 = validate(train_, test_)
    
    ## choose the model with the best rmse here
    
       


def do_walk_forward_validation_and_get_best_model(data,
                                                  train_end_date,
                                                  learning_rate,
                                                  optimizer):

    stores = data.Store.unique()


    for store in stores:

        data_ = data[data.Store == store]

