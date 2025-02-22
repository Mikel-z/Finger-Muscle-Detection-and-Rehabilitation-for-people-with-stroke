# Load melody chart
def load_melody_chart_5(file_path):
    notes = []
    unique_patterns = [
        '0000', '0001', '0002', '0003', '0010', '0011', '0012', '0013', '0020', '0021', '0022', '0023', 
        '0030', '0031', '0032', '0033', '0100', '0101', '0102', '0103', '0110', '0111', '0112', '0113', 
        '0120', '0121', '0122', '0123', '0130', '0131', '0132', '0133', '0200', '0201', '0202', '0203', 
        '0210', '0211', '0212', '0213', '0220', '0221', '0222', '0223', '0230', '0231', '0232', '0233', 
        '0300', '0301', '0302', '0303', '0310', '0311', '0312', '0313', '0320', '0321', '0322', '0323', 
        '0330', '0331', '0332', '0333', '1000', '1001', '1002', '1003', '1010', '1011', '1012', '1013', 
        '1020', '1021', '1022', '1023', '1030', '1031', '1032', '1033', '1100', '1101', '1102', '1103', 
        '1110', '1111', '1112', '1113', '1120', '1121', '1122', '1123', '1130', '1131', '1132', '1133', 
        '1200', '1201', '1202', '1203', '1210', '1211', '1212', '1213', '1220', '1221', '1222', '1223', 
        '1230', '1231', '1232', '1233', '1300', '1301', '1302', '1303', '1310', '1311', '1312', '1313', 
        '1320', '1321', '1322', '1323', '1330', '1331', '1332', '1333', '2000', '2001', '2002', '2003', 
        '2010', '2011', '2012', '2013', '2020', '2021', '2022', '2023', '2030', '2031', '2032', '2033', 
        '2100', '2101', '2102', '2103', '2110', '2111', '2112', '2113', '2120', '2121', '2122', '2123', 
        '2130', '2131', '2132', '2133', '2200', '2201', '2202', '2203', '2210', '2211', '2212', '2213', 
        '2220', '2221', '2222', '2223', '2230', '2231', '2232', '2233', '2300', '2301', '2302', '2303', 
        '2310', '2311', '2312', '2313', '2320', '2321', '2322', '2323', '2330', '2331', '2332', '2333', 
        '3000', '3001', '3002', '3003', '3010', '3011', '3012', '3013', '3020', '3021', '3022', '3023', 
        '3030', '3031', '3032', '3033', '3100', '3101', '3102', '3103', '3110', '3111', '3112', '3113', 
        '3120', '3121', '3122', '3123', '3130', '3131', '3132', '3133', '3200', '3201', '3202', '3203', 
        '3210', '3211', '3212', '3213', '3220', '3221', '3222', '3223', '3230', '3231', '3232', '3233', 
        '3300', '3301', '3302', '3303', '3310', '3311', '3312', '3313', '3320', '3321', '3322', '3323', 
        '3330', '3331', '3332', '3333'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as file:
        in_notes_section = False
        time_stamp = 0.0
        bpm = 160
        seconds_per_beat = 60 / bpm  # Calculate seconds per beat
        for line in file:
            line = line.strip()
            if line.startswith("#NOTES:"):
                in_notes_section = True
                print("Found #NOTES section")
                continue
            if in_notes_section:
                if line.startswith("//") or not line:
                    continue
                if line.startswith(","):
                    time_stamp += seconds_per_beat  # Increment time for each measure
                    #print(f"New measure, time_stamp={time_stamp}")
                    continue
                if any(line.startswith(pattern) for pattern in unique_patterns):
                    #print(f"Processing line: {line}")
                    for i, char in enumerate(line):
                        if char in '123':
                            notes.append((time_stamp, i, char))
                            #print(f"Added note: time_stamp={time_stamp}, key={i}, char={char}")
                        '''
                        elif char == '2':
                            notes.append((time_stamp, i, char))
                            notes.insert(len(notes) - 1, (time_stamp, i, char))  # Insert just above the previous note
                            #print(f"Added note: time_stamp={time_stamp}, key={i}, char={char}")
                        elif char == '3':
                            notes.append((time_stamp, i, char))
                            notes.insert(len(notes) - 1, (time_stamp, i, char))  # Insert just above the previous note
                            notes.insert(len(notes) - 2, (time_stamp, i, char))  # Insert just above the second note
                            #print(f"Added note: time_stamp={time_stamp}, key={i}, char={char}")
                        '''

                    # Increment time for the next line
                    time_stamp += seconds_per_beat  # Increment time for each row (quarter note)

    return notes
def save_notes_to_file(notes, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for note in notes:
            file.write(f"{note[0]},{note[1]},{note[2]}\n")


'''
# Load melody chart
def load_melody_chart(file_path):
    notes = []
    unique_patterns = [['0000', '0001', '0002', '0003', '0010', '0011', '0012', '0013', '0020', '0021', '0022', '0023', '0030', '0031', '0032', '0033', '0100', '0101', '0102', '0103', '0110', '0111', '0112', '0113', '0120', '0121', '0122', '0123', '0130', '0131', '0132', '0133', '0200', '0201', '0202', '0203', '0210', '0211', '0212', '0213', '0220', '0221', '0222', '0223', '0230', '0231', '0232', '0233', '0300', '0301', '0302', '0303', '0310', '0311', '0312', '0313', '0320', '0321', '0322', '0323', '0330', '0331', '0332', '0333', '1000', '1001', '1002', '1003', '1010', '1011', '1012', '1013', '1020', '1021', '1022', '1023', '1030', '1031', '1032', '1033', '1100', '1101', '1102', '1103', '1110', '1111', '1112', '1113', '1120', '1121', '1122', '1123', '1130', '1131', '1132', '1133', '1200', '1201', '1202', '1203', '1210', '1211', '1212', '1213', '1220', '1221', '1222', '1223', '1230', '1231', '1232', '1233', '1300', '1301', '1302', '1303', '1310', '1311', '1312', '1313', '1320', '1321', '1322', '1323', '1330', '1331', '1332', '1333', '2000', '2001', '2002', '2003', '2010', '2011', '2012', '2013', '2020', '2021', '2022', '2023', '2030', '2031', '2032', '2033', '2100', '2101', '2102', '2103', '2110', '2111', '2112', '2113', '2120', '2121', '2122', '2123', '2130', '2131', '2132', '2133', '2200', '2201', '2202', '2203', '2210', '2211', '2212', '2213', '2220', '2221', '2222', '2223', '2230', '2231', '2232', '2233', '2300', '2301', '2302', '2303', '2310', '2311', '2312', '2313', '2320', '2321', '2322', '2323', '2330', '2331', '2332', '2333', '3000', '3001', '3002', '3003', '3010', '3011', '3012', '3013', '3020', '3021', '3022', '3023', '3030', '3031', '3032', '3033', '3100', '3101', '3102', '3103', '3110', '3111', '3112', '3113', '3120', '3121', '3122', '3123', '3130', '3131', '3132', '3133', '3200', '3201', '3202', '3203', '3210', '3211', '3212', '3213', '3220', '3221', '3222', '3223', '3230', '3231', '3232', '3233', '3300', '3301', '3302', '3303', '3310', '3311', '3312', '3313', '3320', '3321', '3322', '3323', '3330', '3331', '3332', '3333']]
    with open(file_path, 'r', encoding='utf-8') as file:
        in_notes_section = False
        time_stamp = 0.0
        bpm = 500
        seconds_per_beat = 60 / bpm  # Calculate seconds per beat
        for line in file:
            line = line.strip()
            if line.startswith("#NOTES:"):
                in_notes_section = True
                print("Found #NOTES section")
                continue
            if in_notes_section:
                if line.startswith("//") or not line:
                    continue
                if line.startswith(","):
                    time_stamp += seconds_per_beat  # Increment time for each measure
                    print(f"New measure, time_stamp={time_stamp}")
                    continue
                if line.startswith(("0000", "1000", "0100", "0010", "0001", "2000", "3000", "1001", "0003", "0101", "0011", "1100", "0200", "0300", "0020", "0030", "0110", "1010", "2020", "3030", "0202", "0303")):
                    print(f"Processing line: {line}")
                    for i, char in enumerate(line):
                        if char in '123':
                            notes.append((time_stamp, i, char))
                            print(f"Added note: time_stamp={time_stamp}, key={i}, char={char}")

                    time_stamp += seconds_per_beat  # Increment time for each row (quarter note)
    return notes
'''
