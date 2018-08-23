import csv
import argparse
import os


class ReportSplitter:
    def __init__(self, values, columns, file, output_folder=None, verbose=False):
        self.values = self._values_to_lowecase(values)
        self.columns = columns
        self.file = file
        self.output_folder = output_folder
        self.file_mapping = {}
        self.opened_files = []
        self.verbose = verbose

        if self.output_folder is None:
            self.output_folder = os.getcwd()


    def split(self):

        if self.verbose:
            print("Values used for indexing:")
            print(self.values)
            print("Columns that will be indexed:")
            print(self.columns)
            print("File that will be splitted: " + self.file)
            print("Output folder: " + self.output_folder)
            print("Starting...")
        try:
            self.file_exists(self.file)
            self.folder_exists(self.output_folder)

            with open(self.file) as csvfile:
                reader = csv.DictReader(csvfile)
                self._verify_column_names(reader.fieldnames)
                self.create_files(reader.fieldnames)
                # Reading row by row
                for row in reader:
                    # For each row checking columns that contain indexed data
                    for column in self.columns:
                        # If indexed value in the column, writing this line to appropriate file
                        if row[column].lower() in self.values:
                            self.write_line_to_file(row[column].lower(), row)

            self._close_files()
        except Exception as err:
            print(err)
            return
        if self.verbose:
            print("Finished...")
            print("Following files were created:")
            for file in self.opened_files:
                print(file.name)

    def write_line_to_file(self, value, row):
        self.file_mapping[value].writerow(row)

    def folder_exists(self, folder):
        if not os.path.exists(folder):
            raise Exception("ERROR - folder " + folder + " doesn't exist!")
        if not os.path.isdir(folder):
            raise Exception("ERROR - " + folder + " is not a folder!")
        if not os.access(folder, os.W_OK):
            raise Exception("ERROR - folder " + folder + " is not writable!")

    def file_exists(self, file):
        if not os.path.exists(file):
            raise Exception("ERROR - file " + file + " doesn't exist!")
        if not os.path.isfile(file):
            raise Exception("ERROR - " + file + " is not a file!")
        if not os.access(file, os.R_OK):
            raise Exception("ERROR - file " + file + " is not readable!")

    def _verify_column_names(self, fieldnames):
        for column in self.columns:
            if column not in fieldnames:
                raise ("ERROR - Column " + column + " not found to be a in the CSV file. Maybe case sensitivity issue?")

    def create_files(self, fieldnames):

        try:
            for value in self.values:
                file_name = os.path.join(self.output_folder, value.replace(".", "_") + ".csv")
                csvfile = open(file_name, 'w')
                writer = csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()
                self.file_mapping[value] = writer
                self.opened_files.append(csvfile)
        except Exception as err:
            raise err

    def _values_to_lowecase(self, list):
        new_list = []
        for value in list:
            new_list.append(value.lower())
        return new_list

    def _close_files(self):
        for file in self.opened_files:
            file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--value_list", help="List of values based on which should the report be splitted. " +
                                                   "Accepts list of comma separated values")
    parser.add_argument("-c", "--column_list", help="List of columns that will be searched for indexing." +
                                                    "Accepts list of comma separated values")
    parser.add_argument("file", help="File that should be splitted")
    parser.add_argument("-o", "--output_folder", help="Folder where the output should be placed")
    parser.add_argument("-p", "--verbose", help="Verbose mode", action='store_true')
    args = parser.parse_args()

    report_splitter = ReportSplitter(args.value_list.split(","), args.column_list.split(","), args.file,
                                     args.output_folder, args.verbose)
    report_splitter.split()
