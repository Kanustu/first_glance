# Import libraries
import pandas as pd
from pandas import DataFrame
from typing import List, Union, Dict
from pydantic import BaseModel
import seaborn as sns
import matplotlib.pyplot as plt
import warnings


class Outputs(BaseModel):
    """
    Base class for input data models.
    """

    class Config:
        """
        Pydantic configuration settings.
        """
        arbitrary_types_allowed = True

        
class NumericOutput(Outputs):
    """
    Model for numeric input data.
    """
    data: DataFrame
    

class NonNumericOutput(Outputs):
    """
    Model for non-numeric input data.
    """
    data: DataFrame
    

class PlotCreation(BaseModel):
    """
    Base class for plot creation models.
    """

    class Config:
        """
        Pydantic configuration settings.
        """
        arbitrary_types_allowed = True
    

class BoxPlotCreation(PlotCreation):
    """
    Model for creating box plots.
    """
    data: DataFrame
    num_cols: int

class HistPlotCreation(PlotCreation):
    """
    Model for creating histogram plots.
    """
    data: DataFrame
    num_cols: int



def numeric_data(data: DataFrame) -> NumericOutput:
    numeric_columns = [column for column in data.columns 
                       if data[column].dtypes == 'int64' or data[column].dtypes == 'float64']
    # Create a new DataFrame with only numeric columns
    dataframe = pd.DataFrame(data, columns=numeric_columns)
    return NumericOutput(data = dataframe).data


def non_numeric_data(data: DataFrame) -> NonNumericOutput:
    non_numeric_columns = [column for column in data.columns
                           if data[column].dtypes != 'int64' and data[column].dtypes != 'float64']
    df = pd.DataFrame(data, columns=non_numeric_columns)
    return NonNumericOutput(data = df).data
    
def create_subplots(data: DataFrame, plot_type: str, num_cols: int) -> None:
    """
    Creates subplots for the specified plot type.

    Parameters:
        data (DataFrame): Input DataFrame.
        plot_type (str): Type of plot ('boxplot' or 'histplot').
        num_cols (int): Number of columns in the grid for subplots.
    """
    numeric_columns = [column for column in data.columns 
                       if data[column].dtypes == 'int64' or data[column].dtypes == 'float64']
    num_plots = len(numeric_columns)
    num_rows = (num_plots + num_cols - 1) // num_cols
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))
    
    for i, column in enumerate(numeric_columns):
        row = i // num_cols
        col = i % num_cols
        if plot_type == 'boxplot':
            sns.boxplot(x=data[column], ax=axes[row, col])
        elif plot_type == 'histplot':
            sns.histplot(x=data[column], ax=axes[row, col])
        axes[row, col].set_title(f'{column}'.capitalize())
    
    plot_title = "Boxplot" if plot_type == 'boxplot' else "Histogram"
    plt.suptitle(f"{plot_title} Analysis", fontsize=16, y=1.02)
    
    for i in range(num_plots, num_rows * num_cols):
        row = i // num_cols
        col = i % num_cols
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()    


def create_heatmap(data: DataFrame) -> None:
    data = numeric_data(data)
    corr_matrix = data.corr()
    
    # Set up the heatmap figure
    plt.figure(figsize=(8, 6))
    
    # Customize the appearance of the heatmap
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", linewidths=.5)
    
    # Add title to the heatmap
    plt.title('Correlation Heatmap')
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the heatmap
    plt.show()


def data_input(csv: str) -> pd.DataFrame:
    """
    Read a CSV file and return its contents as a DataFrame.

    Parameters:
        csv (str): The file path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the CSV file.
    """
    return pd.read_csv(csv)
    
    
def data_describe(data: DataFrame) -> pd.DataFrame:
    """
    Generate descriptive statistics of the DataFrame columns.

    Parameters:
        data (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: Descriptive statistics for the DataFrame columns.
    """
    return data.describe().T.drop(columns='count')
    
    
def data_isnull(data: DataFrame) -> pd.DataFrame:
    """
    Count the number of missing values in each column of the DataFrame.

    Parameters:
        data (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the count of missing values for each column.
    """
    return data.isnull().sum().to_frame().rename(columns={0: 'null_count'})
    

def data_type(data: DataFrame) -> pd.Series:
    """
    Get the data types of each column in the DataFrame.

    Parameters:
        data (pd.DataFrame): The input DataFrame.

    Returns:
        pd.Series: A Series containing the data types of each column.
    """
    return data.dtypes
    
    
def data_count(data: DataFrame) -> dict:
    """
    Count the number of entries in each column of the DataFrame.

    Parameters:
        data (pd.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary containing the count of entries for each column.
    """
    count_dict = {}
    for column in data.columns:
        count_dict[column] = [data.shape[0]]
    return count_dict
    
    
def stats_report(csv: str) -> pd.DataFrame:
    """
    Generate an Exploratory Data Analysis (EDA) report for the DataFrame.

    Parameters:
        data (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: An EDA report containing descriptive statistics, data types, null counts, and entry counts for each                   column.
    """
    data = data_input(csv)
    df1 = pd.DataFrame(data_count(data)).T.rename(columns={0: 'entry_count'})
    df1['data_type'] = data_type(data)
    df1['null_count'] = data_isnull(data)
    df2 = data_describe(data)
    report = pd.merge(df1, df2, left_index=True, right_index=True, how='left')
    return report


def initial_analysis(csv: str, num_cols):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        pd.set_option('mode.use_inf_as_na', True)
        data = data_input(csv)
        print('\n')
        create_subplots(data, 'boxplot', num_cols)
        print('\n\n')
        create_subplots(data, 'histplot', num_cols)
        print('\n\n')
        create_heatmap(data)

    