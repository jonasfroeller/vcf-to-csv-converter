"""
			DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
						Version 1, 2024

Copyright (C) 2024 Jonas Fröller

Everyone is permitted to copy and distribute verbatim or modified 
copies of this license document, and changing it is allowed as long 
as the name is changed. 

			DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

0. You just DO WHAT THE FUCK YOU WANT TO.

This batch converter is not needed, vcf-to-csv.py is sufficient, I made it to learn python better.
"""

import glob
import os
import re
import subprocess

tempfile_name = "temp.csv"


def run_vcf_to_csv(vcf_file, output_directory, delimiter=',', quote='"', trace=False, verbose=False):
    cmd = ['python3', 'vcf-to-csv.py', '-i', vcf_file, '-o', output_directory, '-d',
           delimiter, '-q', quote, '-t', str(trace), '-v', str(verbose)]
    subprocess.run(cmd, stderr=subprocess.PIPE)


def get_vcf_files(input):
    if os.path.isdir(input):
        vcf_files = [os.path.join(input, f)
                     for f in os.listdir(input) if f.endswith('.vcf')]
    else:
        vcf_files = glob.glob(input)

    return vcf_files


def batch_vcf_to_csv_in_multiple_files(input, output_directory, delimiter=',', quote='"', trace=False, verbose=False):
    vcf_files = get_vcf_files(input)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if not output_directory.endswith(os.path.sep):
        output_directory += os.path.sep

    for vcf_file in vcf_files:
        filename = os.path.basename(vcf_file)
        output_file = output_directory + \
            os.path.splitext(filename)[0] + '.csv'
        run_vcf_to_csv(vcf_file, output_file, delimiter, quote, trace, verbose)


def batch_vcf_to_csv_in_single_file(input, output_file, delimiter=',', quote='"', trace=False, verbose=False):
    vcf_files = get_vcf_files(input)

    all_lines = []
    first_file = True
    for vcf_file in vcf_files:
        cmd = ['python3', 'vcf-to-csv.py', '-i', vcf_file, '-o', tempfile_name, '-d',
               delimiter, '-q', quote, '-t', str(trace), '-v', str(verbose)]
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error converting {vcf_file}: {stderr.decode()}")
            continue

        lines = re.split(r'\r?\n', stdout.decode())
        if first_file:
            header = lines[-4].strip()
            all_lines.append(header)
            first_file = False
        all_lines.extend(line for line in lines[-3:] if line)

    with open(output_file, 'w', newline='') as output:
        output.write('\n'.join(all_lines))


if __name__ == '__main__':
    input_dir = input(
        "Enter the input directory path containing VCF files (glob or folder path): ")
    output_mode = input(
        "Enter the output CSV file path ('single' or 'multiple'): ")

    if output_mode not in ['single', 'multiple']:
        print("Invalid output mode. Exiting...")
        exit(1)

    if output_mode == 'single':
        output_file = input(
            "Enter the output CSV file path (.csv not needed): ")

        if os.path.splitext(output_file)[1] == '.csv':
            output_file = os.path.splitext(output_file)[0]

        output_file = output_file + '.csv'
    elif output_mode == 'multiple':
        output_directory = input(
            "Enter the output directory path for CSV files (automatically created if it doesn't exist): ")

    if output_mode == 'multiple':
        print("Converting VCF files to CSV in multiple files...")
        batch_vcf_to_csv_in_multiple_files(input_dir, output_directory)
    elif output_mode == 'single':
        print("Converting VCF files to CSV in single file...")
        batch_vcf_to_csv_in_single_file(input_dir, output_file)
        os.remove(tempfile_name)

    print("Conversion complete.")
