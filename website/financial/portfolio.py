from typing import Tuple, List, Dict, Any, Union, Optional
from website.financial.stock import Stock
from website.financial import utility
import datetime




class Portfolio(object):
    """A collection of Stocks"""

    # Initializing and Mutating
    #region
    def __init__(self, stocks: List[Tuple[str, str, str, int]], capital = 100)->None:
        """
        Create a new Portfolio object
        stocks to be in format: (name, ticker, exchange, no:stocks owned)
        self.stocks is a dictionary of format self.stocks['name of stock'] = Tuple[Stock Object, n:stocks]
        Representation Invariant:
            n is always non negative
        """
        self.capital = capital
        self.stocks = {}
        for stock in stocks:
            a = Stock(stock[0], stock[1],stock[2])
            self.stocks[str(stock[0])] = [a, stock[3]]
        return

    def buy_stock(self, stock: Tuple[str, str, str, int], free = False)->None:
        """
        Stock to be in format: (name, ticker, exchange, no:stocks owned)
        Addition
           If stock (Identified by name) is not in self.stocks then new entry is added
           If stock is in stock.stocks the number of that stock is incrimented
        Spending
            If stock is not free and there is enough capital to make the purchase it will occur
            If not enough capital then the biggest possible purchase will be made
        """

        if stock[0] not in self.stocks:
            a = Stock(stock[0], stock[1],stock[2])
            self.stocks[str(stock[0])] = [a, 0]

        wanted_no = stock[3]
        if free:
            self.stocks[stock[0]][1] += wanted_no
        else:
            price = self.stocks[stock[0]][0].get_current_price()
            possible_no = self.capital // price
            if wanted_no <= possible_no:
                #print("wanted smaller")
                self.stocks[stock[0]][1] += wanted_no
                self.capital -= price* wanted_no
            else:
                if possible_no == 0:
                    pass
                    #self.stocks.pop(str(stock[0]))
                else:
                    self.stocks[stock[0]][1] += possible_no
                    self.capital -= price * possible_no
        if self.stocks[stock[0]][1] == 0:
            self.stocks.pop(str(stock[0]))
        return
        
    def sell_stock(self, stock_name: str, amount:int, free = False):
        """
        Sells amount of stock. If amount is more than what currently is held only the permissible amount is sold.
        If stock is not in portfolio does nothing.
        If free then no change to capital
        If stock number drops to 0 then stock is removed from the dictionary
        """
        if stock_name not in self.stocks:
            return
        stock_entry = self.stocks[stock_name]
        if stock_entry[1] > amount:
            stock_entry[1] -= amount
            if free:
                return
            else:
                self.capital += amount* stock_entry[0].get_current_price()
        else:
            if free:
                self.stocks.pop(stock_name)
                return
            else:
                self.capital += stock_entry[1] * stock_entry[0].get_current_price()
                self.stocks.pop(stock_name)
                return

    def get_init_data(self)-> List:
        """
        Returns the data that would be needed to initialize an equivalent portfolio object i.e
        List - [ [(name of stock0, ticker of stock0, exchange of stock0, number of stock0),....... ], capital]
        List[List[Tuple[str, str, str, int]], int]
        """
        f = []
        mini = []
        for name in self.stocks:
            data = self.stocks[name]
            a = (name, data[0].ticker, data[0].exchange, data[1])
            mini.append(a)
        f.append(mini)
        f.append(self.capital)
        return f
    #endregion

    # General Group Functions
    #region
    def computeActions(self, method: str) -> Dict:
        """
        Returns a dictionary: The output is a dictionary of format: {ticker: Strategy}

        """
        final = {}
        for name in self.stocks:
            self.stocks[name][0].implimentAnalysis(method)
            final[name] = self.stocks[name][0].strategy
        return final
    
    def simulateAnalysis(self, method: str, start_date, frequency = 7)  -> Dict:
        """
        Returns a dictionary: The output is a dictionary of format : {ticker: % Gain or Loss}
        start_date: is in format (YYYY, MM, DD) with YYYY, MM and DD as integers
        frequency: integer that represents the number of days between each trade
        --------------------------------------------------------------------------------------
        Current Options
        --------------------------------------------------------------------------------------
        1. Bollinger Band Analysis : 'bollingerbands'
        """
        final = {}
        for name in self.stocks:
            final[name] = self.stocks[name][0].simulateAnalysis(method, start_date, frequency)

        return final

    def create_Graph(self, method: str):
        final = {}
        for name in self.stocks:
            info = self.stocks[name][0].implimentAnalysis(method)
            final[name] = self.stocks[name][0].create_Graph(method,info)
        return final
    
    #endregion

    # Portfolio Specific Functions
    #region
    def get_asset_value(self)-> float:
        """
        Returns the amount * price sum for each stock
        """
        f = 0
        for name in self.stocks:
            f += self.stocks[name][0].get_current_price() * self.stocks[name][1]
        return f

    def get_value(self)->float:
        """
        Returns asset value + capital
        """
        return self.capital + self.get_asset_value()
    #endregion