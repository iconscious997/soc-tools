import argparse
import os
import csv
import datetime

class ReportMerger:

    def __init__(self, files=None, verbose=False, name_sorting=True, time_sorting=False, output_file='merged.csv',
                 time_verify=None, time_format=""):
        self.verbose = verbose
        self.files = files
        self.name_sorting = name_sorting
        self.time_sorting = time_sorting
        self.output_file = output_file
        self.time_verify = time_verify
        self.time_format = time_format

    def merge(self):

        if self.verbose:
            print("Starting report merger...")
            print("Name sorting: " + str(self.name_sorting))
            print("Time sorting: " + str(self.time_sorting))
            print("Output file: " + self.output_file)
            print("Files:")
            print(self.files)

        try:
            self._verify_settings()
            self._sort_files()
            self.output_file = self._create_output_file()

            if self.time_sorting is not None:
                print("k")
                self.time_merge()
                print("l")
            else:
                self.normal_merge()

            self.close_files()

        except Exception as err:
            print(err)
            return

    # Files
    def normal_merge(self):
        first_header = None

        for file in self.files:
            reader = csv.DictReader(file)
            if first_header is None:
                first_header = reader.fieldnames
                output_writer = csv.DictWriter(self.output_file, fieldnames=reader.fieldnames)
                output_writer.writeheader()
            else:
                if reader.fieldnames != first_header:
                    print("ERROR - CSV Headers are not matching!")
            for row in reader:
                output_writer.writerow(row)
            if self.verbose:
                print("Merged file " + file.name)



    def time_merge(self):
        first_header = None
        readers = {}
        first_rows = {}
        i = 0
        print("TIME MERGE")
        for file in self.files:
            print("File " + file.name)
            reader = csv.DictReader(file)
            readers[i] = reader
            if first_header is None:
                first_header = reader.fieldnames
                output_writer = csv.DictWriter(self.output_file, fieldnames=reader.fieldnames)
                output_writer.writeheader()
            first_rows[i] = next(reader)
            i += 1

        while len(first_rows) > 0:
            index = self._get_lowest_index(first_rows)
            output_writer.writerow(first_rows[index])
            try:
                first_rows[index] = next(readers[index])
            except StopIteration:
                # Next threw an exception meaning there are no more rows in the reader
                print("File " + str(index) + " is empty")
                del first_rows[index]

        print("Merged all reports")

    def _get_lowest_index(self, list):
        lowest_index = None
        lowest_time = None
        # Linear searching currently implemented with complexity O(n)
        # Needs to be changed to faster algorithm that's using O(log(n)). Ideally Python "sorted()"
        for key, value in list.items():

            # Parsing time from string to datetime object
            time = self._parse_time(value[self.time_sorting])

            # Checking if this is minimum time
            if lowest_time is None or time < lowest_time:
                # New minimum time found
                lowest_time = time
                lowest_index = key
        return lowest_index

    def _parse_time(self, time_str):
        try:
            time = datetime.datetime.strptime(time_str, self.time_format)
        except Exception as err:
            print("NOT ABLE TO PARSE TIME " + time_str)
            print(err)
            return None
        return time

    def _verify_settings(self):
        pass

    def _create_output_file(self):
        try:
            file = open(self.output_file, 'w')
        except Exception as err:
            raise err
        return file

    def close_files(self):
        for file in self.files:
            file.close()

    def _sort_files(self):
        files_to_merge = []
        for item in self.files:
            print("ITEM " + item)
            if self._is_folder(item):
                print("Is folder " + item)
                files_to_merge += self._get_folder_contents(item)
            elif self._is_file(item):
                print("Is file " + item)
                files_to_merge.append(item)
            else:
                if self.verbose:
                    print("Warning - not processing " + item)

        # Replacing original list of files with file descriptors
        self.files = files_to_merge

        if self.verbose:
            self._print_sorting_order(files_to_merge)


    def _is_folder(self, folder):
        if not os.path.isdir(folder) or not os.access(folder, os.R_OK):
            return False
        return True

    def _is_file(self, file):
        if not os.path.isfile(file) or not os.access(file, os.R_OK):
            return False
        return True

    def _get_file(self, file):
        return open(file, 'r')

    def _get_folder_contents(self, folder):
        file_list = []
        for entry in os.scandir(folder):
            if entry.is_file():
                file_list.append(self._get_file(entry))
        return sorted(file_list, key=lambda x: x.name)

    def _print_sorting_order(self, sorted_files):
        print("Files will be sorted in following order:")
        for file in sorted_files:
            print(file.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Files or folders that should be merged", nargs='+')
    parser.add_argument("-o", "--output_file", help="Folder where the output should be placed")
    parser.add_argument("-v", "--verbose", help="Verbose mode", action='store_true')
    parser.add_argument("-n", "--namesort", help="Enable name sorting", action='store_true')
    parser.add_argument("-t", "--timesort", help="Enable time sorting")
    parser.add_argument("-s", "--timeformat", help="Format of the timestamp in column specified in timesort option")
    parser.add_argument("-c", "--timeverify", help="Verify if timestamps are no overlapping")
    args = parser.parse_args()
    report_splitter = ReportMerger(files=args.file, verbose=args.verbose, name_sorting=args.namesort,
                                   time_sorting=args.timesort, output_file=args.output_file,
                                   time_verify=args.timeverify, time_format=args.timeformat)
    report_splitter.merge()
