#!/usr/bin/env python3
"""
Test suite for Airline Route Profitability Analysis
"""

import unittest
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from airline_analyzer import AirlineRouteAnalyzer

class TestAirlineAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = AirlineRouteAnalyzer()
        self.analyzer.generate_sample_data()
    
    def test_data_generation(self):
        self.assertIsNotNone(self.analyzer.routes_data)
        self.assertIsNotNone(self.analyzer.passenger_data)
        self.assertIsNotNone(self.analyzer.cost_data)
        self.assertIsNotNone(self.analyzer.fuel_data)
        
        self.assertGreater(len(self.analyzer.routes_data), 0)
        self.assertGreater(len(self.analyzer.passenger_data), 0)
        self.assertGreater(len(self.analyzer.cost_data), 0)
        self.assertEqual(len(self.analyzer.fuel_data), 12)
    
    def test_route_data_integrity(self):
        routes_df = self.analyzer.routes_data
        
        required_columns = ['route_id', 'origin', 'destination', 'distance_miles', 
                          'flight_time_hours', 'daily_flights', 'aircraft_type']
        
        for col in required_columns:
            self.assertIn(col, routes_df.columns)
        
        self.assertTrue(all(routes_df['distance_miles'] > 0))
        self.assertTrue(all(routes_df['flight_time_hours'] > 0))
        self.assertTrue(all(routes_df['daily_flights'] > 0))
        
        self.assertEqual(len(routes_df['route_id']), len(routes_df['route_id'].unique()))
    
    def test_passenger_data_integrity(self):
        passenger_df = self.analyzer.passenger_data
        
        required_columns = ['route_id', 'month', 'passengers', 'load_factor', 
                          'avg_ticket_price', 'revenue']
        
        for col in required_columns:
            self.assertIn(col, passenger_df.columns)
        
        self.assertTrue(all(passenger_df['passengers'] >= 0))
        self.assertTrue(all(passenger_df['load_factor'].between(0, 1)))
        self.assertTrue(all(passenger_df['avg_ticket_price'] > 0))
        self.assertTrue(all(passenger_df['revenue'] >= 0))
        
        self.assertTrue(all(passenger_df['month'].between(1, 12)))
    
    def test_cost_data_integrity(self):
        cost_df = self.analyzer.cost_data
        
        required_columns = ['route_id', 'fuel_cost_per_flight', 'crew_cost_per_flight',
                          'maintenance_cost_per_flight', 'airport_fees_per_flight', 
                          'total_cost_per_flight', 'monthly_cost']
        
        for col in required_columns:
            self.assertIn(col, cost_df.columns)
        
        for col in required_columns[1:]:
            self.assertTrue(all(cost_df[col] > 0))
        
        calculated_total = (cost_df['fuel_cost_per_flight'] + 
                          cost_df['crew_cost_per_flight'] + 
                          cost_df['maintenance_cost_per_flight'] + 
                          cost_df['airport_fees_per_flight'])
        
        np.testing.assert_array_almost_equal(
            cost_df['total_cost_per_flight'].values, 
            calculated_total.values, 
            decimal=2
        )
    
    def test_profitability_calculation(self):
        profitability_df = self.analyzer.calculate_profitability()
        
        self.assertIsNotNone(profitability_df)
        
        required_columns = ['route_id', 'revenue', 'profit', 'profit_margin', 
                          'passengers', 'load_factor', 'roi']
        
        for col in required_columns:
            self.assertIn(col, profitability_df.columns)
        
        self.assertTrue(all(profitability_df['revenue'] >= 0))
        self.assertTrue(all(profitability_df['passengers'] >= 0))
        self.assertTrue(all(profitability_df['load_factor'].between(0, 1)))
        
        self.assertTrue(len(profitability_df) > 0)
    
    def test_insights_generation(self):
        insights = self.analyzer.generate_insights()
        
        required_keys = ['most_profitable_routes', 'least_profitable_routes', 
                        'highest_roi_routes', 'route_type_performance', 'summary_stats']
        
        for key in required_keys:
            self.assertIn(key, insights)
        
        summary = insights['summary_stats']
        self.assertIn('total_routes', summary)
        self.assertIn('profitable_routes', summary)
        self.assertIn('average_profit_margin', summary)
        
        self.assertLessEqual(summary['profitable_routes'], summary['total_routes'])
        
        self.assertIsInstance(insights['most_profitable_routes'], list)
        self.assertIsInstance(insights['least_profitable_routes'], list)
    
    def test_recommendations_generation(self):
        recommendations = self.analyzer.generate_recommendations()
        
        required_keys = ['expand_routes', 'optimize_routes', 'consider_discontinuing']
        
        for key in required_keys:
            self.assertIn(key, recommendations)
        
        for key in required_keys:
            self.assertIn('routes', recommendations[key])
            self.assertIn('rationale', recommendations[key])
            self.assertIsInstance(recommendations[key]['routes'], list)
            self.assertIsInstance(recommendations[key]['rationale'], str)
    
    def test_route_classification(self):
        origin_info = {'hub_status': 'Major'}
        dest_info = {'hub_status': 'Major'}
        
        result = self.analyzer._classify_route(origin_info, dest_info)
        self.assertEqual(result, 'Major-Major')
        
        dest_info = {'hub_status': 'Medium'}
        result = self.analyzer._classify_route(origin_info, dest_info)
        self.assertEqual(result, 'Major-Medium')
    
    def test_seasonal_factors(self):
        summer_factor = self.analyzer._get_seasonal_factor(7, 'Major-Major')
        winter_factor = self.analyzer._get_seasonal_factor(2, 'Major-Major')
        
        self.assertGreater(summer_factor, winter_factor)
        
        for month in range(1, 13):
            factor = self.analyzer._get_seasonal_factor(month, 'Major-Major')
            self.assertGreater(factor, 0)
    
    def test_export_functionality(self):
        self.analyzer.calculate_profitability()
        
        try:
            self.analyzer.export_results('test_export')
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Export failed with exception: {e}")

class TestDataValidation(unittest.TestCase):
    def setUp(self):
        self.analyzer = AirlineRouteAnalyzer()
    
    def test_empty_data_handling(self):
        with self.assertRaises((AttributeError, TypeError)):
            self.analyzer.calculate_profitability()
    
    def test_data_consistency(self):
        self.analyzer.generate_sample_data()
        
        route_ids_routes = set(self.analyzer.routes_data['route_id'])
        route_ids_passengers = set(self.analyzer.passenger_data['route_id'])
        route_ids_costs = set(self.analyzer.cost_data['route_id'])
        
        self.assertTrue(route_ids_passengers.issubset(route_ids_routes))
        self.assertTrue(route_ids_costs.issubset(route_ids_routes))

if __name__ == '__main__':
    unittest.main(verbosity=2)