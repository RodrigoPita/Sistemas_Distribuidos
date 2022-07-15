import io
a_string = 'áâàãä'
e_string = 'éêèë'
i_string = 'íîìï'
o_string = 'óôòõö'
u_string = 'úûùü'
c_string = 'ç'

file_name = 'freq.txt'
file_name_2 = 'conjug.txt'
new_file_name = 'display_dict_2.txt'
new_file_name_2 = 'dictionary_2.txt'

word_list = []
conjug_list = []

for word in io.open( file_name_2, mode = 'r', encoding = 'utf-8' ):
    word = word.strip()
    if ( len( word ) != 5 ): continue
    conjug_list.append( ( word ).upper() )

for line in io.open( file_name, mode = 'r', encoding = 'utf-8' ):
    line = line.strip()
    L = line.split( ',' )
    word = L[0]
    freq = L[1]
    freq = int( freq )
    if ( len( word ) != 5  or word.upper() in conjug_list or freq < 100000 ): continue
    word_list.append( (word+'\n').upper() )
    for i in range( 5 ):
        if ( word[i] in a_string ): word = word[:i] + 'a' + word[i+1:]
        elif ( word[i] in e_string ): word = word[:i] + 'e' + word[i+1:]
        elif ( word[i] in i_string ): word = word[:i] + 'i' + word[i+1:]
        elif ( word[i] in o_string ): word = word[:i] + 'o' + word[i+1:]
        elif ( word[i] in u_string ): word = word[:i] + 'u' + word[i+1:]
        elif ( word[i] in c_string ): word = word[:i] + 'c' + word[i+1:]
    file_2 = open( new_file_name_2, 'a' )
    file_2.write( (word+'\n').upper() )
    file_2.close

file = io.open( new_file_name, mode = 'w', encoding = 'utf-8' )
file.writelines( word_list )
file.close