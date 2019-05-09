# Imports
#region
from typing import List, Set, Tuple, Any, Dict
import matplotlib.pyplot as plt
import pickle as pl
import seaborn as sns
import pandas as pd
import numpy as np
import quandl
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
from website.financial import utility
from flask import url_for
#endregion


class Strategy:
    """
    Object to store a complex Strategy
    """
    def __init__(self, message = ""):
        """
        Creates a new Strategy Object with quote string, confidence, action (-1, 1)
        Action Works the following way:
            0 - iff Hold
            >0 - Iff Sell, 
        """
        self.message = message
        self.confidence = 0
        self.action = 0

    def __str__(self):
        if self.message != "":
            return self.message
        else:
            if self.action > 0:
                return f"Buy with {self.action*100}% of capital. Confidence Level: {self.confidence}"
            elif self.action < 0:
                return f"Sell {self.action*100}% of held asset. Confidence Level: {self.confidence}"
            else:
                return "Hold"

    def __repr__(self):
        return str(self)

    def updateStrategy(self, new_action, new_confidence, new_message = ""):
        """
        Update The Strategy's Data
        """
        self.message = new_message
        self.confidence = new_confidence
        self.action = new_action


class Stock:
    """
Initializing Notes-
------------------------------------------------------------------------------------------------
1. BSE stocks need to be entered as tickers with BOM atached
     (E.g if HDFC is BOM500180) then ticker = BOM500180
------------------------------------------------------------------------------------------------

This application is in charge of detailing the Stock Class will take in the following informtion
1. Stock Ticker
2. Stock Exchange out of a list of options
    a. BSE -> Uses Quandl for Data
    b. NASDAQ -> Uses AlphaVantage for Data
3. Date Range
4. Method of analysis out of a list of options
    a. Bollinger Bands

Then the application will return
1. Graph with solution and analysis on it
2. Suggestion explicit on whether they should sell
3. A percentage on how sure we are of this suggestion

Publically will be in charge of 
1. Obtaining the data in the form of a csv from the internet
    a. Adapting the data to a standardized     
    b. Short circuiting a response if the data doesn't exist or is too small
2. Calling on the graphing and calculation methods in order and intergrating the display
3. Calling on calculation to formulate a strategy with associated success rate

Privately Will also
1. Graph
2. Compute

"""
    # Initializing and built ins
#region
    def __init__(self, name: str, ticker: str, exchange: str):
        """
        Creates also a Pandas Dataframe with the following 2 columns:        
            A date column with datetime objects within them,
            Associated data column with the adj.price of those dates
            
        If exchange is set to INTERNAL then there must be a preloaded pandas dataframe in local memory
            This df must be named ticker.csv
            dates must be a valid set of dates within the range of the initial date set
        """
        self.name = name
        self.ticker = ticker
        self.exchange = exchange
        self.strategy = Strategy()
        
        attribute_dict = {
            'BSE': 'Close',
            'NASDAQ': '5. adjusted close',
            }
        method_dict = {
            'BSE': self._initializeBSE,
            'NASDAQ': self._initializeNASDAQ,
            }
        sns.set(rc={'axes.facecolor':'#111010', 'figure.facecolor':'#111010','axes.labelcolor':'#fbffc1', 'text.color': '#fbffc1', 'ytick.color': 'white', 'xtick.color': 'white'})
        colors = ['#58ff15','#FFFF00','#24f8e5','#DD0048','#00ffdf'] # Neon Green, Neon Blue, Neon Red, Neon Yellow
        sns.set_palette(colors)

        #dates = pd.date_range(self.dates[0],self.dates[1])
        
        if exchange == "INTERNAL":
            self._initializeINTERNAL()
            self.start_date, self.end_date = self.analyzeBoundary()
            return
      
        self.attribute = attribute_dict[exchange]
        
        
        dftemp = (method_dict[self.exchange]())

        dftemp = dftemp.rename(columns = {self.attribute: name})
        self.df = dftemp[[self.name]]
        #save_location = url_for('static')
        self.df.to_csv(f"website/static/{self.name}({self.ticker}).csv", index_label = "Date")
        self.start_date, self.end_date = self.analyzeBoundary()

    def _initializeBSE(self) -> pd.DataFrame: 
        """
        Returns a pandas dataframe dftemp which needs to be renamed
        Note that the index of this df is already Date and the title is already DateTime
        """
        try:
            dftemp = quandl.get(f'BSE/{self.ticker}', api_key = 'sSGH7WY-GiPzryVyKS9y')
        except quandl.errors.quandl_error.NotFoundError:
            raise utility.NotFoundError
        except:
            raise utility.OtherImportError
        return dftemp
    def _initializeNASDAQ(self) -> pd.DataFrame: 
        """
        Returns a pandas dataframe dftemp which needs to be renamed and joined. 
        Note that the index column of dftemp is already "dates" but it is a string. We change it to a DateTime index
        before returning it. 
        """        
        ts = TimeSeries(key='MCD3GDSY1WYI9LA1', output_format='pandas')
        try:
            dftemp, meta = ts.get_daily_adjusted(symbol=self.ticker, outputsize='full')
        except:
            raise utility.OtherImportError
        dftemp.index = dftemp.index.astype('datetime64', copy = False)

        return dftemp
    def _initializeINTERNAL(self) -> None:
        """
        Returns a pandas dataframe dftemp which needs to be renamed and joined.
        To be used only when we know that a saved file already exists in local storage with the raw csv in it
        The raw csv to have format
        """
        df = pd.read_csv(f'website/static/{self.name}({self.ticker}).csv', index_col = 'Date', parse_dates = True)
        self.df = df
        
    def __repr__(self):
        return f'Stock Object of :{self.name}'
    def __str__(self):
        return f'{self.name}'
    def extract_section(self, starting: datetime, ending: datetime)-> None:
        """
        Accepts a starting and ending datetime. If the dates are not within the current data raises OutofDateException
        If ending date is within the data but not actually present i.e no trades on that day. raises NotIncludedError
        If dates within data the stock.df object is mutated to only have that section(inclusive). 
        Also updates variables start_date and end_date to match
        """
        starting, ending = np.datetime64(starting), np.datetime64(ending)
        if not utility.date_within_inclusive_range(starting, self.start_date, self.end_date) or not utility.date_within_inclusive_range(ending, self.start_date, self.end_date):
            raise utility.OutDatedError(f"starting - {utility.represent_date(starting)}. start data - {utility.represent_date(self.start_date)} end data -{utility.represent_date(self.end_date)}")
        if ending not in self.df.index.values:
            #print(type(ending), type(self.df.index.values[0]))
            #print(f"This is ending {ending}.")
            #print(f"This is the bool {ending not in self.df.index.values}")
            #print(f"Heres values {self.df.index.values}")
            raise utility.NotIncludedError(utility.represent_date(ending))
        #print(ending in self.df.index.values)
        #print(starting in self.df.index.values)
        self.df = self.df[starting: ending]
        self.start_date, self.end_date = self.analyzeBoundary()




#endregion

    # Utility
    #region
    def analyzeBoundary(self)->Tuple[datetime, datetime]:
        """
        Returns the unbounded Tuple(start_date, end_date)
        Precondition:
            self.df exists
        """
        return self.df.index.values[0], self.df.index.values[-1]

    def get_current_price(self)->float:
        """
        Returns the latest recorded price on the data
        As numpy float64
        """
        return self.df.iloc[-1][0]
    #endregion

   # Computation
   #region
    def _rollingMean(self, timeFrame):
     """
     Rolling Mean
     """
     return self.df[self.name].rolling(timeFrame).mean()

    # Rolling Standard Deviation Function
    def _rollingStandardDeviation(self, timeFrame):
        """
        Calculate Standard Deviation Rolling
        """
        return self.df[self.name].rolling(timeFrame).std()

    # Bollinger Bands Function
    def _ComputeBollingerBands(self, timeFrame = 20, bandSeparation = 2, overlapMarginRate = 0.0075, predictionMarginRate = 0.0225, testing = False, testParameter = "None" ):
        """
        Computes The Bollinger Bands Method of Analysis on the Stock and returns a Tuple
        Parameters
        timeFrame: Time Frame of Rolling Statistics, Higher is less risk
        bandSeparation: How much of a deviation you consider significant, Higher is less risk
        overlapMargin: How much of a margin do you consider prices trivially the same
        predictionMargin: How much of a prediction error do you consider tolerable
        testing: Are you Testing
        testParameter: If so what are you testing
        """
        # Initialize
        #region
        rm = self._rollingMean(timeFrame)
        rstd = self._rollingStandardDeviation(timeFrame)
        upperBand = rm + bandSeparation*rstd
        lowerBand = rm - bandSeparation*rstd
        current_price_series = pd.Series(self.df[self.name])
        #print(self.df)
        #print(f"Current Price_Series length is {(len(current_price_series))}. For date {self.dates[1]}. For {self.name}")
        last_price = current_price_series[(len(current_price_series))-1]
        ouUpperBound = upperBand*(1 + overlapMarginRate)
        olUpperBound = upperBand*(1- overlapMarginRate)
        ouLowerBound = lowerBand*(1 + overlapMarginRate)
        olLowerBound = lowerBand*(1 - overlapMarginRate)
        puUpperBound = upperBand*(1 + predictionMarginRate)
        plUpperBound = upperBand*(1- predictionMarginRate)
        puLowerBound = lowerBand*(1 + predictionMarginRate)
        plLowerBound = lowerBand*(1 - predictionMarginRate)
        current_stage = 4
        previous_stage = 4
        previous_stage_age = 0
        # Stages Detailed Below
        """
        Stages:
        1
        ---------- Upper UpperBound Overlap
        2
        ---------- Lower UpperBound Overlap
        3
        ---------- Lower UpperBound Prediction
        4
        ---------- Upper LowerBound Prediction
        5
        ---------- Upper LowerBound Overlap
        6
        ---------- Lower LowerBound Overlap
        7
        """
        #endregion
        
        # Advanced Initialization to find previous stage age, previous stage and current stage
        #region
        for i in range(len(current_price_series)):
            temp_stage = 0
            # Find Temp Stage
            #region
            value = current_price_series[i]
            if np.isnan(olUpperBound[i]):
                temp_stage = current_stage
            elif value >= ouUpperBound[i]:
                temp_stage = 1
            elif value >= olUpperBound[i]:
                temp_stage = 2
            elif value >= plUpperBound[i]:
                temp_stage = 3
            elif value >= puLowerBound[i]:
                temp_stage = 4
            elif value >= ouLowerBound[i]:
                temp_stage = 5
            elif value >= olLowerBound[i]:
                temp_stage = 6
            else:
                temp_stage = 7
            #endregion
            if temp_stage == current_stage:
                previous_stage_age += 1
            else:
                previous_stage, current_stage = current_stage, temp_stage
                previous_stage_age = 0
                #print("Change Detected From {} to {} at {}".format(previous_stage, current_stage, i))
        #endregion
                
        # Stage Assignment
        #region
        if current_stage == 4:
            self.strategy.updateStrategy(0,0,"Prediction: Hold. Last Chance For Decisive Action: {} days ago.".format(previous_stage_age))

        elif current_stage == 3:
            if previous_stage < current_stage:
                self.strategy.updateStrategy(0,0,"Prediction: Watch Very Closely, Potential Sell Upcoming.")
            else:
                self.strategy.updateStrategy(-0.7,0.7)
                
        elif current_stage == 2:
            if previous_stage == 1:
                self.strategy.updateStrategy(-0.95,0.95)
                
            else:
                self.strategy.updateStrategy(-0.8,0.8)
        elif current_stage == 1:
            self.strategy.updateStrategy(-0.8,0.8)
       
        elif current_stage == 5:
            if previous_stage < current_stage:
                self.strategy.updateStrategy(0 , 0, "Prediction: Watch Very Closely, Potential Buy Upcoming")
            else:
                self.strategy.updateStrategy(0.7,0.7)
        elif current_stage == 6:
            if previous_stage == 7:
                self.strategy.updateStrategy(0.95,0.95)
            else:
                self.strategy.updateStrategy(0.8,0.8)
        elif current_stage ==7:
            self.strategy.updateStrategy(0.8,0.8)
        else:
            self.strategy.updateStrategy(0,0, new_message= "Insufficient Data To Predict")
        #endregion
        

        graphing_tuple = ( (("Bollinger Bands Analysis For " + str(self.name) ), "Date", "Price")  ,   (upperBand, lowerBand) )
        
        # Special Case for Testing
        #region
        if testing:
            if testParameter  == "timeFrame":
                pass
            elif testParameter == "bandSeparation":
                pass
            elif testParameter == "overlapMarginRate":
                Uupper = upperBand*(1+overlapMarginRate)
                Ulower = upperBand*(1-overlapMarginRate)
                Lupper = lowerBand*(1+overlapMarginRate)
                Llower = lowerBand*(1-overlapMarginRate)
                graphing_tuple = (graphing_tuple[0], graphing_tuple[1], (Uupper, Ulower, Lupper, Llower), ('High Upper', 'High Lower', 'Low Upper', 'Low Lower') )
            elif testParameter == "predictionMarginRate":
                Uupper = upperBand*(1+predictionMarginRate)
                Ulower = upperBand*(1-predictionMarginRate)
                Lupper = lowerBand*(1+predictionMarginRate)
                Llower = lowerBand*(1-predictionMarginRate)
                graphing_tuple = (graphing_tuple[0], graphing_tuple[1], (Uupper, Ulower, Lupper, Llower), ('High Upper', 'High Lower', 'Low Upper', 'Low Lower') )

            else:
               return (graphing_tuple)
            #endregion
        return (graphing_tuple)
   #endregion

   # Graphical
   #region
    def _GraphBollingerBands(self, info: Tuple):
        """
        Generates a plot and saves it to a pickle location as method.pickle(TYPE IDK YET)

        """
        basic = info[0]
        lowerBand = info[1][1]
        upperBand = info[1][0]
        ax = self.df[self.name].plot(title = basic[0], label = self.name, fontsize = 12)
        upperBand.plot(label = "Upper Band", ax = ax)
        lowerBand.plot(label = "Lower Band", ax = ax)
        ax.set_xlabel(basic[1])
        ax.set_ylabel(basic[2])
        ax.legend(loc = "upper left")
        #Must Make Save
        pl.dump(ax, open('bollingerbands.pickle',  'wb'))
        plt.show()
        return None

   #endregion

   # Testing and Internal Only
   #region
    def test_Bollinger_Parameter_Sensitivity(self, testParameter, _timeFrame = 20, _bandSeparation = 2, _overlapMarginRate = 0.0075, _predictionMarginRate = 0.0225):
        """
        Used to Change Parameters of Bollinger and show the different options.
        Testing Only
        """
        info = self._ComputeBollingerBands(timeFrame= _timeFrame, bandSeparation = _bandSeparation, overlapMarginRate = _overlapMarginRate, predictionMarginRate = _predictionMarginRate, testing = True, testParameter= testParameter)
        basic = info[0]
        bands = info[1]
        lowerBand = bands[1]
        upperBand = bands[0]
        bands = info[2]
        ax = self.df[self.name].plot(title = "Test For "+ basic[0] + ": "+testParameter, label = self.name, fontsize = 12)
        upperBand.plot(label = "Upper Band", ax = ax)
        lowerBand.plot(label = "Lower Band", ax = ax)
        for band in range(len(bands)):
            bands[band].plot(label = info[3][band], ax = ax)
        ax.set_xlabel(basic[1])
        ax.set_ylabel(basic[2])
        ax.legend(loc = "upper left")
        #Must Make Save
        plt.show()
        return None

   #endregion

    # Access Functions

    def implimentAnalysis(self, method: str) -> Tuple:
        """
        Returns a Tuple that with help with graphing it has two subTuples such that 
        the value to the tuple[0] will be a tuple in the following format
            (title, x axis label, y axis label), the second will be contingent on method
        -------------------------------------------------------------------------------------
        Current Options
        -------------------------------------------------------------------------------------
        1. Bollinger Band Analysis : 'bollingerbands'
        """
        methoddict = {
            'bollingerbands': self._ComputeBollingerBands
            }
        method_to_run = methoddict[method]
        return method_to_run()

    def create_Graph(self, method: str, info: Tuple)-> None:
        """
        Take in the input of the implimentAnalysis and save the plot to a location on the database with name method.format

        """
        methoddict = {
            'bollingerbands': self._GraphBollingerBands
            }
        method_to_run = methoddict[method]
        method_to_run(info)

    def simulateAnalysis(self, method: str, start_date: Tuple[int, int, int], frequency = 7) -> float:
        """
        Returns the % gain/ loss of the stock if 'method' was used starting from 'start_date'
        Default Returns -1 if the start_date is less than 2 months from the first date in the stock data
        Insufficient Data if start_date is within 2 months of self.start_date

        start_date: is in format (YYYY, MM, DD) with YYYY, MM and DD as integers
        frequency: integer that represents the number of days between each trade
        --------------------------------------------------------------------------------------
        Current Options
        --------------------------------------------------------------------------------------
        1. Bollinger Band Analysis : 'bollingerbands'
        """
        starting = datetime(start_date[0], start_date[1], start_date[2])
        #print(type(starting))
        #print(type(self.start_date))
        #print(type(self.end_date))
        if not utility.date_within_inclusive_range(starting, self.start_date, self.end_date):
            raise utility.OutDatedError(f"Trying start date of analysis - {utility.represent_date(starting)} but data starts only from {utility.represent_date(self.start_date)} and ends by {utility.represent_date(self.end_date)}")
        if not utility.date_within_days(starting, self.start_date, 62):
            raise utility.InsufficientDataError
        
        initial_capital = 100000
        capital = initial_capital
        n_stocks = 0
        price = 1 # to change scope 1 not relevant
        for date in pd.date_range(starting, self.end_date, freq= f"{frequency}D"):
            a = Stock(self.name, self.ticker, "INTERNAL")
            try:
                a.extract_section(self.start_date, date)
            except utility.NotIncludedError:
                #print("Fails This")
                continue
            a.implimentAnalysis(method)
            price = a.df.iloc[-1][0] # Code to get the last element in the last row
            final_action = a.strategy.action* a.strategy.confidence
            #print(f"Before {date}, capital is {capital}, going under action {action}")
            #print(f'actually reaches here for {date}')
            if final_action > 0 :
                if price > final_action * capital:
                    #print("Price > capital")
                    continue
                else:
                    n_buy = ((final_action*capital )/price)//1
                    capital -= n_buy* price
                    n_stocks += n_buy
                    #print("Buys")
            elif final_action < 0:
                if n_stocks == 0:
                    #print("No stocks")
                    continue
                else:
                    n_sell = abs((final_action * n_stocks))//1
                    n_stocks -= n_sell
                    capital += n_sell * price
                    #print("Sells")
            else:
                #print("Price = capital")
                continue
        #return capital
        return ((capital + price*n_stocks)/(initial_capital))*100
