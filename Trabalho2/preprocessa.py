import io
a_string = 'áâàãä'
e_string = 'éêèë'
i_string = 'íîìï'
o_string = 'óôòõö'
u_string = 'úûùü'
c_string = 'ç'

file_name = 'palavras.txt'
new_file_name = 'dictionary.txt'

for word in io.open( file_name, mode = 'r', encoding = 'utf-8' ):
    word = word.strip()
    if ( len( word ) != 5 ): continue
    for i in range( 5 ):
        if ( word[i] in a_string ): word = word[:i] + 'a' + word[i+1:]
        elif ( word[i] in e_string ): word = word[:i] + 'e' + word[i+1:]
        elif ( word[i] in i_string ): word = word[:i] + 'i' + word[i+1:]
        elif ( word[i] in o_string ): word = word[:i] + 'o' + word[i+1:]
        elif ( word[i] in u_string ): word = word[:i] + 'u' + word[i+1:]
        elif ( word[i] in c_string ): word = word[:i] + 'c' + word[i+1:]
    file = open( new_file_name, 'a' )
    file.write( (word+'\n').upper() )