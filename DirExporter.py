import glob
import os

# Specify the directory containing the C# files
directory = r'C:\Users\NT\Documents\NinjaTrader 8\bin\Custom\Indicators'

# Specify the output file name
output_file = 'DirExported.txt'

# Define a separator (you can customize this)
separator = '\n\n' + '#'*25 + '\n\n'

# Get all .cs files in the directory
csharp_files = glob.glob(os.path.join(directory, '*.cs'))

# Read and combine the contents of all files
combined_content = ''
for file_path in csharp_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        combined_content += file_content + separator

# Write the combined content to the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write(combined_content)

print(f"Combined {len(csharp_files)} C# files into {output_file}")