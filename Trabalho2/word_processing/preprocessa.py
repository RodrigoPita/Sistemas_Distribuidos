import io
a_string = 'áâàãä'
e_string = 'éêèë'
i_string = 'íîìï'
o_string = 'óôòõö'
u_string = 'úûùü'
c_string = 'ç'

WORDS_FREQUENCY = 'Trabalho2/word_processing/filters/frequency_per_word.txt'
CONJUGATION_WORDS = 'Trabalho2/word_processing/filters/conjugation_words.txt'
COMPLETE_DICTIONARY = 'word_processing/result/complete_dictionary_2.txt'
NO_ACCENT_DICT = 'word_processing/result/no_accent_dictionary_2.txt'

WORD_MAX_LENGTH = 5
MIN_FREQUENCY = 100000

def not_playable(word, conjug_list, freq):
    not_playable_length = len( word ) != WORD_MAX_LENGTH
    not_playable_class = word.upper() in conjug_list
    not_playable_frequency = freq < MIN_FREQUENCY
    return  not_playable_length or not_playable_class or not_playable_frequency

def eliminate_accents(word):
    for i in range( WORD_MAX_LENGTH ):
            if ( word[i] in a_string ): word = word[:i] + 'a' + word[i+1:]
            elif ( word[i] in e_string ): word = word[:i] + 'e' + word[i+1:]
            elif ( word[i] in i_string ): word = word[:i] + 'i' + word[i+1:]
            elif ( word[i] in o_string ): word = word[:i] + 'o' + word[i+1:]
            elif ( word[i] in u_string ): word = word[:i] + 'u' + word[i+1:]
            elif ( word[i] in c_string ): word = word[:i] + 'c' + word[i+1:]
    return word

def get_five_letters_conjugation_words():
    for word in io.open( CONJUGATION_WORDS, mode = 'r', encoding = 'utf-8' ):
        word = word.strip()
        if ( len( word ) != 5 ): continue
        conjug_list.append( ( word ).upper() )
    return conjug_list

def get_playable_words(conjug_list):
    for line in io.open( WORDS_FREQUENCY, mode = 'r', encoding = 'utf-8' ):
        line = line.strip()
        L = line.split( ',' )
        word = L[0]
        freq = int(L[1])
        
        if ( not_playable(word, conjug_list, freq) ): continue
        
        playable_words_list.append( (word+'\n').upper() )
        word = eliminate_accents(word)

        no_accent_file = open( NO_ACCENT_DICT, 'a' )
        no_accent_file.write( (word+'\n').upper() )
        no_accent_file.close
    return playable_words_list


conjug_list = get_five_letters_conjugation_words()
playable_words_list = get_playable_words(conjug_list)

file = io.open( COMPLETE_DICTIONARY, mode = 'w', encoding = 'utf-8' )
file.writelines( playable_words_list )
file.close