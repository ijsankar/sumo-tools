"""
Module: data_collector

This module contains the DataCollector class which can collect data from SUMO simulation.
"""

from typing import List,Tuple,Set
from metrics import WaitingTime, Throughput
from visualisation import FundamentalDiagram, TimeDistance
import libsumo as traci
from traci import StepListener
class DataCollector(StepListener):
    """
    Class: DataCollector

    Provides capability for collecting simulation data from SUMO using traci/libsumo
    """
    def __init__(self) -> None:
        """
        Args:
        self

        Returns:
        The DataCollector object
        """
        id = traci.addStepListener(self)
        self.id = id
        edges : List[str] = list(traci.edge.getIDList())
        while (edges[-1].endswith('-sink') or edges[-1].endswith('-source')):
            edges.pop()
        self.edges = edges
        self.waiting_time = None
        self.throughput = None
        self.fundamental_diagram = None
        self.time_distance_diagram = None
        self.step_count = 0

    def stop_collecting(self) -> None :
        """
        Function: stop

        Set DataCollector to not collect anymore .

        Args:
        self

        Returns:
        None
        """
        if self.id != None:
            traci.removeStepListener(self.id)
            self.id = None

    def __del__(self) -> None:
        self.stop_collecting()

    def initialised(self) -> bool:
        """
        Function: initialised

        Checks if DataCollector was initialised successfully.

        Args:
        self

        Returns:
        True if DataCollector was initialised
        """
        return self.id != None
        
    def add_waiting_time(self, waiting_time : WaitingTime) -> None:
        """
        Function: add_waiting_time

        Adds a WaitingTime object to the DataCollector instance. Used for collecting the waiting time data for all edges.

        Args:
        self, waiting_time : WaitingTime

        Returns:
        None
        """
        self.waiting_time = waiting_time

    def remove_waiting_time(self,waiting_time : WaitingTime) -> bool:
        """
        Function: remove_waiting_time

        Removes a WaitingTime object from DataCollector

        Args:
        self,waiting_time : WaitingTime

        Returns:
        True if the the object was removed.
        """
        if self.waiting_time == waiting_time:
            self.waiting_time = None
            return True
        return False
    
    def add_throughput(self, throughput : Throughput) -> None:            
        """
        Function: add_throughput

        Adds a Throughput object to the DataCollector instance. Used for collecting the throughput data for all edges.

        Args:
        self, throughput : Throughput

        Returns:
        None
        """
        self.throughput = throughput

    def remove_throughput(self,throughput : Throughput) -> bool:
        """
        Function: remove_throughput

        Removes a Throughput object from DataCollector

        Args:
        self,throughput : Throughput

        Returns:
        True if the the object was removed.
        """
        if self.throughput == throughput:
            self.throughput = None
            return True
        return False
    
    def add_fundamental_diagram(self, fundamental_diagram : FundamentalDiagram) -> None:            
        """
        Function: add_fundamental_diagram

        Adds a FundamentalDiagram object to the DataCollector instance.

        Args:
        self, fundamental_diagram : FundamentalDiagram

        Returns:
        None
        """
        self.fundamental_diagram = fundamental_diagram
        for id in traci.lane.getIDList():
            if traci.lane.getEdgeID(id) == fundamental_diagram.edge_id:
                lane_length = traci.lane.getLength(id)
                fundamental_diagram.edge_length = lane_length
                break

    def remove_fundamental_diagram(self,fundamental_diagram : FundamentalDiagram) -> bool:
        """
        Function: remove_fundamental_diagram

        Removes a FundamentalDiagram object from DataCollector

        Args:
        self,fundamental_diagram : FundamentalDiagram

        Returns:
        True if the the object was removed.
        """
        if self.fundamental_diagram == fundamental_diagram:
            self.fundamental_diagram = None
            return True
        return False
    
    def add_time_distance_diagram(self, time_distance_diagram : TimeDistance) -> None:            
        """
        Function: add_fundamental_diagram

        Adds a TimeDistance object to the DataCollector instance.

        Args:
        self, fundamental_diagram : TimeDistance

        Returns:
        None
        """
        self.time_distance_diagram = time_distance_diagram

    def remove_time_distance_diagram(self,time_distance_diagram : TimeDistance) -> bool:
        """
        Function: remove_time_distance_diagram

        Removes a TimeDistance object from DataCollector

        Args:
        self,time_distance_diagram : TimeDistance

        Returns:
        True if the the object was removed.
        """
        if self.time_distance_diagram == time_distance_diagram:
            self.time_distance_diagram = None
            return True
        return False
    
    # called by traci when a simulation step occurs
    def step(self,step : int) -> None:
        """
        Function: step

        For internal use. 
        """
        if self.waiting_time != None:
            average_wait_times = {}
            for edge in self.edges:
                waiting_time = traci.edge.getWaitingTime(edge)
                vehicle_count = traci.edge.getLastStepVehicleNumber(edge)
                average_wait_times[edge] = waiting_time/vehicle_count if vehicle_count !=0 else 0
            self.waiting_time.update(average_wait_times)
        if self.throughput != None:
            edge_ids_to_collect = self.throughput.edge_ids if self.throughput.edge_ids != None else self.edges
            for edge_id in edge_ids_to_collect:
                    vehicle_ids = traci.edge.getLastStepVehicleIDs(edge_id)
                    self.throughput.update(edge_id,set(vehicle_ids))
        if self.fundamental_diagram != None:
            vehicle_ids = traci.edge.getLastStepVehicleIDs(self.fundamental_diagram.edge_id)
            vehicle_count = len(vehicle_ids)
            if vehicle_count != 0:
                mean_velocity = sum(traci.vehicle.getSpeed(id) for id in vehicle_ids) /vehicle_count
            else:
                mean_velocity = 0

            self.fundamental_diagram.update(mean_velocity,set(vehicle_ids))
        if self.time_distance_diagram != None:
            if (self.time_distance_diagram.timespan[0] <= self.step_count) and (self.time_distance_diagram.timespan[1] > self.step_count):
                vehicles = traci.vehicle.getIDList()
                teleporting = traci.vehicle.getTeleportingIDList()
                vehicles = set(vehicles).difference(set(teleporting))
                for vehicle in vehicles:
                    route = traci.vehicle.getRoute(vehicle)
                    if route[0] == self.time_distance_diagram.route_edges[0] and route[-1] == self.time_distance_diagram.route_edges[1]:
                        distance = traci.vehicle.getDistance(vehicle)
                        self.time_distance_diagram.update(vehicle,distance,self.step_count)
        self.step_count += 1
        return True


