import csv
import random

# Confederation mappings
conmebol = {'uy Uruguay', 'ec Ecuador', 'py Paraguay', 'br Brazil', 'ar Argentina', 'co Colombia'}
uefa = {'no Norway', 'sct Scotland', 'ch Switzerland', 'nl Netherlands', 'tr Türkiye', 
        'fr France', 'at Austria', 'ba Bosnia–Herz', 'se Sweden', 'de Germany', 
        'eng England', 'pt Portugal', 'es Spain', 'hr Croatia', 'be Belgium', 'cz Czechia'}

squad_to_fed = {squad: 'CONMEBOL' for squad in conmebol}
squad_to_fed.update({squad: 'UEFA' for squad in uefa})

input_file = 'Shooting Stat_population.csv'
output_file = 'Shooting Stat_40 random samples (updated v2).csv'

target_columns = ['Rk', 'Player', 'Pos', 'Squad', 'Gls', 'Sh', 'G/Sh']

uefa_primary = []
uefa_null = []
conmebol_primary = []
conmebol_null = []

# Using 'utf-8-sig' strips hidden UTF-8 BOM characters (\ufeff)
with open(input_file, mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    
    # Dynamically find the row that contains 'Rk'
    header2 = None
    for row in reader:
        # Strip whitespace from row elements to avoid hidden character issues
        cleaned_row = [col.strip() for col in row]
        if 'Rk' in cleaned_row:
            header2 = cleaned_row
            break

    if not header2:
        raise ValueError("Could not find header row containing 'Rk' in the CSV file.")

    col_idx = {name: header2.index(name) for name in target_columns}
    
    for row in reader:
        if not row or len(row) <= max(col_idx.values()):
            continue
        
        squad = row[col_idx['Squad']].strip()
        pos = row[col_idx['Pos']].strip()
        sh_str = row[col_idx['Sh']].strip()
        gsh_str = row[col_idx['G/Sh']].strip()
        
        # 1. Check if CONMEBOL or UEFA
        if squad not in squad_to_fed:
            continue
        
        # 2. Exclude Goalkeepers (GK)
        if pos == 'GK':
            continue
            
        # 3. Exclude players with 0 shots
        try:
            sh_val = float(sh_str)
            if sh_val <= 0:
                continue
        except ValueError:
            continue
            
        fed = squad_to_fed[squad]
        new_row = [
            row[col_idx['Rk']],
            row[col_idx['Player']],
            pos,
            squad,
            fed,
            row[col_idx['Gls']],
            sh_str,
            gsh_str
        ]
        
        # 4. Separate by Federation and G/Sh null status
        is_valid_gsh = gsh_str != '' and gsh_str.lower() != 'nan'
        if fed == 'UEFA':
            if is_valid_gsh:
                uefa_primary.append(new_row)
            else:
                uefa_null.append(new_row)
        else:  # CONMEBOL
            if is_valid_gsh:
                conmebol_primary.append(new_row)
            else:
                conmebol_null.append(new_row)

# Sample 20 UEFA players (18 primary, up to 2 null)
sample_uefa_p = random.sample(uefa_primary, min(18, len(uefa_primary)))
sample_uefa_n = random.sample(uefa_null, min(2, len(uefa_null)))
sample_uefa = sample_uefa_p + sample_uefa_n
if len(sample_uefa) < 20:
    remaining_uefa = [r for r in uefa_primary if r not in sample_uefa_p]
    sample_uefa += random.sample(remaining_uefa, min(20 - len(sample_uefa), len(remaining_uefa)))

# Sample 20 CONMEBOL players (18 primary, up to 2 null)
sample_conmebol_p = random.sample(conmebol_primary, min(18, len(conmebol_primary)))
sample_conmebol_n = random.sample(conmebol_null, min(2, len(conmebol_null)))
sample_conmebol = sample_conmebol_p + sample_conmebol_n
if len(sample_conmebol) < 20:
    remaining_conmebol = [r for r in conmebol_primary if r not in sample_conmebol_p]
    sample_conmebol += random.sample(remaining_conmebol, min(20 - len(sample_conmebol), len(remaining_conmebol)))

# Combine, shuffle, and save
final_sample = sample_uefa + sample_conmebol
random.shuffle(final_sample)

header_out = ['Rk', 'Player', 'Pos', 'Squad', 'Federation', 'Gls', 'Sh', 'G/Sh']
with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header_out)
    writer.writerows(final_sample)

print(f"Successfully saved header and {len(final_sample)} rows (20 UEFA, 20 CONMEBOL) to '{output_file}'.")