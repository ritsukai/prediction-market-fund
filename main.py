from src.engine.simulation import Simulation
from src.data.sources import MockDataSource, NewsDataSource

def main():
    """
    Main entry point for the prediction market fund simulation.
    """
    print("Starting Prediction Market Fund Simulation...")

    # Initialize data sources
    data_sources = [
        MockDataSource(),
        NewsDataSource()
    ]

    # Initialize and run the simulation
    sim = Simulation(data_sources=data_sources)
    sim.run_step()

    print("Simulation finished.")

if __name__ == "__main__":
    main()
