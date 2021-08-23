# Group 34 ECE356-Project
By Ian Steneker, Abdulmateen Shaikh, Hariharan Karthikeyan
## Prerequisites
In order to set up the database and run the client, all that is required is python3 and the libraries listed in requirements.txt. These can be installed using `pip install -r requirements.txt`, but we recommend creating a virtual environment first to reduce problems from conflicting libraries, especially the many mysql connectors.
If you want to run an instance of MySQL locally, run `docker-compose up`.
## Database setup
All of the following takes place in the `database` folder.

Unzip `target_tables.zip`, or download the [CORD-19](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge) dataset and extract the `target_tables` folder to the `database` folder. Then run `python preprocessing.py` and ensure an `output` folder is created. Move this output folder to `/var/lib/mysql-files`, or modify the paths in `createCOVID_19.sql`. Once the files are in an appropriate position, open a mysql client and run `createCOVID_19.sql` to load the preprocessed tables and create the database. The dataset is quite small so this should not take very long.

## Client Setup & Usage
Modify `databaseDetails.yml` to contain the appropriate credentials and connection information for your desired MySQL instance. If you are running MySQL locally, update the host details in `databaseDetails.yml` to be "localhost".

Once this is correct, launch the client by running `python app`. If everything goes well you will be dropped at the main menu. If there are any authorization or connectivity issues, an error message will display and the program will exit.

Once at the client main menu, please feel free to use the help menu to determine how to add/remove studies, results, and more.

## Datamining
Datamining was done externall using the [Orange data mining tool](https://orangedatamining.com). Instructions to set this tool up can be found [here](https://github.com/biolab/orange3). The `datamining` folder is already set up such that the Orange data mining tool can be used to open `riskFactorResultsMining.ows` and view the various results for fatality and severity of each risk factor, but screenshots of these results are also contained within the `datamining` folder. The CSVs in output_csvs are direct exports of the FatalityResults and SeverityResults table of the MySQL instance, but can be re-exported using a tool of your choice.

## Report and video
The report and associated video can be found in the `deliverables` folder.