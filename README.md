# London Rental Finder Dashboard

An interactive Dash application for exploring rental listings in central London. The dashboard lets you filter by bedrooms, bathrooms, price, and distance from a chosen location, then visualises the results on an interactive map, a price distribution chart, and a table of relevant listings.

---

## Key features

* Interactive map of properties, coloured by monthly rent and sized by bedroom count  
* Smart filters for bedrooms, bathrooms, and rent range  
* Distance based filtering using the Haversine formula  
* Quick station buttons for common central London locations (Liverpool Street, Moorgate, Bank, and others)  
* Summary cards showing total listings, number matching your filters, average price, and average distance  
* Price distribution histogram for the currently filtered properties  
* Paginated table view with clickable links that open the original listing in a new tab  
* Narrative text block summarising the current filter selection and results  

---

## Project structure

The core of the project is a single Python script that:

* Loads a CSV file of listings into a Pandas data frame  
* Cleans numeric columns and coordinates  
* Defines a Haversine distance helper  
* Constructs a Dash layout (filters, map, charts, and table)  
* Registers callbacks to update everything whenever the user changes filters or interacts with the map  

You only need the Python script and the CSV data file to run the dashboard.

---

## Requirements

Python version 3.8 or later is recommended.

Required packages:

* dash  
* plotly  
* pandas  
* numpy  

You can install them with:

```bash
pip install dash plotly pandas numpy
