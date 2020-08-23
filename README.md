# FinlandKuntaHarmon
Project to harmonize Finnish kunta (municipality) borders and population statistics across time.
If you use the data or the scripts in this repository for your research, please cite:

Jonas Mueller-Gastell, 2020, "Finnish Municipalities 1880 to 1974: Creating Harmonized Statistical Units Over a Century"

If you find any mistakes in the code or the underlying data, or would like to contribute to digitizing or auditing the data, please contact me at jonasmg[at]stanford.edu

## Project Architecture
	|_ Module
		|_ code_linker.py
		|_ haromizer.py
	|_ Data
		|_AllMoves.csv
		|_kuntacodes_utf8.csv
		|_Population1880_1974.csv
		|_Helper
			|_ ...
		|_TransitionFiles
			|_ ...
		|_ TransitionLong
			|_ ...
	|_ FromScratch
		|__ ...

## Module
All scripts and programs live here   

### code_linker.py
This file provides a utility to match kunta names with the modern kunta-koodi system employed by Statistics Finland. 

	findCodes(df, names, province=False, urban=False,  yearvar = False, 
	          verbose=False, suggestFixes = False, 
		  path = '[your path]FinlandKuntaHarmon/Data/')
				  
		df: the pre-loaded pandas data-frame in which you would like to link names, needs to contain a column with kunta-names
		names: string with the name of the column which contains the names, OR a list with strings with (in this order) the names of name-column, province-column, urban-column (province and urban indicator help the program deal with ambiguous names), OR a dictionary with 'name', 'province', 'urban' fields
		province: bool, should province names be used to help?
		urban: bool, should urban/rural indicator be used to help?
		yearvar: bool, string, or integer; should the program attempt to check the matched list of names agains the population data file for the given year to identify kuntas who did not exist (in the population tables) in the given year? If so, include either the column name that contains the year or the year to be checked as an integer
		suggestFixes: bool, should the program make suggestions for what re-namings should occur to get non-anachronistic matches? 
		path: string, path to the data necessary to run the module
	output: data-frame with an additional column 'code' containing kunta-coodi, or this data-frame and a dictionary of suggestions (see above)

### harmonizer.py
This file provides utilities to translate a given data-frame from the kunta-boundaries of year A to the kunta-boundaries of year B (A>B). The assumption maintained is that the variable of interest (an abslute value or a per-population rate or a categorical membership) is uniformly distributed within the population of the kunta. Then, the utilities trace all (recorded) population transfers, kunta splits, merges, and foundations. By maintaining this assumption of uniformity and hence by using population weights, we  create a best guess of what the data-frame would have looked like if the historical data was collected under the boundaries of the more recent kunta coding system. 

	harmonize(...) harmonize a data frame with absolute or relative statistics from one year to another
		harmonize(df, year1, year2, absCols = [], relCols = [], idCol = False, f= '[your path]/FinlandKuntaHarmon/')
		df: the pre-loaded pandas data-frame with a kunta-koodi id column and at least one data column to translate
		year1: int or string, the year on which the data-frame's kunta boundaries are based
		year2: int or string, the year to which you would like to translate the kunta boundaries
		absCols: string or list, the name(s) of the columns with abslute value (e.g., number of tractors) to translate
		relCols: string or list, the name(s) of the columns with relative values (e.g., casualty rate) to translate
		idCol: string, name of the kunta-koodi containing identifier column, if False assume idCol is one of ['code', 'id', 'kunta', 'grouper']
		f: string, path to where the kunta harmonization module lives
	output: data frame with harmonized columns and an identifier columns (kunta-koodi)

	categoricalHarmonize(...) harmonizes categorical variables (e.g., membership in a province) from one year to another
		categoricalHarmonize(df, year1, year2, whichCol, idCol = False, f= '[your path]/FinlandKuntaHarmon/')
		df: the pre-loaded pandas data-frame with a kunta-koodi id column and at least one data column to translate
		year1: int or string, the year on which the data-frame's kunta boundaries are based
		year2: int or string, the year to which you would like to translate the kunta boundaries
		whichCol: string or list, the name(s) of the columns with categorical variables to translate
		idCol: string, name of the kunta-koodi containing identifier column, if False assume idCol is one of ['code', 'id', 'kunta', 'grouper']
		f: string, path to where the kunta harmonization module lives
	output: data frame with harmonized columns and an identifier columns (kunta-koodi). Note that categorical variables are translated into one column per level, with values continuously between 0 and 1, allowing the user to determine thresholds at which to assign 0 or 1 themselves
	
	
## Data
All data used by the scripts and all additional data provided for convenience and general use are collected here. 

	|_AllMoves.csv
	A list of all recorded redrawings of statistical kunta boundaries from 1880 to 1975.  
		Year: year of transfer/move/split
		NameSource: municipality from which people were moved/split off
		NameTarget: municipality to which people were sent/split off into
		codeSource: kunta-koodi of source
		codeTarget: kunta-koodi of target/destination
		TotalDist: number of people involved in the transfer
		PopSource: total population of source municipality as reference
		

	|_kuntacodes_utf8.csv
	kunta-koodi matched to names and some kunta information variables
		code: kunta-koodi in current style
		code50: kunta-koodi in style used in 1950 population census (zeroth digit is status in 1950, first digit is province, second and third digit are town type, last three are kunta code within province and town style)
		Name_Fi: primarily used name in Finnish
		Name_Sv: primarily used name in Swedish, if different
		Name_AltGen: alternative name, usually a non-declinated variant of gentiive (e.g., Haaga kla instead of Haagan kla)
		Name_Alt: alternatve name, e.g., when municipalities are renamed or have a common alternative spelling
		province_Fi: name of province in 1950 in Finnish
		province_Sv: name of province in 1950 in Swedish
		Status: categorical for status in 1950 relative to the Post-WW2 border: 'remain': no change, 'temporarily_ceded': military lease, 'Cartially_Ceded': municipality which lost some land in peace treaty, 'Viipuri_Ceded': municipality in Viipruin laani which was lost, 'Petsamo_Ceded': Petsamo kunta (which was lost), 'North_Partiall_Ceded': kuntas in the North of Finland that lost territory, 'Island_Ceded': islands in the gulf of Finland that were lost
		Urban: indicator whether the kunta is in kunta or maalaiskunta part of 1950 table
		grouperMLK: kunta-koodi, but assigning MLKs the same code as their KLA
		grouperAll: kunta-koodi, but heuristically merging kunta's that saw significant population transfers, MLKs with KLAs, and Helsinki capital region
	
	|_Population1880_1974.csv
	A time series of relevant demographic variables for all kuntas in Finland 1880 to 1974. 
	All data processing and harmonization steps are detailed in the paper: \\\\ 
	The original digitization of data pre 1914 does not include detailed immigration numbers, data processing or data post 1938 has not yet been completed and thus only total population is given here, not births, deaths, nor immigration numbers. 
	Data before 1930s is aggregated up from Parishes, rather than directly taken from kunta boundaries, which means accuracy before 1930 is likely lower, in particular for population totals.

		kunta: kunta name
		code: kunta-koodi
		year: year of observation
		PopInterpol: interpolated population number (see paper) pre 1940, recorded population number post 1940
		birthsM, birthsW, birthsTot: births men, women, total
		deathsM, deathsW, deathsTot: deaths men, women, total
		inmigM,	inmigW,	inmigTot: in-migration  men, women, total (not always digitized, then 0)
		outmigM	outmigW	outmigTot: out-migration  men, women, total (not always digitized, then 0)
		netchgM	netchgW	netchgTot: total change across births, deaths, in- and out-migration  men, women, total (when immigration is not recorded, this number does NOT add up to births and deaths -- it also contains the net of the two, due to how the original data was digitized from the paper documents)
		

'TransitionFiles' contains the Excel files in which the raw transition dictionaries are stored, 
'TransitionLong' contains the long-form csv's that could be read and used in Stata, for example, to perform manual harmonizations. 
	
	|_TransitionFiles
		|_ {Year1}{Year2}Transition.xlsx
			id: id of kunta in year 2
			Abs: dictionary with pairs (id of a source kunta in year1) and (% of the source kunta population year1 present in id target kunta in year2)
			Rel: dictionary with pairs (id of a source kunta in year1) and (% of the target kunta population in year2 that originates from source kunta)
		|_ ...
	|_TransitionLong
		|_LongVersion{year1}{year2}.csv
			idTarget: id of kunta in year2
			idSource: if od kunta in year1 that 'sends' population to kunta target
			ValueAbs: % of source kunta in year1 present in target kunta in year2
			ValueRel: % of target kunta population in year1 that stems from source kunta
The LongVersion{year1}{year2}.csv files can also be used to harmonize population without the use of the harmonizer.py file. E.g., in Stata, read the file (import delimited ... ), and then merge (merge m:1) with your data file that you would like to harmonize, on idTarget, then perform a (series of) egen command(s) to sum-multiply your source data with the ValueAbs or ValueRel columns to obtain your final data (after dropping duplicate rows)


'Helper' contains utility files (.csv and .pickle) that are used by the scripts to minimize computation time

## FromScratch
This folder contains code routines that produce the translation files and helper files for a given set of population totals and moves information. 

## Acknowledgements
This project is a collaborative project with a humongous number of dedicated academic contributors. I could not have created the scripts and routines here without the generous contributions of data, time, and money of all of my collaborators and research assistants. All errors remain my own.

Sakari Saaritsa, who funded and oversaw the digitization of the original Census and Parish files from 1880 to 1938, in collaboration with

Jarmo Peltola, for the urban population data from 1880 to 1938, see https://doi.org/10.1080/1081602X.2019.1598462, with

Eero Simanainen, who undertook the digitization of the 1914 to 1938 parish data and did the heroic initial aggregation work of these parishes into kunta borders.

Matti Sarvimäki, who funded the digitization of the original Census tables from 1938 to 1974 and the municipality changes files from 1880 to 1974, see this paper http://www.aalto-econ.fi/sarvimaki/forced.pdf , jointly with 

Maarit Olkkola, who funded, managed, and oversaw the digitization of the original Census tables from 1938 to 1969,

Elina Laakso, who undertook the digitization of the population transfers and 1970-1974 original tables.


Funding for this project comes from a variety of sources. I am particularly grateful for the financial support by the Shultz Foundation at SIEPR, the Economic History Association, and the GRO Fund at Stanford. I also want to thank Aalto Department of Economics for their administrative support and generous hospitality.
	
	
