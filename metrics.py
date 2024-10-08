"""
Module: metrics

This module contains Metric classes for storing various traffic metrics.
"""

import pandas as pd
from pandas import DataFrame
from typing import Dict, List,Set

class WaitingTime():
    """
    Class: WaitingTime

    Stores the average waiting time for each edge across the simulation.
    """
    def __init__(self) -> None:
        """
        Args:
        self

        Returns:
        The WaitingTime object
        """
        self.waiting_times : List[Dict[str,int]] = []

    def update(self,average_waiting_times :Dict[str,int]) -> None:
        """
        Function: update

        Updates the data stored in the object.

        Args:
        self,
        average_waiting_times :Dict[str,int]

        Returns:
        None
        """
        self.waiting_times.append(average_waiting_times)
    
    def to_dataframe(self) -> DataFrame:
        """
        Function: to_dataframe

        Converts the metric to a DataFrame object

        Args:
        self

        Returns:
        DataFrame object.
        """
                
        return pd.DataFrame(self.waiting_times)
    
class Throughput():
    """
    Class: Throughput

    Stores the average throughput for each edge across the simulation.
    """
    def __init__(self, edge_ids : List[str] = None) -> None:
        """
        Inputs:
        self, 
        edge_ids : List[str] = None

        Returns:
        The WaitingTime object
        """
        self.vehicles_in_edge : Dict[str,Set[str]] = {}
        self.vehicles_left_count: Dict[str, List[int]] = {}
        self.edge_ids = edge_ids

    def update(self,edge_id : str,vehicle_ids : Set[str]) -> None:
        """
        Function: update

        Updates the data stored in the object.

        Args:
        self,
        edge_id : str,
        vehicle_ids : Set[str]

        Returns:
        None
        """
        if edge_id in self.vehicles_in_edge:
            vehicles_left_count = len(self.vehicles_in_edge[edge_id].difference(vehicle_ids))   
        else:
            self.vehicles_left_count[edge_id] = []
            vehicles_left_count = 0
        self.vehicles_in_edge[edge_id] = vehicle_ids
        self.vehicles_left_count[edge_id].append(vehicles_left_count)

    def to_dataframe(self) -> DataFrame:
        """
        Function: to_dataframe

        Converts the metric to a DataFrame object

        Args:
        self

        Returns:
        DataFrame object.
        """
                
        return pd.DataFrame(self.vehicles_left_count)