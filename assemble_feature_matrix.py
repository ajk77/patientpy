"""
assemble_feature_matrix.py
version 3.0
package github.com/ajk77/PatientPy
Created by AndrewJKing.com|@andrewsjourney

This file assembles the features into a feature matrix based on the input parameters. 
Input parameters include:
feature directory -> as populated by create_feauture_vectors.py
output filename -> where the resulting feature vector should be saved; feature_names will be output to a file of the same name but with _names appended to it. 
Features types to include -> list of the feature types to include (must be in the form created by create_feature_vectors.py) [1]
Additional feature files -> additional features to include, i.e. ones not generated by create_feature_vectors. [2]
Feature columns to match -> if tying to match the feature columns of a previously assembled feature matrix

[Notes]
[1] for each feature type NAME -> a folder NAME_feature_files and a file NAME_feature_columns where the rows in the file correspond to the columns in each of the feature files. Look at example in resources
[2] for each additional feature NAME -> a feature file called NAME_features and a file called NAME_feature_columns. The same correspondence as Note 1. 

---DEPENDENCIES---
Must run create_feature_vectors first.
Feature directory should be the same as used in create_feature_vectors output.
Must create additional feature files separately and add them to the feature directory if any additional feature files are desired. 

---LICENSE---
This file is part of PatientPy

PatientPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or 
any later version.

PatientPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PatientPy.  If not, see <https://www.gnu.org/licenses/>.
"""

from patientpy_utils import load_list, load_file_list
import numpy as np

def assemble_feature_matrix(feature_directory, output_filename, feature_types_to_include=['demo', 'io', 'med', 'micro', 'procedure', 'root'], additional_features=[], feature_columns_to_match=[]):
    """
    Assemble feature matrix for the different experiments
    """
    def concat(c_idx, f_data, f_names, l_data, l_names):
        """
        Concatenates loaded data and loaded names to full data and full names. 
        """
        # ## append current type data and names to full data and names
        if c_idx == 0:  # first type
            f_data = l_data
            f_names = l_names
        elif l_data.ndim == 2:  # test for single column feature types
            f_data = np.concatenate((f_data, l_data), axis=1)
            f_names = np.concatenate((f_names, l_names), axis=0)
        else:  # test for multiple column feature types
            f_data = np.concatenate((f_data, l_data), axis=0)
            f_names = np.concatenate((f_names, l_names), axis=0)
        return [f_data, f_names]

    def load_dir(files_dir, var_name_file):
        """
        Loads comma separated file into numpy array and returns all columns except those containing all null
        """
        file_list = load_file_list(files_dir)  # root_feature_files
        var_names = load_list(var_name_file)
        all_data = None
        all_names = None
        for idx2, filename in enumerate(file_list):
            curr_data = np.genfromtxt(files_dir + filename, delimiter=',', missing_values='')
            curr_names = np.asarray([x + '_' + filename[:-4] for x in var_names], dtype='U')
            all_data, all_names = concat(idx2, all_data, all_names, curr_data, curr_names)
        return [all_data, all_names]

    # ## creating the feature matrix and column names
    full_data = 0
    full_names = 0
    for idx, curr_type in enumerate(feature_types_to_include):
        print('======' + curr_type + '======')

        # ## load current type feature name files
        training_file_dir = feature_directory + curr_type + '_feature_files/'
        training_var_names_file = feature_directory + curr_type + '_feature_columns.txt'

        # ## load current type data
        loaded_data, loaded_names = load_dir(training_file_dir, training_var_names_file)
        print('loaded: ', loaded_data.shape, loaded_names.shape)

        # concatenate loaded data to full data
        full_data, full_names = concat(idx, full_data, full_names, loaded_data, loaded_names)

        # print shape after addition of current type
        print('concatenated: ', full_data.shape, full_names.shape)


    # ## additing additional types of features
    if len(additional_features):
        for idx, curr_file in enumerate(additional_features):
            print('------' + curr_file + '------')
            var_names = load_list(feature_directory + curr_file + '_columns.txt')
            curr_data = np.genfromtxt(feature_directory + curr_file + '.txt', delimiter=',', missing_values='')
            curr_data = curr_data.reshape(curr_data.shape[0], 1)
            curr_names = np.asarray([x + '_' + curr_file for x in var_names], dtype='U')
            print(curr_data.shape, curr_names.shape)
            full_data, full_names = concat(idx+1, full_data, full_names, curr_data, curr_names)
            print('concatenated: ', full_data.shape, full_names.shape)
        print('additional featueres added: ', full_data.shape, full_names.shape)

    # ## if insureing the feature columns are the same as an existing feature matix
    if len(feature_columns_to_match):
        new_indicies = []
        for idx, curr_feature_name in enumerate(feature_columns_to_match):
            column_index_result = np.where(full_names==curr_feature_name)
            if column_index_result[1].size:
                new_indicies.append(column_index_result[1][0])
        full_data = full_data[:, column_index_result]
        full_names = full_names[:, column_index_result]
        print('columns are matched: ', full_data.shape, full_names.shape)

    # print shape after num training columns are removed
    print('full: ', full_data.shape, full_names.shape)

    # ## reshape name dimensions
    full_names = full_names.reshape((full_names.shape[0], 1))

    # save data and names files
    np.save(output_filename, full_data)
    np.save(output_filename + '_names', full_names)

    return


if __name__ =='__main__':

    # where the data was stored from create_feature_vectors.py
    feature_dir = '//modeling_folder/complete_feature_files_demo/'
    output_filename = '//modeling_folder/feature_matrix_storage/full_demo'
    add_feat = []  # use to add any other feature types. Files must be placed in feature_dir

    feat_types = ['demo', 'io', 'med', 'micro', 'procedure', 'root']

    column_match = []  # 

    assemble_feature_matrix(feature_dir, output_filename, feature_types_to_include=feat_types, additional_features=add_feat)
