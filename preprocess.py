import pandas as pd

columns = ['Job Id', 'Experience', 'Qualifications', 'Salary Range','Country','Work Type','Company Size','Job Posting Date','Job Title','Benefits','skills','Company']
df = pd.read_csv('./Dataset/job_descriptions.csv', usecols = columns)
df_usa = df[df["Country"]=="USA"]
df_usa = df_usa.drop(columns=['Country'])

df_usa[['Min salary', 'Max Salary']] = df_usa['Salary Range'].str.replace('[$K]', '', regex=True).str.split('-', expand=True)
df_usa['Min salary'] = pd.to_numeric(df_usa['Min salary'])
df_usa['Max Salary'] = pd.to_numeric(df_usa['Max Salary'])
df_usa = df_usa.drop(columns=['Salary Range'])

df_usa[['Min Experience', 'Max Experience']] = df_usa['Experience'].str.replace(' Years', '', regex=False).str.split(' to ', expand=True)
df_usa['Min Experience'] = pd.to_numeric(df_usa['Min Experience'])
df_usa['Max Experience'] = pd.to_numeric(df_usa['Max Experience'])

df_usa['Company Size'] = pd.to_numeric(df_usa['Company Size'])
df_usa['Job Posting Date'] = pd.to_datetime(df_usa['Job Posting Date'])
df_usa = df_usa.drop(columns=['Experience'])
df_usa.to_csv('./Dataset/usa_jobs.csv', index = False)
