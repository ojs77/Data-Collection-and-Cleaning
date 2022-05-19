# Unzipping relevant folders
def q1():
    import os
    # unzips specified folder
    def unzip(file_name, extract_path = ""):
        from zipfile import ZipFile
        # opening the zip file in READ mode
        with ZipFile(file_name, 'r') as zip:
        # printing all the contents of the zip file
            zip.printdir()
        # extracting all the files
            zip.extractall(extract_path)

    file_name = "kaggle-survey.zip"
    unzip(file_name)

    # Renaming folder
    new_folder = "Kaggle"
    old_folder = file_name.removesuffix(".zip")
    os.rename(old_folder, new_folder)

    # Unzipping subdirectories
    my_list = os.listdir(new_folder)
    for sub_file in my_list:
        file_name = f"{new_folder}/{sub_file}"
        unzip(file_name, new_folder)

    # Delete zipped folders
    for file in os.listdir(new_folder):
        if file.endswith(".zip"):
            os.remove(f"{new_folder}/{file}")

def q2():
    # finds similar questions across the 3 surveys and stores them in a text file which is acessed later, once to find the similar questions
    # This should automate a lot of the merging of similar questions
    def similar_questions():
        import pandas as pd

        # read in 3 surveys
        survey_2019 = pd.read_csv("Kaggle/multiple_choice_responses.csv")
        survey_2020 = pd.read_csv("Kaggle/kaggle_survey_2020_responses.csv")
        survey_2021 = pd.read_csv("Kaggle/kaggle_survey_2021_responses.csv")

        # Compiles list of questions in each and then combines to 1 big list
        questions_2019 = survey_2019.loc[0, :].values.tolist()
        questions_2020 = survey_2020.loc[0, :].values.tolist()
        questions_2021 = survey_2021.loc[0, :].values.tolist()
        questions_total= questions_2019 + questions_2020 + questions_2021

        # removes duplicate questions and sorts them, so that similar questions will mostly be next to each other in the list
        questions_total = list(dict.fromkeys(questions_total))
        questions_total.sort()

        
        # Function which conducts similarity check between strings, most similar questions have different final parts, so the similarity check is only on that final part
        # The function difflib.SequenceMatcher was imported to do this
        def similar(a, b):
            from difflib import SequenceMatcher
            a = a.split("-")
            b = b.split("-")
            return SequenceMatcher(None, a[-1], b[-1]).ratio()


        # Generate a list of similar questions
        # Format of each element in replacements list is [nth element, (n-1)th element]
        replacements = []
        previous_element = ""
        for current_element in questions_total:
            if similar(previous_element, current_element) > 0.5:
                replacements.append([current_element, previous_element])
            previous_element = current_element

        # Iterates through the potential similar questions and the user (me) manually decides whether each question is similar
        # This process of filtering the similar questions for the user to evaluate reduceded the number of manual decisions by about 80-90%
        for replacement in reversed(replacements):
            print(replacement[0])
            print(replacement[1])
            delete = input("Delete?")
            if delete == "y":
                replacements.remove(replacement)
            
        # Saves the replacement data to a txt file, so that it can be accessed later and the former steps don't need to be repeated
        with open("replacements.txt", "w") as f:
            for replacement in replacements:
                f.write(f"{replacement[0]}| {replacement[1]}")
                f.write("\n")
    
    # similar_questions()

    import pandas as pd

    # Import the 3 surveys and replace similar questions so that the question is identical in all 3
    survey_2019 = pd.read_csv("Kaggle/multiple_choice_responses.csv")
    survey_2020 = pd.read_csv("Kaggle/kaggle_survey_2020_responses.csv")
    survey_2021 = pd.read_csv("Kaggle/kaggle_survey_2021_responses.csv")

    # Import questions to replace
    with open("replacements.txt") as file:
        replacements = file.readlines()
        replacements = [line.rstrip() for line in replacements]

    # Replace relevant questions in each survey
    for replacement in replacements:
        replacement = replacement.split("|")
        new = replacement[0]
        old = replacement[1].lstrip()
        survey_2021 = survey_2021.replace([old], new)
        survey_2020 = survey_2020.replace([old], new)
        survey_2019 = survey_2019.replace([old], new)


    # The question number and their parts didn't match up in the different data sets as much as the actual questions did
    # Replaced column names with the questions, instead of question numbers, so that the 3 surveys can be merged easier
    survey_2019.columns = survey_2019.iloc[0]
    survey_2019 = survey_2019[1:]
    survey_2020.columns = survey_2020.iloc[0]
    survey_2020 = survey_2020[1:]
    survey_2021.columns = survey_2021.iloc[0]
    survey_2021 = survey_2021[1:]

    # Added a year of the answer column with the respective value
    survey_2021["year of the answer"] = 2021
    survey_2020["year of the answer"] = 2020
    survey_2019["year of the answer"] = 2019

    # Merged dataframes
    survey_2019_2021 = pd.concat([survey_2019, survey_2020, survey_2021])

    # Exported to csv file
    survey_2019_2021.to_csv("Kaggle_survey 2019-2021.csv", index = False)

# General clean of data, some cleaning is done later on as it is relevant to the analysis at that point, but not relevant for the other analysis 
def q3():
    import pandas as pd

    clean_survey = pd.read_csv("Kaggle_survey 2019-2021.csv")  

    # Remove rows that are wholly empty and any duplicates
    clean_survey = clean_survey.dropna(how="all")
    clean_survey = clean_survey.drop_duplicates()


    # Remove all columns that have "text" at the end of it, as it won't be useful for graphing 
    columns = clean_survey.columns
    drop_columns_index = []
    for index, column in enumerate(columns):
        column = column.split("-")
        if column[-1].strip() == "Text":
            drop_columns_index.append(index)

    clean_survey = clean_survey.drop(clean_survey.columns[drop_columns_index], axis = 1)


    # Exported to csv file
    clean_survey.to_csv("Kaggle_survey 2019-2021_cleaned.csv", index = False)


# Function used for evaluating number of unique elements in a column, which is used many times throughout the remaning analysis
def number_of_unique_elements(survey, col_name):

        # Converts pandas column to a numpy array
        column = survey[col_name].to_numpy()
        
        # Finds all unique values
        unique = []
        for element in column:
            if element not in unique:
                unique.append(element)
        
        # Initialises dictionary with keys as uniques and values as 0
        unique = dict.fromkeys(unique, 0)
        # Counts each instance of key
        for element in column:
            unique[element] += 1

        # Sorts the dictionary in ascending order
        unique = reversed(sorted(unique.items(), key=lambda x:x[1]))
        unique = dict(unique)

        # Returns the distribution of unique elements and the total elements
        return unique, len(column)

# Analysis of top programming languages and top data viz tools
def q4():
    import pandas as pd

    # Imports previously cleaned data
    survey = pd.read_csv("Kaggle_survey 2019-2021_cleaned.csv")


    # Task-based cleaning:
    # Removes blanks and reassigns some values so the set of answers for each year's survey is the same
    # Also changes some answers so there is no overlap of potential answers (5-10 and 10-20, there is an overlap of 10)
    survey = survey[survey["For how many years have you been writing code and/or programming?"].notna()]
    survey.loc[survey["For how many years have you been writing code and/or programming?"] == "I have never written code", "For how many years have you been writing code and/or programming?"] = "Never"
    survey.loc[survey["For how many years have you been writing code and/or programming?"] == "5-10 years", "For how many years have you been writing code and/or programming?"] = "6-10 years"
    survey.loc[survey["For how many years have you been writing code and/or programming?"] == "1-3 years", "For how many years have you been writing code and/or programming?"] = "1-2 years"
    survey.loc[survey["For how many years have you been writing code and/or programming?"] == "10-20 years", "For how many years have you been writing code and/or programming?"] = "11-20 years"

    # Only programmers with more than 5 years of exp:
    survey = survey.loc[survey["For how many years have you been writing code and/or programming?"] != "Never"]
    survey = survey.loc[survey["For how many years have you been writing code and/or programming?"] != "< 1 years"]
    survey = survey.loc[survey["For how many years have you been writing code and/or programming?"] != "1-2 years"]
    survey = survey.loc[survey["For how many years have you been writing code and/or programming?"] != "3-5 years"]

    # Returns dictionary for each year's survey with key:value = Language Name : No of respondents who selected the language for prog_lang_count 
    # and data viz tool : No of respondents who selected that tool
    def count_year_prog_lang(survey, year):
        survey_year = survey[survey["year of the answer"] == year]

        # Counts each langauge and assigns it to the relevant key in the dict
        prog_lang_count = {
            "Python": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Python"].count(),
            "R": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - R"].count(),
            "SQL": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - SQL"].count(),
            "C": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - C"].count(),
            "C++": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - C++"].count(),
            "Java": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Java"].count(),
            "Javascript" : survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Javascript"].count(),
            "Julia": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Julia"].count(),
            "Swift" : survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Swift"].count(),
            "Bash": survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Bash"].count(),
            "MATLAB" : survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - MATLAB"].count(),
            "Other" : survey_year["What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Other"].count()
        }

        # Sorts the dictionary in ascending order, so that filtering of top 5 languages can be done
        prog_lang_count = reversed(sorted(prog_lang_count.items(), key=lambda x:x[1]))
        prog_lang_count = dict(prog_lang_count)

        # Does the same for the data viz tools
        viz_count = {
            "Ggplot": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Ggplot / ggplot2 "].count(),
            "Matplotlib": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Matplotlib "].count(),
            "Altair": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Altair "].count(),
            "Shiny": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Shiny "].count(),
            "D3.js": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  D3.js "].count(),
            "Plotly": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Plotly / Plotly Express "].count(),
            "Bokeh" : survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Bokeh "].count(),
            "Seaborn": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Seaborn "].count(),
            "Geoplotlib" : survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Geoplotlib "].count(),
            "Leaflet / Folium": survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice -  Leaflet / Folium "].count(),
            "Other" : survey_year["What data visualization libraries or tools do you use on a regular basis?  (Select all that apply) - Selected Choice - Other"].count(),
            }

        viz_count = reversed(sorted(viz_count.items(), key=lambda x:x[1]))
        viz_count = dict(viz_count)

        # Returns each dictionary and the number of respondents for that year
        return prog_lang_count, viz_count, len(survey_year)
    
    # Returns all the dictionaries necessary for each year
    prog_lang_count_2019, viz_count_2019, respondents_2019 = count_year_prog_lang(survey, 2019)
    prog_lang_count_2020, viz_count_2020, respondents_2020 = count_year_prog_lang(survey, 2020)
    prog_lang_count_2021, viz_count_2021, respondents_2021 = count_year_prog_lang(survey, 2021)
    prog_lang_count_future, respondents_future = number_of_unique_elements(survey, "What programming language would you recommend an aspiring data scientist to learn first? - Selected Choice")

    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Defines the palette for each entry, so that the colours are consistant across all charts
    palette_prog = {"Python":"tab:blue",
           "R":"tab:orange", 
           "SQL":"tab:purple",
           "Javascript":"tab:red",
           "Java": "tab:green",
           "Bash": "tab:gray",
           "C":"tab:pink",
           "C++":"tab:olive",
           "Other":"tab:cyan",
           "Julia":"tab:brown",
           "MATLAB":"yellow",
           "Swift":"aquamarine",
           "None": "black",
           "TypeScript": "green"}

    palette_viz = {"Ggplot":"tab:blue",
           "Matplotlib":"tab:orange", 
           "Altair":"tab:purple",
           "Shiny":"tab:red",
           "D3.js": "tab:green",
           "Plotly": "tab:gray",
           "Bokeh":"tab:pink",
           "Seaborn":"tab:olive",
           "Geoplotlib":"tab:cyan",
           "Leaflet / Folium":"tab:brown",
           "Other":"yellow"}


    # Plotting programming languages:
    # 2021:
    plot_2021_prog = plt.figure(1)
    # X on bar chart is programming language names, y is the frequency of each, derived from dictionary
    x_1 = list(prog_lang_count_2021)
    y_1 = list(prog_lang_count_2021.values())
    # Only top 5 languages shown
    x_1, y_1 = x_1[:5], y_1[:5]
    bar_2021_prog = sns.barplot(x=x_1, y=y_1, palette=palette_prog)
    # Annotate percentage of respondents for that year on each bar
    for p in bar_2021_prog.patches:
        bar_2021_prog.annotate("{0:.0%}".format(p.get_height()/respondents_2021), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")

    # Label axes and caption
    bar_2021_prog.set(xlabel = "Programming Language", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 3: This shows the 5 most popular programming languages from the survey in 2021. The same questions were asked and data displayed as in Fig. 1", wrap=True, horizontalalignment='center', fontsize=12)


    # Same as above for 2020
    plot_2020_prog = plt.figure(2)
    x_2 = list(prog_lang_count_2020)
    y_2 = list(prog_lang_count_2020.values())

    x_2, y_2 = x_2[:5], y_2[:5]

    bar_2020_prog = sns.barplot(x=x_2, y=y_2, palette=palette_prog)
    for p in bar_2020_prog.patches:
        bar_2020_prog.annotate("{0:.0%}".format(p.get_height()/respondents_2020), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    bar_2020_prog.set(xlabel = "Programming Language", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 2: This shows the 5 most popular programming languages from the survey in 2020. The same questions were asked and data displayed as in Fig. 1.", wrap=True, horizontalalignment='center', fontsize=12)


    # Same as above for 2019
    plot_2019_prog = plt.figure(3)
    x_3 = list(prog_lang_count_2019)
    y_3 = list(prog_lang_count_2019.values())

    x_3, y_3 = x_3[:5], y_3[:5]

    bar_2019_prog = sns.barplot(x=x_3, y=y_3, palette=palette_prog)
    for p in bar_2019_prog.patches:
        bar_2019_prog.annotate("{0:.0%}".format(p.get_height()/respondents_2019), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    bar_2019_prog.set(xlabel = "Programming Language", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 1: This shows the 5 most popular programming languages from the survey in 2019. Each respondent selected as many programming languages that they used currently. The percentage of respondents who selected each option is displayed above each bar.", wrap=True, horizontalalignment='center', fontsize=12)
    
    
    # # future
    # plot_future_prog = plt.figure(4)
    # x_4 = list(prog_lang_count_future)
    # y_4 = list(prog_lang_count_future.values())
    # # Only top 5
    # x_4, y_4 = x_4[:5], y_4[:5]
    # # get values in the same order as keys, and parse percentage values
    # bar_future_prog = sns.barplot(x=x_4, y=y_4, palette=palette_prog)
    # bar_future_prog.set(xlabel = "Programming Language Future", ylabel= "Frequency")


    # Visualisation libraries plots:
    # Same as programming language previously
    plot_2021_viz = plt.figure(5)
    x_5 = list(viz_count_2021)
    y_5 = list(viz_count_2021.values())

    x_5, y_5 = x_5[:5], y_5[:5]

    bar_2021_viz = sns.barplot(x=x_5, y=y_5, palette=palette_viz)
    for p in bar_2021_viz.patches:
        bar_2021_viz.annotate("{0:.0%}".format(p.get_height()/respondents_2021), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    bar_2021_viz.set(xlabel = "Visualisation Libraries", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 6: This shows the 5 most popular data visualization libraries and tools from the survey in 2021. The same questions were asked and data displayed as in Fig. 4.", wrap=True, horizontalalignment='center', fontsize=12)


    # 2020
    plot_2020_viz = plt.figure(6)
    x_6 = list(viz_count_2020)
    y_6 = list(viz_count_2020.values())
    
    x_6, y_6 = x_6[:5], y_6[:5]
    
    bar_2020_viz = sns.barplot(x=x_6, y=y_6, palette=palette_viz)
    for p in bar_2020_viz.patches:
        bar_2020_viz.annotate("{0:.0%}".format(p.get_height()/respondents_2020), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    bar_2020_viz.set(xlabel = "Visualisation Libraries", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 5: This shows the 5 most popular data visualization libraries and tools from the survey in 2020. The same questions were asked and data displayed as in Fig. 4.", wrap=True, horizontalalignment='center', fontsize=12)
    

    # 2019
    plot_2019_viz = plt.figure(7)
    x_7 = list(viz_count_2019)
    y_7 = list(viz_count_2019.values())

    x_7, y_7 = x_7[:5], y_7[:5]

    bar_2019_viz = sns.barplot(x=x_7, y=y_7, palette=palette_viz)
    for p in bar_2019_viz.patches:
        bar_2019_viz.annotate("{0:.0%}".format(p.get_height()/respondents_2019), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    bar_2019_viz.set(xlabel = "Visualisation Libraries", ylabel= "Frequency")
    plt.figtext(0.5, 0.01, "Fig. 4: This shows the 5 most popular data visualization libraries and tools from the survey in 2019. Each respondent could select as many libraries and tools as possible and the percentage of respondents who answered a particular way are displayed above the bars.", wrap=True, horizontalalignment='center', fontsize=12)

    # Show all the figures
    plt.show()

# Analysis on compensation and the difference between men and women
def q5_comp_analysis():
    import numpy as np
    import pandas as pd

    # Imports previously cleaned data
    survey = pd.read_csv("Kaggle_survey 2019-2021_cleaned.csv")

    # Task-based cleaning:
    # Removing genders that are empty or prefer not to say then mapping man > male and woman > female
    survey = survey[survey["What is your gender? - Selected Choice"].notna()]
    survey = survey[survey["What is your gender? - Selected Choice"] != "Prefer not to say"]
    survey = survey[survey["What is your gender? - Selected Choice"] != "Prefer to self-describe"]

    survey.loc[survey["What is your gender? - Selected Choice"] == "Man", "What is your gender? - Selected Choice"] = "Male"
    survey.loc[survey["What is your gender? - Selected Choice"] == "Woman", "What is your gender? - Selected Choice"] = "Female"

    # Removes blanks and reassigns some values so the set of answers for each year's survey is the same
    survey = survey[survey["What is your current yearly compensation (approximate $USD)?"].notna()]
    survey.loc[survey["What is your current yearly compensation (approximate $USD)?"] == "300,000-500,000", "What is your current yearly compensation (approximate $USD)?"] = "300,000-499,999"
    survey.loc[survey["What is your current yearly compensation (approximate $USD)?"] == "> $500,000", "What is your current yearly compensation (approximate $USD)?"] = "500,000-999,999"
    survey.loc[survey["What is your current yearly compensation (approximate $USD)?"] == ">$1,000,000", "What is your current yearly compensation (approximate $USD)?"] = "999999"
    
    # Removes dollar sign and commas
    survey["What is your current yearly compensation (approximate $USD)?"] = survey["What is your current yearly compensation (approximate $USD)?"].str.replace("$","")
    survey["What is your current yearly compensation (approximate $USD)?"] = survey["What is your current yearly compensation (approximate $USD)?"].str.replace(",","")

    # Returns mean of upper and lower bound for each bin, this transforms the data to numerical data, which can then be binned in a histogram
    def return_average(string_start):
        string_1, string_2 = string_start.split("-")
        average = np.mean([int(string_1), int(string_2)])

        return average
    
    # Replaces bin with mean or if bin only has a lower/upper bound (>1000000), return itself without the bound (1000000)
    temp_column = []
    for row in survey["What is your current yearly compensation (approximate $USD)?"]:
        if "-" in row:
            temp_column.append(return_average(row))
        else:
            temp_column.append(int(row))
    survey["What is your current yearly compensation (approximate $USD)?"] = temp_column
    
    # data_comp = number_of_unique_elements(survey, "What is your current yearly compensation (approximate $USD)?")

    # Make and display graphs for the comp data
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Produces plot which simultaneously shows male and female split on comp via a histogram
    figure_2 = plt.figure(2)
    hist_plot_2 = sns.histplot(data = survey[survey["What is your gender? - Selected Choice"] == "Male"], x = "What is your current yearly compensation (approximate $USD)?", bins= 50, stat = "probability", color = "Blue")
    hist_plot_2.set(xlabel = "Yearly Compensation", ylabel= "Frequency Male")
    hist_plot_3 = sns.histplot(data = survey[survey["What is your gender? - Selected Choice"] == "Female"], x = "What is your current yearly compensation (approximate $USD)?", bins= 50, stat = "probability", color = "Red")
    hist_plot_3.set(xlabel = "Yearly Compensation ($ USD)", ylabel= "Proportion")
    plt.figtext(0.5, 0.01, "Fig. 7: The histogram above shows the distribution of males (Blue) and females (Red), where the height of each bar is the proportion of each group in that bar's bin range. The orange parts of the histogram indicate bins where the females' proportion is that large, and as such the line between red and orange is the height of the males' bar.", wrap=True, horizontalalignment='center', fontsize=12)

    # Generate stats for previous plot:
    print("Males comp stats:", survey[survey["What is your gender? - Selected Choice"] == "Male"]["What is your current yearly compensation (approximate $USD)?"].describe())
    print("Females comp stats:", survey[survey["What is your gender? - Selected Choice"] == "Female"]["What is your current yearly compensation (approximate $USD)?"].describe())

    # As above but filters on high earners, to produce another graph which further shows split on comp
    figure_high_earners = plt.figure(3)
    survey_high_earners = survey[survey["What is your current yearly compensation (approximate $USD)?"] > 100000]
    hist_plot_5 = sns.histplot(data = survey_high_earners[survey_high_earners["What is your gender? - Selected Choice"] == "Male"], x = "What is your current yearly compensation (approximate $USD)?", bins= [100000,200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000], stat = "probability", color = "Blue")
    hist_plot_5.set(xlabel = "Yearly Compensation of High Earners ($ USD)", ylabel= "Proportion")
    hist_plot_4 = sns.histplot(data = survey_high_earners[survey_high_earners["What is your gender? - Selected Choice"] == "Female"], x = "What is your current yearly compensation (approximate $USD)?", bins= [100000,200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000], stat = "probability", color = "Red")
    hist_plot_4.set(xlabel = "Yearly Compensation of High Earners ($ USD)", ylabel= "Proportion")
    print("Males comp high stats:", survey_high_earners[survey_high_earners["What is your gender? - Selected Choice"] == "Male"]["What is your current yearly compensation (approximate $USD)?"].describe())
    print("Females comp high stats:", survey_high_earners[survey_high_earners["What is your gender? - Selected Choice"] == "Female"]["What is your current yearly compensation (approximate $USD)?"].describe())
    plt.xlim(100000, 1000000)
    plt.figtext(0.5, 0.01, "Fig. 8: The histogram above shows the distribution of high earners, which is defined as those earning more than $100,000. The height of each bar is the proportion of high earners in each group in that bar's bin range.", wrap=True, horizontalalignment='center', fontsize=12)

    # As above but filters on low earners
    figure_low_earners = plt.figure(4)
    survey_low_earners = survey[survey["What is your current yearly compensation (approximate $USD)?"] <= 100000]
    hist_plot_7 = sns.histplot(data = survey_low_earners[survey_low_earners["What is your gender? - Selected Choice"] == "Male"], x = "What is your current yearly compensation (approximate $USD)?", bins= 10, stat = "probability", color = "Blue")
    hist_plot_7.set(xlabel = "Yearly Compensation of Low Earners ($ USD)", ylabel= "Proportion")
    hist_plot_6 = sns.histplot(data = survey_low_earners[survey_low_earners["What is your gender? - Selected Choice"] == "Female"], x = "What is your current yearly compensation (approximate $USD)?", bins= 10, stat = "probability", color = "Red")
    hist_plot_6.set(xlabel = "Yearly Compensation of Low Earners ($ USD)", ylabel= "Proportion")
    print("Males comp low stats:", survey_low_earners[survey_low_earners["What is your gender? - Selected Choice"] == "Male"]["What is your current yearly compensation (approximate $USD)?"].describe())
    print("Females comp low stats:", survey_low_earners[survey_low_earners["What is your gender? - Selected Choice"] == "Female"]["What is your current yearly compensation (approximate $USD)?"].describe())
    plt.figtext(0.5, 0.01, "Fig. 9: The histogram above shows the distribution of low earners, which is defined as those earning less than or equal to $100,000. The height of each bar is the proportion of low earners in each group in that bar's bin range.", wrap=True, horizontalalignment='center', fontsize=12)

    # Shows plots
    plt.show()


# q5_comp_analysis()

# Analysis on the highest level of education achieved and the difference between men and women
def q5_education_analysis():
    import pandas as pd

    # Imports previously cleaned data
    survey = pd.read_csv("Kaggle_survey 2019-2021_cleaned.csv")

    # Removes rows with empty values in relevant column(s)
    survey = survey[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"].notna()]
    survey = survey[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] != "I prefer not to answer"]

    # Changes some entries to remove outliers and reduce the number of potential outcomes, to simplify the graphs produced
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "Bachelorâ€™s degree", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "Bachelor's degree"
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "Masterâ€™s degree", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "Master's degree"
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "Some college/university study without earning a bachelorâ€™s degree", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "High School"
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "Some college/university study without earning a bachelor’s degree", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "High School"
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "No formal education past high school", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "High School"
    survey.loc[survey["What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] == "Professional doctorate", "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?"] = "Doctoral degree"
    

    import seaborn as sns
    import matplotlib.pyplot as plt

    # Order for the graphs produced, in ascending order of path 
    education_order = ["High School", "Bachelor’s degree", "Master’s degree", "Professional degree", "Doctoral degree"]

    # Since the number of male and female respondents was different, the graphs show % of each gender, as it is more informative
    # Returns dictionary with the key : value = type of degree : percentage of respondents
    def replace_with_percentage(survey):
        item_counts, total = number_of_unique_elements(survey, "What is the highest level of formal education that you have attained or plan to attain within the next 2 years?")
        item_percentages = {}
        for key in item_counts.keys():
            item_percentages[key] = item_counts[key]/total
        
        return item_percentages
    
    survey_female = survey[survey["What is your gender? - Selected Choice"] == "Female"]
    female_percentages = replace_with_percentage(survey_female)
    survey_male = survey[survey["What is your gender? - Selected Choice"] == "Male"]
    male_percentages = replace_with_percentage(survey_male)
            
    # Generates bar chart for females, of percentage of respondents against type of degree
    plot_1 = plt.figure(5)
    x_female_percentage = list(female_percentages)
    y_female_percentage = list(female_percentages.values())
    female_percentage_plot = sns.barplot(x=x_female_percentage, y=y_female_percentage, order = education_order)
    # Adds percentage to each bar for clarity
    for p in female_percentage_plot.patches:
        female_percentage_plot.annotate("{0:.0%}".format(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    female_percentage_plot.set(xlabel = "Highest level of education achieved", ylabel= "Proportion")
    plt.figtext(0.5, 0.01, "Fig. 11: The bar chart shows the percentage of females who's highest level of education is above.", wrap=True, horizontalalignment='center', fontsize=12)

    # Gen bar chart for males of the same format
    plot_2 = plt.figure(6)
    x_male_percentage = list(male_percentages)
    y_male_percentage = list(male_percentages.values())
    male_percentage_plot = sns.barplot(x=x_male_percentage, y=y_male_percentage, order = education_order)
    # Adds percentage to each bar for clarity
    for p in male_percentage_plot.patches:
        male_percentage_plot.annotate("{0:.0%}".format(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()), ha= "center", va = "bottom")
    male_percentage_plot.set(xlabel = "Highest level of education achieved", ylabel= "Proportion")
    plt.figtext(0.5, 0.01, "Fig. 10: The bar chart shows the percentage of males who's highest level of education is above. They are ordered from lowest to highest, apart from the professional and doctoral degree bars, which are comparable to each other.", wrap=True, horizontalalignment='center', fontsize=12)

    # Shows plots
    plt.show()

q5_education_analysis()
