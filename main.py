# /// script
# dependencies = [
#     "pygame-ce",
# ]
# ///

import random, sys, pygame, copy
import asyncio
from pygame.locals import *

FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
SPACESIZE = 50
BOARDWIDTH = 8
BOARDHEIGHT = 8
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'
ANIMATIONSPEED = 25

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 50, 255)
BROWN = (174, 94, 0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN

async def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    __ANDROID__ = hasattr(sys, "getandroidapilevel")
    __EMSCRIPTEN__ = hasattr(sys, "_emscripten_info")
    
    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    if __ANDROID__:
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),
                                        pygame.SCALED | pygame.FULLSCREEN)
    elif __EMSCRIPTEN__:
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0)
    else:
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),
                                        pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption('Othello')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
    
    boardImage = pygame.image.load('flippyboard.png')
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (XMARGIN, YMARGIN)
    
    BGIMAGE = pygame.image.load('flippybackground.png')
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(boardImage, boardImageRect)
    
    while True:
        await runGame()

def getSpaceClicked(mousex, mousey):
    x = (mousex - XMARGIN) // SPACESIZE
    y = (mousey - YMARGIN) // SPACESIZE
    if isOnBoard(x, y):
        return (x, y)
    return None

def drawInfo(boardToDraw, playerTile, computerTile, turn):
    scores = getScoreOfBoard(boardToDraw)
    playerScore = scores[playerTile]
    computerScore = scores[computerTile]
    playerText = f'Player: {playerScore}'
    computerText = f'Computer: {computerScore}'
    turnText = f'Turn: {turn.capitalize()}'
    playerSurf = FONT.render(playerText, True, TEXTCOLOR, TEXTBGCOLOR1)
    playerRect = playerSurf.get_rect()
    playerRect.topleft = (WINDOWWIDTH - 120, 70)
    computerSurf = FONT.render(computerText, True, TEXTCOLOR, TEXTBGCOLOR1)
    computerRect = computerSurf.get_rect()
    computerRect.topleft = (WINDOWWIDTH - 120, 90)
    turnSurf = FONT.render(turnText, True, TEXTCOLOR, TEXTBGCOLOR1)
    turnRect = turnSurf.get_rect()
    turnRect.topleft = (WINDOWWIDTH - 120, 110)
    DISPLAYSURF.blit(playerSurf, playerRect)
    DISPLAYSURF.blit(computerSurf, computerRect)
    DISPLAYSURF.blit(turnSurf, turnRect)

def getComputerMove(mainBoard, computerTile):
    validMoves = getValidMoves(mainBoard, computerTile)
    if validMoves:
        return random.choice(validMoves)
    return None

async def runGame():
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = random.choice(['computer', 'player'])
    consecutivePasses = 0
    
    drawBoard(mainBoard)
    playerTile, computerTile = await enterPlayerTile()
    
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    
    hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 8, 40)
    
    while True:
        if turn == 'player':
            validMoves = getValidMoves(mainBoard, playerTile)
            if validMoves:
                consecutivePasses = 0
                movexy = None
                while movexy == None:
                    if showHints:
                        boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                    else:
                        boardToDraw = mainBoard
                    pygame.event.pump()
                    for event in pygame.event.get(MOUSEBUTTONUP, pump=False):
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint((mousex, mousey)):
                            return True
                        elif hintsRect.collidepoint((mousex, mousey)):
                            showHints = not showHints
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None
                    for event in pygame.event.get(FINGERDOWN, pump=False):
                        mousex = int(event.x * WINDOWWIDTH)
                        mousey = int(event.y * WINDOWHEIGHT)
                        if newGameRect.collidepoint((mousex, mousey)):
                            return True
                        elif hintsRect.collidepoint((mousex, mousey)):
                            showHints = not showHints
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None
                    drawBoard(boardToDraw)
                    drawInfo(boardToDraw, playerTile, computerTile, turn)
                    DISPLAYSURF.blit(newGameSurf, newGameRect)
                    DISPLAYSURF.blit(hintsSurf, hintsRect)
                    MAINCLOCK.tick(FPS)
                    pygame.display.update()
                    await asyncio.sleep(0)
                await makeMove(mainBoard, playerTile, movexy[0], movexy[1], True, mainBoard)
                turn = 'computer'
            else:
                consecutivePasses += 1
                turn = 'computer'
        else:
            validMoves = getValidMoves(mainBoard, computerTile)
            if validMoves:
                consecutivePasses = 0
                drawBoard(mainBoard)
                drawInfo(mainBoard, playerTile, computerTile, turn)
                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)
                pygame.display.update()
                await asyncio.sleep(random.randint(5, 15) * 0.1)
                x, y = getComputerMove(mainBoard, computerTile)
                await makeMove(mainBoard, computerTile, x, y, True, mainBoard)
                turn = 'player'
            else:
                consecutivePasses += 1
                turn = 'player'
        
        if consecutivePasses >= 2:
            break
    
    drawBoard(mainBoard)
    drawInfo(mainBoard, playerTile, computerTile, turn)
    
    scores = getScoreOfBoard(mainBoard)
    if scores[playerTile] > scores[computerTile]:
        text = 'You beat the computer by %s points! Congratulations!' % (scores[playerTile] - scores[computerTile])
    elif scores[playerTile] < scores[computerTile]:
        text = 'You lost. The computer beat you by %s points.' % (scores[computerTile] - scores[playerTile])
    else:
        text = 'The game was a tie!'
    
    textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(textSurf, textRect)
    
    text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)
    
    yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)
    
    noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)
    
    while True:
        pygame.event.pump()
        for event in pygame.event.get(MOUSEBUTTONUP, pump=False):
            mousex, mousey = event.pos
            if yesRect.collidepoint((mousex, mousey)):
                return True
            elif noRect.collidepoint((mousex, mousey)):
                return True
        for event in pygame.event.get(FINGERDOWN, pump=False):
            mousex = int(event.x * WINDOWWIDTH)
            mousey = int(event.y * WINDOWHEIGHT)
            if yesRect.collidepoint((mousex, mousey)):
                return True
            elif noRect.collidepoint((mousex, mousey)):
                return True
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yesSurf, yesRect)
        DISPLAYSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        await asyncio.sleep(0)

def translateBoardToPixelCoord(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)

async def animateTileChange(tilesToFlip, tileColor, additionalTile, mainBoard):
    if tileColor == WHITE_TILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    pygame.display.update()
    MAINCLOCK.tick(ANIMATIONSPEED)
    
    for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        
        if tileColor == WHITE_TILE:
            color = tuple([rgbValues] * 3)
        elif tileColor == BLACK_TILE:
            color = tuple([255 - rgbValues] * 3)
        
        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
        
        drawBoard(mainBoard)
        pygame.display.update()
        MAINCLOCK.tick(ANIMATIONSPEED)
        pygame.event.pump()
        await asyncio.sleep(0)

def drawBoard(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))

    for x in range(BOARDWIDTH + 1):
        # draw the horizontal lines
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        # draw the vertical lines
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

def getNewBoard():
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board

def resetBoard(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE

def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE:
                xscore += 1
            if board[x][y] == BLACK_TILE:
                oscore += 1
    return {WHITE_TILE:xscore, BLACK_TILE:oscore}

async def enterPlayerTile():
    textSurf = FONT.render('Do you want to be white or black?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)
    oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)
    while True:
        pygame.event.pump()
        for event in pygame.event.get(MOUSEBUTTONUP, pump=False):
            mousex, mousey = event.pos
            if xRect.collidepoint((mousex, mousey)):
                return [WHITE_TILE, BLACK_TILE]
            elif oRect.collidepoint((mousex, mousey)):
                return [BLACK_TILE, WHITE_TILE]
        for event in pygame.event.get(FINGERDOWN, pump=False):
            mousex = int(event.x * WINDOWWIDTH)
            mousey = int(event.y * WINDOWHEIGHT)
            if xRect.collidepoint((mousex, mousey)):
                return [WHITE_TILE, BLACK_TILE]
            elif oRect.collidepoint((mousex, mousey)):
                return [BLACK_TILE, WHITE_TILE]
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        await asyncio.sleep(0)

async def makeMove(board, tile, xstart, ystart, realMove=False, mainBoard=None):
    tilesToFlip = isValidMove(board, tile, xstart, ystart)
    if tilesToFlip == False:
        return False
    board[xstart][ystart] = tile
    if realMove:
        await animateTileChange(tilesToFlip, tile, (xstart, ystart), mainBoard if mainBoard is not None else board)
        for x, y in tilesToFlip:
            board[x][y] = tile
    return True

def isValidMove(board, tile, xstart, ystart):
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False
    board[xstart][ystart] = tile
    otherTile = getOpponentTile(tile)
    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])
    board[xstart][ystart] = EMPTY_SPACE
    if len(tilesToFlip) == 0:
        return False
    return tilesToFlip

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT

def getBoardWithValidMoves(board, tile):
    dupeBoard = copy.deepcopy(board)
    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    return dupeBoard

def getValidMoves(board, tile):
    validMoves = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves

def getOpponentTile(tile):
    if tile == WHITE_TILE:
        return BLACK_TILE
    else:
        return WHITE_TILE


asyncio.run(main())
