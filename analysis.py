#!/usr/bin/env python3
"""
Airline Route Profitability Analysis - Main Execution Script
Runs the complete analysis pipeline and generates all outputs
"""

import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from airline_analyzer import AirlineRouteAnalyzer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def setup_directories():
    directories = [
        'data/raw',
        'data/processed', 
        'data/sample',
        'reports',
        'outputs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logging.info(f"Ensured directory exists: {directory}")

def main():
    parser = argparse.ArgumentParser(description='Run Airline Route Profitability Analysis')
    parser.add_argument('--use-sample-data', action='store_true', 
                       help='Use generated sample data instead of real data')
    parser.add_argument('--output-dir', default='outputs',
                       help='Output directory for results')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization generation')
    
    args = parser.parse_args()
    
    setup_directories()
    logging.info("Starting Airline Route Profitability Analysis")
    
    try:
        analyzer = AirlineRouteAnalyzer()
        
        if args.use_sample_data:
            logging.info("Generating sample data...")
            analyzer.generate_sample_data()
            logging.info("Sample data generated successfully")
        else:
            logging.info("Loading real data...")
            logging.warning("Real data loading not implemented, using sample data")
            analyzer.generate_sample_data()
        
        logging.info("Calculating route profitability...")
        profitability_df = analyzer.calculate_profitability()
        logging.info(f"Analyzed {len(profitability_df)} routes")
        
        logging.info("Generating business insights...")
        insights = analyzer.generate_insights()
        
        if not args.no_viz:
            logging.info("Creating visualizations...")
            analyzer.create_visualizations()
            logging.info("Visualizations created")
        
        logging.info("Generating recommendations...")
        recommendations = analyzer.generate_recommendations()
        
        output_prefix = f"{args.output_dir}/airline_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logging.info(f"Exporting results to {output_prefix}_*")
        analyzer.export_results(output_prefix)
        
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Routes Analyzed: {insights['summary_stats']['total_routes']}")
        print(f"Profitable Routes: {insights['summary_stats']['profitable_routes']}")
        print(f"Avg Profit Margin: {insights['summary_stats']['average_profit_margin']:.1f}%")
        print(f"Total Annual Profit: ${insights['summary_stats']['total_annual_profit']/1000000:.1f}M")
        print(f"Avg Load Factor: {insights['summary_stats']['average_load_factor']:.1%}")
        
        print(f"\nTOP 3 PROFITABLE ROUTES:")
        for i, route in enumerate(insights['most_profitable_routes'][:3], 1):
            profit_millions = route['profit'] / 1000000
            print(f"   {i}. {route['route_id']}: ${profit_millions:.1f}M ({route['profit_margin']:.1f}% margin)")
        
        print(f"\nKEY RECOMMENDATIONS:")
        print(f"   Expand: {len(recommendations['expand_routes']['routes'])} high-ROI routes")
        print(f"   Optimize: {len(recommendations['optimize_routes']['routes'])} underperforming routes")
        print(f"   Review: {len(recommendations['consider_discontinuing']['routes'])} loss-making routes")
        
        print(f"\nResults saved to: {args.output_dir}/")
        print("="*60)
        
        logging.info("Analysis completed successfully!")
        return 0
        
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)