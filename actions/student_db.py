# import pandas as pd
# pd.options.mode.chained_assignment = None
# student_data = pd.read_excel('./student_db_new.xlsx')
# student_data = student_data.loc[:, ~
#                                 student_data.columns.str.contains('^Unnamed')]
# xx = student_data.copy()
# user_id = '1082171472'
# subject = 'Business'

# subjects = []
# values = []

# for index, row in student_data.iterrows():
#     if str(row['User']) == str(user_id):
#         print('==========PLOT EQUALS==========')
#         largest_values = row.to_dict()
#         largest_values.pop('User')
#         # largest_values_dict = largest_values.to_dict()

#         print('==========PLOT EQUALS==========')

# for subject, score in largest_values_dict.items():
#     subjects.append(subject)
#     values.append(int(score))

# print(subjects, values)
# for i, row in student_data.iterrows():
#     if str(row['User']) == str(user_id):
#         # row[subject] += 1
#         # print(row[subject])
#         # xx.loc[xx['User'] == user_id, subject] += 1
#         student_data.loc[student_data['User'] == user_id, subject] += 1
#         break

# print(student_data)
# print(xx)

# student_data = pd.DataFrame(columns=['User', 'Art and Design',	'Biology',	'Business',	'Chemistry',
#                                      'History',	'Humanities',	'Language',	'Math',	'Physics',	'Psychology',	'Technology', 'Other'])
# # # student_data.set_index('User', inplace=True)
# if user_id not in student_data.values:
#     student_data = pd.concat(
#         [student_data, pd.DataFrame({'User': [user_id]})], ignore_index=True)
#     student_data.fillna(0, inplace=True)
#     # student_data.set_index('User', inplace=True)
#     # student_data.to_excel('actions/student_db_new.xlsx')
# student_data.to_excel('student_db_new.xlsx')

# # for _ in range(2):
# #     user_name = input(str('Enter user name: '))
# #     if user_name not in data.values:
# #         print('---------------------------------------')
# #         data = pd.concat(
# #             [data, pd.DataFrame({'User': [user_name]})], ignore_index=True)
# #         data.fillna(0, inplace=True)

# # data.fillna(0, inplace=True)
# # data.set_index('User', inplace=True)
# # student_data = pd.read_excel('./student_db_new.xlsx')
# # student_data = student_data.loc[:, ~
# #                                 student_data.columns.str.contains('^Unnamed')]
# # xx = student_data[student_data['User'].astype(str).str.contains('1082171472')]
# # print(xx)
# # data.loc['xyz']['Biology'] += 5
# # data.loc['xyz']['Humanities'] += 2

# subject = 'Business'
# # user_id = '1082171472'
# # user_id = 1082171472

# time.sleep(2)

# xdata = pd.read_excel('./student_db_new.xlsx')  # , index_col='User')
# xdata = xdata.loc[:, ~xdata.columns.str.contains('^Unnamed')]

# for row in xdata.iterrows():
#     if row[1]['User'] == int(user_id):
#         print(row[1]['User'])
#         row[1]['Math'] += 1
#         print(row[1]['Math'])

# print(xdata)

# subjects = []
# values = []

# for row in xdata.iterrows():
#     if row[1]['User'] == int(user_id):
#         largest_values = row[1].nlargest(n=6)
#         largest_values_dict = largest_values.to_dict()
#         largest_values_dict.pop('User')

#         print(largest_values_dict)

#         for subject, score in largest_values_dict.items():
#             subjects.append(subject)
#             values.append(int(score))

# print(subjects, values)
# # largest_values = xdata.loc[int(user_id)].nlargest(n=5)
# # largest_values_dict = largest_values.to_dict()

# # for subject, score in largest_values_dict.items():
# #     subjects.append(subject)
# #     values.append(int(score))
