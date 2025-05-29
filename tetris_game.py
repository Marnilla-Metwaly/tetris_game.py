#################################################
# tetris.py
#################################################

from cmu_graphics import *
import random

def gameDimensions():
    # Default game dimensions
    rows = 15       # Number of rows in the Tetris board
    cols = 10       # Number of columns in the Tetris board
    cellSize = 20   # Size of each cell in pixels
    margin = 25     # Margin size around the board in pixels
    return (rows, cols, cellSize, margin)

def playTetris():
    # Retrieve game dimensions
    rows, cols, cellSize, margin = gameDimensions()
    # Calculate window size
    width = cols * cellSize + margin * 2
    height = rows * cellSize + margin * 2
    
    runApp(width=width, height=height)

def onAppStart(app):
    app.timerDelay = 300  # Default delay in milliseconds
    app.fallCounter = 0   
    app.fallDelay = 20     # Number of steps before moving the piece down
    # Set up game dimensions
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = 'blue'
    # Initialize the board with the empty color
    app.board = [[app.emptyColor for _ in range(app.cols)]\
                 for _ in range(app.rows)]
    
    # Define the seven standard Tetris pieces
    iPiece = [
        [True, True, True, True]
    ]
    jPiece = [
        [True, False, False],
        [True, True,  True]
    ]
    lPiece = [
        [False, False, True],
        [True,  True,  True]
    ]
    oPiece = [
        [True, True],
        [True, True]
    ]
    sPiece = [
        [False, True, True],
        [True,  True, False]
    ]
    tPiece = [
        [False, True, False],
        [True,  True, True]
    ]
    zPiece = [
        [True,  True, False],
        [False, True, True]
    ]

    # Store pieces and their colors
    app.tetrisPieces = [iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece]
    app.tetrisPieceColors = ['red', 'yellow', 'magenta', 'pink', 'cyan',\
                             'green', 'orange']

    # Initialize game state
    app.isPaused = False
    app.isGameOver = False
    app.score = 0  

    # Bonus mode flag
    app.bonusMode = False

    # Generate the first falling piece
    newFallingPiece(app)

def newFallingPiece(app):
    if app.bonusMode:
        app.fallingPiece = app.nextFallingPiece
        app.fallingPieceColor = app.nextFallingPieceColor
        # Prepare the next piece if in bonus mode
        randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
        app.nextFallingPiece = app.tetrisPieces[randomIndex]
        app.nextFallingPieceColor = app.tetrisPieceColors[randomIndex]
    
    else:
        # Randomly select a piece and its color
        randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
        app.fallingPiece = app.tetrisPieces[randomIndex]
        app.fallingPieceColor = app.tetrisPieceColors[randomIndex]

    # Position the piece at the top-middle of the board
    app.fallingPieceRow = 0
    app.fallingPieceCol = app.cols // 2 - len(app.fallingPiece[0]) // 2
    # Check for game over condition
    if not fallingPieceIsLegal(app):
        app.isGameOver = True

def moveFallingPiece(app, drow, dcol):
    # Attempt to move the falling piece
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol
    if not fallingPieceIsLegal(app):
        # Revert if move is illegal
        app.fallingPieceRow -= drow
        app.fallingPieceCol -= dcol
        return False
    return True

def rotateFallingPiece(app):
    # Save the current state
    oldPiece = app.fallingPiece
    oldRow = app.fallingPieceRow
    oldCol = app.fallingPieceCol
    oldNumRows = len(oldPiece)
    oldNumCols = len(oldPiece[0])

    # Generate the new rotated piece (90 degrees counterclockwise)
    newNumRows = oldNumCols
    newNumCols = oldNumRows
    newPiece = [[False] * newNumCols for _ in range(newNumRows)]

    for r in range(oldNumRows):
        for c in range(oldNumCols):
            newRow = oldNumCols - 1 - c
            newCol = r
            newPiece[newRow][newCol] = oldPiece[r][c]

    # Compute the new position to keep the piece centered
    oldCenterRow = oldRow + oldNumRows // 2
    oldCenterCol = oldCol + oldNumCols // 2
    newRow = oldCenterRow - newNumRows // 2
    newCol = oldCenterCol - newNumCols // 2

    # Update the piece and its position
    app.fallingPiece = newPiece
    app.fallingPieceRow = newRow
    app.fallingPieceCol = newCol

    if not fallingPieceIsLegal(app):
        # Revert if rotation is illegal
        app.fallingPiece = oldPiece
        app.fallingPieceRow = oldRow
        app.fallingPieceCol = oldCol

def fallingPieceIsLegal(app):
    # Check if the falling piece is in a legal position
    for r in range(len(app.fallingPiece)):
        for c in range(len(app.fallingPiece[0])):
            if app.fallingPiece[r][c]:
                boardRow = app.fallingPieceRow + r
                boardCol = app.fallingPieceCol + c
                if (boardRow < 0 or boardRow >= app.rows or
                    boardCol < 0 or boardCol >= app.cols):
                    return False
                if app.board[boardRow][boardCol] != app.emptyColor:
                    return False
    return True

def placeFallingPiece(app):
    # Place the falling piece onto the board
    for r in range(len(app.fallingPiece)):
        for c in range(len(app.fallingPiece[0])):
            if app.fallingPiece[r][c]:
                boardRow = app.fallingPieceRow + r
                boardCol = app.fallingPieceCol + c
                app.board[boardRow][boardCol] = app.fallingPieceColor
    # Remove any full rows
    removeFullRows(app)

def removeFullRows(app):
    # Remove any full rows from the board and update the score
    newBoard = []
    fullRows = 0
    for row in app.board:
        if app.emptyColor not in row:
            fullRows += 1
            # Do not add this row to newBoard
        else:
            newBoard.append(row)
    # Add empty rows at the top
    for _ in range(fullRows):
        newBoard.insert(0, [app.emptyColor] * app.cols)
    app.board = newBoard
    # Update score
    app.score += fullRows
    # Adjust speed if in bonus mode
    if app.bonusMode:
        increaseSpeed(app)

def increaseSpeed(app):
    # Increase the falling speed as the score increases
    # Minimum fallDelay is 2 to prevent zero or negative delay
    app.fallDelay = max(2, 10 - app.score // 10)

def drawBoard(app):
    # Draw all the cells in the board
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)

def drawCell(app, row, col, color=None):
    # Draw a single cell at the given row and column
    if color is None:
        color = app.board[row][col]
    x0 = app.margin + col * app.cellSize
    y0 = app.margin + row * app.cellSize
    drawRect(x0, y0, app.cellSize, app.cellSize, fill=color, border='black',\
             borderWidth=2)

def drawFallingPiece(app):
    # Draw the currently falling piece
    piece = app.fallingPiece
    color = app.fallingPieceColor
    for r in range(len(piece)):
        for c in range(len(piece[0])):
            if piece[r][c]:
                row = app.fallingPieceRow + r
                col = app.fallingPieceCol + c
                drawCell(app, row, col, color)

def drawNextPiece(app):
    # Draw the next piece preview
    if app.bonusMode:
        piece = app.nextFallingPiece
        color = app.nextFallingPieceColor
        startX = app.width - app.margin // 2 - len(piece[0]) * app.cellSize
        startY = app.margin
        drawLabel('Next:', startX + len(piece[0]) * app.cellSize / 2,\
                  startY - 15, size=15, bold=True)
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if piece[r][c]:
                    x = startX + c * app.cellSize
                    y = startY + r * app.cellSize
                    drawRect(x, y, app.cellSize, app.cellSize, fill=color,\
                             border='black', borderWidth=2)

def drawScore(app):
    # Draw the score at the top of the board
    scoreText = f"Score: {app.score}"
    x = (app.cols * app.cellSize)/2 + app.margin
    y = app.margin / 2
    drawLabel(scoreText, x, y, size=20, bold=True)

def redrawAll(app):
    # Draw the background and game elements
    drawRect(0, 0, app.width, app.height, fill='orange')  # Background color
    drawBoard(app)
    if not app.isGameOver:
        drawFallingPiece(app)
        if app.bonusMode:
            drawNextPiece(app)
    drawScore(app)
    if app.isGameOver:
        # Display 'Game Over' message
        drawRect(app.margin, app.margin + app.cellSize, app.cols*app.cellSize,\
                 app.cellSize*2, fill='black')
        x = (app.cols * app.cellSize)/2 + app.margin
        y = app.margin + app.cellSize*2
        drawLabel('Game Over!', x, y, size=25, fill='yellow', align='center',\
                  bold=True)
    elif app.isPaused:
        # Display 'Paused' message
        drawRect(0, 0, app.width, app.height, fill='grey', opacity=65)
        drawLabel('Paused', app.width / 2, app.height / 2, size=30,\
                  fill='white')

def onKeyPress(app, key):
    if key in 'Rr':
        onAppStart(app)
    elif key in 'Bb':
        app.bonusMode = True
        # Initialize nextFallingPiece and nextFallingPieceColor
        randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
        app.nextFallingPiece = app.tetrisPieces[randomIndex]
        app.nextFallingPieceColor = app.tetrisPieceColors[randomIndex]
        print("Bonus mode activated!")
        print("Bonus Features:")
        print("1- Next Piece Preview: See the next piece that will fall")
        print("2- Increasing Speed: The game speeds up as your score increases")
    elif not app.isGameOver and not app.isPaused:
        if key == 'left':
            moveFallingPiece(app, 0, -1)
        elif key == 'right':
            moveFallingPiece(app, 0, 1)
        elif key == 'down':
            moveFallingPiece(app, 1, 0)
        elif key == 'up':
            rotateFallingPiece(app)
        elif key == 'space':
            # Hard drop
            while moveFallingPiece(app, 1, 0):
                pass
            placeFallingPiece(app)
            newFallingPiece(app)
        elif key in 'Pp':
            app.isPaused = not app.isPaused
    elif key in 'Pp':
        app.isPaused = not app.isPaused

def onStep(app):
    if not app.isPaused and not app.isGameOver:
        app.fallCounter += 1
        if app.fallCounter % app.fallDelay == 0:
            if not moveFallingPiece(app, 1, 0):
                placeFallingPiece(app)
                newFallingPiece(app)

# Start the game
playTetris()


