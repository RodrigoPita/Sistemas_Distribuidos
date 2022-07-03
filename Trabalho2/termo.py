# Para as cores funcionarem no terminal do Windows, use o codigo abaixo no cmd como admin
# reg add HKEY_CURRENT_USER\Console /v VirtualTerminalLevel /t REG_DWORD /d 0x00000001 /f

# biblioteca auxiliar
from random import shuffle

# nome do banco de palavras
file_name = 'words.txt'

# lista com as palavras
words = []

# list com todas as letras
alphabet = [ 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 
            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 
            'Z', 'X', 'C', 'V', 'B', 'N' , 'M']

# abrindo o banco de palavras, para popular a lista
for word in open( file_name ):
    words.append( word.replace( '\n', '' ) )

def chooseWord( list_of_words:list = words ) -> str:
    '''Sorteia a palavra do jogo'''
    shuffle( list_of_words ) # embaralha a lista de palavras
    return list_of_words[0]

def displayAttempts( w:str, attempts:list = [], round:int = 6) -> None:
    '''Imprime as tentativas no terminal, colorindo as letras caso necessario'''
    for i in range( len( attempts ) ):
        print( f'{i + 1}:', end = ' ' )
        for l in attempts[i]:
            if ( len( l ) > 1 ):
                # chama a funcao para alterar a cor da letra l
                l = colorLetter( l[0], l[1] )
            print( f'{l}', end = '\u001b[37m ' )
        print() # apenas uma quebra de linha
    if ( round < 6 ): print( f'{round+1}: _ _ _ _ _')

def colorLetter( l:str, token:str ) -> str:
    '''Colore a letra l de acordo com o token'''
    pallete = { 'g': '\u001b[92m',
                'y': '\u001b[93m',
                'w': '\u001b[37m'} # dicionario com os codigos de cores no terminal
    new_l = pallete[token] + l[0] + pallete['w']
    return new_l

def wordAnalize( test_word:str, real_word:str ) -> list:
    '''Analisa quantas letras a palavra teste tem em comum com a palavra real
    e atrela um token nas letras que estiverem certas
    "g" se a letra pertencer a palavra e estiver na posicao certa
    "y" se a letra pertencer a palavra, mas estiver na posicao errada'''
    position_colors = [] # lista com as letras e seus respectivos tokens
    repeated_letters = [] # lista de letras repetidas que pertencem a palavra real
    for i in range( len( test_word ) ):
        if ( test_word[i] in real_word ): 
            if ( test_word[i] == real_word[i] ): position_colors.append( test_word[i] + 'g' )
            else:
                aux = real_word.count( test_word[i] )
                if ( repeated_letters.count( test_word[i] ) < aux ): position_colors.append( test_word[i] + 'y' )
                else: position_colors.append( test_word[i] )
            repeated_letters.append( test_word[i] )
        else: position_colors.append( test_word[i] )
    for i in range( len( position_colors ) ):
        if ( repetitionAnalize( real_word, position_colors, repeated_letters, i ) ):
            if ( len( position_colors[i] ) > 1 ):
                if ( position_colors[i][1] == 'y' ):
                    repeated_letters.remove( position_colors[i][0] )
                    position_colors[i] = position_colors[i][0]
    return position_colors

def repetitionAnalize( real_word:str, position_colors:list, repeated_letters:list, pos:int ) -> bool:
    '''Analisa se alguma letra foi contada mais do que devia'''
    return ( real_word.count( position_colors[pos][0] ) < repeated_letters.count( position_colors[pos][0] ) 
            and ( position_colors.count( position_colors[pos] ) == repeated_letters.count( position_colors[pos][0] )
            or position_colors.count( position_colors[pos][0] + 'y' ) + 
            position_colors.count( position_colors[pos][0] + 'g' ) == repeated_letters.count( position_colors[pos][0] ) ) )

def finalMessage( test:list , w:str , round:int ) -> None:
    '''Imprime a mensagem final do jogo'''
    if ( test == w ): print( f'\nParabéns, você acertou em {round} tentativas')
    else: print( f'\nA palavra era {w}, mais sorte da próxima vez')

def reduceAlphabet( letters:list, used_letters:list ) -> list:
    '''Retira da lista de letras possiveis
    as letras testadas que nao fazem parte da palavra'''
    for l in used_letters:
        if ( len( l ) > 1 ): 
            letters[alphabet.index( l[0] )] = colorLetter( l[0], l[1] )
        if ( l in letters ): letters[letters.index( l )] = ' '
    return letters

def printAlphabet( letters:list ) -> None:
    print( f'+---------------------+\n| ', end = '' )
    for i in range( len( letters ) ):
        print( f'{letters[i]}', end = ' ' )
        if ( i == 9 ): print( '|\n| ', end = ' ')
        if ( i == 18 ): print( ' |\n|  ', end = ' ')
    print( f'    |\n+---------------------+' )

def beginGame():
    '''Da inicio ao jogo'''
    chosen_word = chooseWord( words )
    possible_letters = [] + alphabet
    attempts = []
    final_round = 6
    for round in range( 1, 7 ):
        printAlphabet( possible_letters )
        test = input( f'\nTentativa {round}: ').upper()
        while ( test not in words ): test = input( f'Tentativa {round}: ').upper()
        aux = wordAnalize( test, chosen_word )
        possible_letters = reduceAlphabet( possible_letters, aux )
        attempts.append( aux )
        if ( test == chosen_word ):
            final_round = round
            displayAttempts( chosen_word, attempts )
            break
        displayAttempts( chosen_word, attempts, round )
    finalMessage( test, chosen_word, final_round )

def main():
    beginGame()
    play_again = input( "Quer jogar de novo? ( S/N ): ").upper()
    while play_again != 'N':
        beginGame()
        play_again = input( "Quer jogar de novo? ( S/N ): ").upper()
main()