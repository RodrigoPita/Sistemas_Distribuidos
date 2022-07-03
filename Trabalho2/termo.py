from asyncore import write
from random import shuffle
import sys

# nome do banco de palavras
file_name = 'words.txt'

# lista com as palavras
words = []

# abrindo o banco de palavras, para popular a lista
for word in open( file_name ):
    words.append( word.replace( '\n', '' ) )

def chooseWord( list_of_words:list = words ) -> str:
    '''Escolhe uma palavra aleatoria da lista'''
    shuffle( list_of_words )
    return list_of_words[0]

def displayAttempts( w:str, attempts:list = [], round:int = 6) -> None:
    '''Imprime as tentativas no terminal, colorindo as letras caso necessario'''
    for i in range( len( attempts ) ):
        print( f'{i + 1}:', end = ' ' )
        for l in attempts[i]:
            if ( len( l ) > 1 ):
                l = colorLetter( l[0], l[1] )
            print( f'{l}', end = '\u001b[37m ' )
        print()
    if ( round < 6 ): print( f'{round+1}: _ _ _ _ _')

def colorLetter( l:str, token:str ) -> str:
    '''Colore a letra l de acordo com o token'''
    pallete = { 'g': '\u001b[32m',
                'y': '\u001b[33m',
                'w': '\u001b[37m'}
    new_l = pallete[token] + l[0]
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
    if ( test == w ): print( f'\nParabéns, você acertou em {round} tentativas')
    else: print( f'\nA palavra era {w}, mais sorte da próxima vez')

def beginGame():
    chosen_word = chooseWord( words )
    ## print( chosen_word )
    attempts = []
    final_round = 6
    for round in range( 1, 7 ):
        test = input( f'\nTentativa {round}: ').upper()
        while ( test not in words ): test = input( f'Tentativa {round}: ').upper()
        aux = wordAnalize( test, chosen_word )
        attempts.append( aux )
        if ( test == chosen_word ):
            final_round = round
            displayAttempts( chosen_word, attempts )
            break
        displayAttempts( chosen_word, attempts, round )
    ## displayAttempts( chosen_word, attempts )
    finalMessage( test, chosen_word, final_round )

def main():
    beginGame()
    play_again = input( "Quer jogar de novo? ( S/N ): ").upper()
    while play_again != 'N':
        beginGame()
        play_again = input( "Quer jogar de novo? ( S/N ): ").upper()
main()
