import pygame, sys
from pygame.locals import *
import random

pygame.init()

fps = 30
smallFont = pygame.font.Font('freesansbold.ttf', 16)
bigFont = pygame.font.Font('freesansbold.ttf', 24)

WINDOWWIDTH = 1000
WINDOWHEIGHT = 520
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

pygame.display.set_caption('Card Game')

class Game:
    def __init__(self, store, stage, inventory, bank, turnCounter):
        self.allCardObjects = (store, stage, inventory)
        self.store = store
        self.stage = stage
        self.inventory = inventory
        self.firstSelection = None
        self.bank = bank
        self.turnCounter = turnCounter

    def clearAllHighlights(self):
        for cardObject in self.allCardObjects:
            for card in cardObject.cards:
                card.color = BLACK

    def resetClicks(self):
        self.firstSelection = None
        self.clearAllHighlights()

    def firstClick(self, clickedTuple):
        self.firstSelection = clickedTuple
        clickedTuple[2].color = BLUE
        
    def swapCards(self, secondCard):
        object1 = self.firstSelection[0]
        object2 = secondCard[0]
        index1 = self.firstSelection[1]
        index2 = secondCard[1]
        card1 = self.firstSelection[2]
        card2 = secondCard[2]

        if object2 == self.store: #if store receives a card, it does nothing
            self.resetClicks() 
        elif object1 == self.store and (object2 == self.stage or object2 == self.inventory): #handles buying from store
            if self.store.checkTransaction(card1, card2, self.bank):
                object1.cards[index1], object2.cards[index2] = object2.cards[index2], object1.cards[index1]
        else: #handles reordering stage or inventory
            object1.cards[index1], object2.cards[index2] = object2.cards[index2], object1.cards[index1]

class Board:

	def __init__(self, deck, top, columns):
		self.deck = deck
		self.cards = [Card(None, BLACK), Card(None, BLACK), Card(None, BLACK)]
		self.top = top
		self.columns = columns

	def leftCoordsOfBox(self, boxx):
		# Convert board coordinates to pixel coordinates
		XMARGIN = int((WINDOWWIDTH - (self.columns * (self.deck.cards[0].width + self.deck.cards[0].gap) - self.deck.cards[0].gap)) / 2)
		left = boxx * (self.deck.cards[0].width + self.deck.cards[0].gap) + XMARGIN
		return left

	def show(self):
		for x in range(self.columns):
			left = self.leftCoordsOfBox(x)
			self.cards[x].show(left, self.top)

	def clicked(self, mousex, mousey):
		for x in range(self.columns):
			left = self.leftCoordsOfBox(x)
			cardCollisionBox = pygame.Rect(left, self.top, self.deck.cards[0].width, self.deck.cards[0].height)
			if cardCollisionBox.collidepoint(mousex, mousey):
				return (self, x, self.cards[x])
		else:
			return None   

class Store(Board):

	def __init__(self, deck, top, columns):
		super().__init__(deck, top, columns)

	def refresh(self):
		self.cards = []
		self.cards = self.deck.draw(self.columns)

	def checkTransaction(self, card1, card2, bank):
		if card2.rank is None and card1.rank is not None:
			if card1.cost <= bank.money:
				bank.money -= card1.cost
				return True

class Inventory(Board):

	def __init__(self, deck, top, columns):
		super().__init__(deck, top, columns)
		

class Stage(Inventory):

	def __init__(self, deck, top, columns):
		super().__init__(deck, top, columns)

    def battle(self):
        sumOfStrength = 0
        for card in self.cards:
            if card.rank != None:
                sumOfStrength += card.rank
        print(sumOfStrength)
  
	def battle(self):
		sumOfStrength = 0
		for card in self.cards:
			if card.rank != None:
				sumOfStrength += card.rank
		print(sumOfStrength)

class Card:

	RANKS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

	def __init__(self, rank, color):

		self.width = 100
		self.height = 50
		self.gap = 10
		self.rank = rank
		self.color = color
		self.cost = rank

	def show(self, x, y):
		pygame.draw.rect(screen, self.color, (x, y, self.width, self.height), 1)
		number_text = smallFont.render(str(self.rank), True, BLACK) #prints all of the board matrix
		number_text_rect = number_text.get_rect()
		number_text_rect.center = (x + self.width / 2, y + self.height / 2)
		screen.blit(number_text, number_text_rect)

class Deck():

	def __init__(self):
		self.cards = []
		for rank in Card.RANKS:
			card = Card(rank, BLACK)
			self.cards.append(card)

	def shuffle(self):
		random.shuffle(self.cards)

	def draw(self, size):
		drawnCards = []
		assert len(self.cards) >= size #returns error if card cannot be drawn because deck is empty
		for i in range(size):
			drawnCards.append(self.cards[0])
			del self.cards[0]
		return drawnCards

class Button():

	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = "Not defined yet"

	def show(self):
		button = pygame.Rect(self.x, self.y, self.width, self.height)
		pygame.draw.rect(screen, BLACK, button, 2)
		self.displayText(smallFont, False, self.text, BLACK, self.x, self.y)

	def displayText(self, font, rotate, displayedText, color, x, y):
		text = font.render(displayedText, True, color)
		if rotate:
			text = pygame.transform.rotate(text, 90)
		text_rect = text.get_rect()
		text_rect.center = (x, y)
		screen.blit(text, text_rect.center)

class Bank(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.money = 100
        self.interest = 5
        self.text = "Bank: " + str(self.money) + " dollars!"

class TurnCounter(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.text = "Next Turn"
        self.phases = ["Set-up", "Battle"]

class RerollStore(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.text = "Reroll Store"
        self.cost = 1
	
def main():
	run = True
	
	deck = Deck()
	deck.shuffle()
	bank = Bank(WINDOWWIDTH *.5 - 230*.5, 0, 230, 50)
	rerollStore = RerollStore(WINDOWWIDTH *.25 - 230*.5, 0, 230, 50)
	board = Board(deck, None, None)
	store = Store(deck, 60, 4)
	store.refresh()
	stage = Stage(deck, 160, 3)
	inventory = Inventory(deck, 260, 3)
	game = Game(store, stage, inventory, bank)
	
	#variables to track mouse position
	mousex = 0
	mousey = 0

	while run:
		screen.fill(WHITE)

		store.show()
		stage.show()
		inventory.show()
		bank.show()
		rerollStore.show()

		#inputs
		mouseClicked = False
		for event in pygame.event.get(): # event handling loop
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:#tracks mouse motion
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:#tracks mouse click
				mousex, mousey = event.pos
				mouseClicked = True

		if mouseClicked:
			clickResponses = []
			clickResponses.append(store.clicked(mousex, mousey))
			clickResponses.append(stage.clicked(mousex, mousey))
			clickResponses.append(inventory.clicked(mousex, mousey))
			for clickedTuple in clickResponses:
				if clickedTuple is not None:
					if game.firstSelection is None:
						game.firstClick(clickedTuple)
					else:
						game.swapCards(clickedTuple)
						game.resetClicks()
						stage.battle()
						
						
		pygame.display.update()

main()
