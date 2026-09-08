import csv

# Define confederation mapping
conmebol = {'uy Uruguay', 'ec Ecuador', 'py Paraguay', 'br Brazil', 'ar Argentina', 'co Colombia'}
uefa = {'no Norway', 'sct Scotland', 'ch Switzerland', 'nl Netherlands', 'tr Türkiye', 
        'fr France', 'at Austria', 'ba Bosnia–Herz', 'se Sweden', 'de Germany', 
        'eng England', 'pt Portugal', 'es Spain', 'hr Croatia', 'be Belgium', 'cz Czechia'}

squad_to_fed = {squad: 'CONMEBOL' for squad in conmebol}
squad_to_fed.update({squad: 'UEFA' for squad in uefa})

input_file = 'Shooting Stat.csv'
output_file = 'Shooting Stat_population.csv'

with open(input_file, mode='r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    
    # Skip standard preamble row if present (header=1 logic)
    header1 = next(reader)
    header2 = next(reader)  # Actual headers: Rk, Player, Pos, Squad, etc.
    
    # Map index positions of target columns
    col_indices = {name: header2.index(name) for name in ['Rk', 'Player', 'Pos', 'Squad', 'Gls', 'Sh', 'G/Sh']}
    
    output_rows = []
    # New header order: Rk, Player, Pos, Squad, Federation, Gls, Sh
    output_rows.append(['Rk', 'Player', 'Pos', 'Squad', 'Federation', 'Gls', 'Sh', 'G/Sh'])
    
    for row in reader:
        if not row:
            continue
        squad = row[col_indices['Squad']]
        if squad in squad_to_fed:
            federation = squad_to_fed[squad]
            new_row = [
                row[col_indices['Rk']],
                row[col_indices['Player']],
                row[col_indices['Pos']],
                squad,
                federation,
                row[col_indices['Gls']],
                row[col_indices['Sh']],
                row[col_indices['G/Sh']]
            ]
            output_rows.append(new_row)

with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(output_rows)

print(f"Successfully processed {len(output_rows) - 1} rows and saved to '{output_file}'.")