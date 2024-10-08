"""
Module: visualisation

This module contains classes for visualising the traffic flow properties
"""

from abc import ABC
import pandas as pd
from pandas import DataFrame
from matplotlib import pyplot as plt
from matplotlib.pyplot import Axes
from typing import Dict, List,Set, Tuple
import numpy as np

class FundamentalDiagram():
    def __init__(self,edge_id :str) -> None:
        """
        Inputs:
        self,
        edge_id :str

        Returns:
        The Fundamental Diagram object.
        """
        self.edge_id : str = edge_id
        self.data : Dict[str,List[int]]={'speed' : [],
                                         'flow' : [],
                                         'vehicle_count' :[]} 
        self.vehicles_in_edge :Set[str] = set()
        self.edge_length : int = 0

    def update(self,mean_speed : int,vehicle_ids : Set[str]) -> None:
        """
        Function: update

        Updates the data stored in the object.

        Args:
            self,
            mean_velocity : int, vehicle_ids : Set[str]

        Returns:
        None
        """
        self.data['speed'].append(mean_speed * 3.6)
        count = len(vehicle_ids)
        self.data['vehicle_count'].append(count)
        vehicles_left_count = len(self.vehicles_in_edge.difference(vehicle_ids))   
        self.vehicles_in_edge = vehicle_ids
        self.data['flow'].append(vehicles_left_count) # vehicles per second
    
    def to_dataframe(self) -> DataFrame:
        """
        Function: to_dataframe

        Converts the metric to a DataFrame object which contains the flow and velocity data per timestep.

        Args:
        self

        Returns:
        DataFrame object.
        """
        pd =  pd.DataFrame(self.data)
        pd['density']= pd['vehicle_count']/self.edge_length
        return pd
    
    def plot(self, dlabel : str= 'Density (veh/km)',qlabel : str = 'Flow (veh/hr)',title :str = 'Flow vs Density') -> Tuple:
        """
        Function: plot

        Generates the plot of the fundamental diagram.

        Returns:
        Tuple object containing Figure and Axes
        """
        df = pd.DataFrame(self.data,index=pd.date_range(0,periods=len(self.data['speed']),freq='s'))
        df['agg_speed'] = df['speed'] * df['vehicle_count']
        df_aggregated = df.resample('T').agg({'flow': 'sum', 'agg_speed': 'sum','vehicle_count' : 'sum'})
        df_aggregated['speed'] = df_aggregated['agg_speed']/df_aggregated['vehicle_count']
        df_aggregated['density'] = df_aggregated['vehicle_count'] * 60/ (self.edge_length * 3.6)
        df_aggregated['flow'] = df_aggregated['flow'] * 60 # to per hours
        fig,axes = plt.subplots(figsize=(10, 6))
        plot = axes.scatter(df_aggregated['density'], df_aggregated['flow'], marker='o', linestyle='-', c = df_aggregated['speed'],alpha=0.7)
        cbar = plt.colorbar(plot)
        cbar.set_label('Speed (kmph)')
        # Add labels and title
        axes.set_xlabel(dlabel);
        axes.set_ylabel(qlabel)
        axes.set_title(title)
        axes.grid(True)
        return fig,axes

class TimeDistance():
    def __init__(self, route_edges : Tuple[str,str],timespan : Tuple[int,int]) -> None:
        """
        Inputs:
        self,
        edge_id :str

        Returns:
        The Fundamental Diagram object.
        """
        self.data : Dict[str,List[int]]= {} 
        self.route_edges = route_edges
        self.timespan = timespan
        self.time_diff = self.timespan[1] - self.timespan[0]
        self.start_time = timespan[0]

    def update(self,vehicle_id : str, distance :int, time : int) -> None:
        """
        Function: update

        Updates the data stored in the object.

        Args:
            self,
            mean_velocity : int, vehicle_ids : Set[str]

        Returns:
        None
        """
        time_delta = time - self.start_time
        if not vehicle_id in self.data:
            self.data[vehicle_id] = [np.NaN]*self.time_diff
        
        self.data[vehicle_id][time_delta] = distance
            
            
    
    def to_dataframe(self) -> DataFrame:
        """
        Function: to_dataframe

        Converts the metric to a DataFrame object which contains the flow and velocity data per timestep.

        Args:
        self

        Returns:
        DataFrame object.
        """
        return pd.DataFrame(self.data)
    
    def plot(self, tlabel : str= 'Time (s)',dlabel : str = 'Distance (km)',title :str = 'Distance vs Time') -> Tuple:
        """
        Function: plot

        Generates the plot of the fundamental diagram.

        Returns:
        Tuple object containing Figure and Axes
        """
        df = pd.DataFrame(self.data)
        fig,axes = plt.subplots(figsize=(10, 6))
        for vehicle_id in df.columns:
            axes.plot(df.index + self.start_time, df[vehicle_id], marker='.')

        # Add labels and title
        axes.set_xlabel(tlabel)
        axes.set_ylabel(dlabel)
        axes.set_title(title)
        axes.grid(True)
        return fig,axes