"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import math

class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


class RandomWalkEnemy(Enemy):

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.state = None
        self.speed_x = 3
        self.speed_y = 3

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='pink')

    def update(self) -> None:
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y < 0 or self.y > self.canvas.winfo_height():
            self.speed_y = -self.speed_y
        if self.x < 0 or self.x > self.canvas.winfo_width():
            self.speed_x = -self.speed_x
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
        print(self.game.enemies)


class ChasingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.state = None
        self.speed_x = 3
        self.speed_y = 3

    def create(self):
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill='lightblue')

    def update(self) -> None:
        player_x = self.game.player.x
        player_y = self.game.player.y

        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            dx /= distance
            dy /= distance

        dx *= self.speed_x
        dy *= self.speed_y
        self.x += dx
        self.y += dy

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class FencingEnemy(Enemy):
    def __init__(self,
                game: "TurtleAdventureGame",
                size: int,
                color: str):
        super().__init__(game, size, color)
        self.state = self.right
        self.speed = 3
        self.home_size = self.game.home.size
        self.home_x = self.game.home.x
        self.home_y = self.game.home.y
        self.check_xl = self.home_x-self.home_size/2 - 10
        self.check_xr = self.home_x+self.home_size/2 + 10
        self.check_yt = self.home_y-self.home_size/2 - 20
        self.check_yb = self.home_y-self.home_size/2 + 28

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill='violet')

    def update(self) -> None:
        self.state()
        if self.hits_player():
            self.game.game_over_lose()

    def right(self):
        self.x += self.speed
        if self.x > self.check_xr:
            self.state = self.down

    def down(self):
        self.y += self.speed
        if self.y > self.check_yb:
            self.state = self.left

    def left(self):
        self.x -= self.speed
        if self.x < self.check_xl:
            self.state = self.up

    def up(self):
        self.y -= self.speed
        if self.y < self.check_yt:
            self.state = self.right

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class TrainEnemy(Enemy):
    def __init__(self,
                game: "TurtleAdventureGame",
                size: int,
                color: str):
        super().__init__(game, size, color)
        self.walk = self.canvas.winfo_width() - 100
        self.speed = 5
        self.state = self.left
        self.check = True

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill='red')

    def update(self) -> None:
        self.state()
        if self.hits_player():
            self.game.game_over_lose()

    def down(self):
        self.y += self.speed
        if self.y > self.canvas.winfo_height():
            self.check = False
            self.state = self.left

    def up(self):
        self.y -= self.speed
        if self.y < 0:
            self.check = True
            self.state = self.left

    def left(self):
        self.x -= self.speed
        if self.x < self.walk:
            if self.check:
                self.state = self.down
            if not self.check:
                self.state = self.up
            self.walk -= 100

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        pass


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if self.level == 1:
            random_walk_enemy_1 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_1.x = 100
            random_walk_enemy_1.y = 100

            random_walk_enemy_2 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_2.x = 500
            random_walk_enemy_2.y = 100

            random_walk_enemy_3 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_3.x = 700
            random_walk_enemy_3.y = 300

            random_walk_enemy_4 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_4.x = 0
            random_walk_enemy_4.y = 300

            random_walk_enemy_5 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_5.x = 0
            random_walk_enemy_5.y = 500

            random_walk_enemy_6 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_6.x = 300
            random_walk_enemy_6.y = 0
            self.game.add_element(random_walk_enemy_1)
            self.game.add_element(random_walk_enemy_2)
            self.game.add_element(random_walk_enemy_3)
            self.game.add_element(random_walk_enemy_4)
            self.game.add_element(random_walk_enemy_5)
            self.game.add_element(random_walk_enemy_6)
            self.game.after(10000, self.create_enemy)

        if self.level == 2:
            random_walk_enemy_1 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_1.x = 100
            random_walk_enemy_1.y = 100

            random_walk_enemy_2 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_2.x = 500
            random_walk_enemy_2.y = 100

            random_walk_enemy_3 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_3.x = 700
            random_walk_enemy_3.y = 300

            random_walk_enemy_4 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_4.x = 0
            random_walk_enemy_4.y = 300

            random_walk_enemy_5 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_5.x = 0
            random_walk_enemy_5.y = 500

            random_walk_enemy_6 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_6.x = 300
            random_walk_enemy_6.y = 0
            self.game.add_element(random_walk_enemy_1)
            self.game.add_element(random_walk_enemy_2)
            self.game.add_element(random_walk_enemy_3)
            self.game.add_element(random_walk_enemy_4)
            self.game.add_element(random_walk_enemy_5)
            self.game.add_element(random_walk_enemy_6)

            chasing_enemy = ChasingEnemy(self.__game, 20, "red")
            self.game.add_element(chasing_enemy)

            fencing_enemy = FencingEnemy(self.__game, 15, "red")
            fencing_enemy.x = self.game.home.x-self.game.home.size/2 - 10
            fencing_enemy.y = self.game.home.y-self.game.home.size/2 - 10
            self.game.add_element(fencing_enemy)
            self.game.after(10000, self.create_enemy)

        if self.level == 3:
            random_walk_enemy_1 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_1.x = 100
            random_walk_enemy_1.y = 100

            random_walk_enemy_2 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_2.x = 500
            random_walk_enemy_2.y = 100

            random_walk_enemy_3 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_3.x = 700
            random_walk_enemy_3.y = 300

            random_walk_enemy_4 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_4.x = 0
            random_walk_enemy_4.y = 300

            random_walk_enemy_5 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_5.x = 0
            random_walk_enemy_5.y = 500

            random_walk_enemy_6 = RandomWalkEnemy(self.__game, 20, "red")
            random_walk_enemy_6.x = 300
            random_walk_enemy_6.y = 0
            self.game.add_element(random_walk_enemy_1)
            self.game.add_element(random_walk_enemy_2)
            self.game.add_element(random_walk_enemy_3)
            self.game.add_element(random_walk_enemy_4)
            self.game.add_element(random_walk_enemy_5)
            self.game.add_element(random_walk_enemy_6)

            chasing_enemy = ChasingEnemy(self.__game, 20, "red")
            self.game.add_element(chasing_enemy)

            fencing_enemy = FencingEnemy(self.__game, 15, "red")
            fencing_enemy.x = self.game.home.x - self.game.home.size / 2 - 10
            fencing_enemy.y = self.game.home.y - self.game.home.size / 2 - 10
            self.game.add_element(fencing_enemy)
            train_enemy = TrainEnemy(self.__game, 20, color="red")
            train_enemy.x = self.game.canvas.winfo_width()
            train_enemy.y = 0
            self.game.add_element(train_enemy)
            self.game.after(10000, self.create_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
