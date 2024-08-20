from modules.data import data_loader
from modules.sr import result_saver
from modules.experiment.tscv import get_tscv_results

import time

def save_results(prediction_length,
                ticker, 
                frequency, 
                type_of_data,
                folds,
                context_length,
                batch_size,
                max_epochs,
                ft_length,
                ft_frequency,
                ft_gap,
                start_date,
                end_date,
                tscv_repeats,
                rtrn):


    # data config
    data_config = {"ticker" : ticker,
                   "type" : type_of_data,
                   "frequency" : frequency,
                   "start" : start_date,
                   "end" : end_date,
                   "rtrn" : rtrn}
    
    # loading the data
    data = data_loader.get_data(**data_config)
    #ft_data = data_loader.get_data(data_type=type_of_data, kwargs=ft_data_config)

    data_length = len(data)
    #ft_length = len(ft_data)

    if folds == "max":
        folds = int((data_length - ft_length - ft_gap) / prediction_length)
    
    print(f"PL={prediction_length}__T={ticker}__FR={frequency}__TOD={type_of_data}__FO={folds}__CLTS={context_length}__SD={start_date}__ED={end_date}__FTL={ft_length}__DL={data_length}__FTF={ft_frequency}__FTG={ft_gap}__TSCVR={tscv_repeats}__BS={batch_size}__ME={max_epochs}")
    start = time.time()

    # getting the TSCV results
    r, p = get_tscv_results(data = data,
                           prediction_horizon=prediction_length,
                           context_length=context_length, 
                           folds=folds, 
                           frequency=frequency,
                           ft_length=ft_length,
                           batch_size=batch_size,
                           max_epochs=max_epochs,
                           fine_tune_frequency=ft_frequency,
                           ft_gap = ft_gap,
                           tscv_repeats=tscv_repeats)
    
    end = time.time()

    elapsed_time = end - start
    print(f"Experiment finished in: {elapsed_time:.2f} seconds")
    
    # experiment name
    if "/" in ticker:
        ticker = ticker.replace("/", "")
    experiment_name = f"T={ticker}__FR={frequency}__T_O_D={type_of_data}__FO={folds}__C_L_T_S={context_length}__S_D={start_date}__E_D={end_date}__FT_L={ft_length}__FT_F={ft_frequency}__FT_G={ft_gap}__TSCV_R={tscv_repeats}.csv"

    # saving the results
    result_saver.save_results(r, experiment_name, type="evaluation")
    result_saver.save_results(p, experiment_name, type="prediction")    

