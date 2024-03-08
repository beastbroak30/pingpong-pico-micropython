from ST7735 import TFT
from machine import SPI, Pin, ADC
import time

# Assuming screen dimensions are 128x160
screen_width = 128
screen_height = 160

spi = SPI(0, baudrate=20000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
tft = TFT(spi, 0, 7, 1)
tft.initr()
tft.rgb(True)

# Set paddle parameters
paddle_width = 40
paddle_height = 10
paddle_color = TFT.GREEN

# Set ball parameters
ball_radius = 5
ball_color = TFT.RED
ball_speed_x = 2
ball_speed_y = 2

# Set up ADC for potentiometer input
potentiometer_pin = 26  # GPIO pin connected to the potentiometer
adc = ADC(Pin(potentiometer_pin))
adc_width = 10  # 10-bit ADC resolution

# Set dead zone and smoothing factor
dead_zone = 100  # Adjust based on your potentiometer characteristics
smoothing_factor = 0.1  # Adjust based on your preference

# Set the step size for paddle movement
step_size = 1  # Adjust based on your preference

# Read the initial position of the potentiometer
initial_pot_value = adc.read_u16()

current_paddle_x = screen_width // 2  # Start in the middle of the screen

# Initial ball position and direction
ball_x = screen_width // 2
ball_y = screen_height - paddle_height - 10 - ball_radius
ball_direction_x = 1
ball_direction_y = -1

while True:
    # Read the analog value from the potentiometer
    pot_value = adc.read_u16()

    # Apply dead zone
    if pot_value < initial_pot_value + dead_zone and pot_value > initial_pot_value - dead_zone:
        pot_value = initial_pot_value

    # Smooth the potentiometer value
    target_paddle_x = int((pot_value - initial_pot_value) / max(1, (2**adc_width - 1)) * (screen_width - paddle_width))
    current_paddle_x = int(current_paddle_x + smoothing_factor * (target_paddle_x - current_paddle_x))

    # Calculate the new position with a smaller step size
    current_paddle_x += step_size * (target_paddle_x - current_paddle_x) // max(1, abs(target_paddle_x - current_paddle_x))

    # Limit the paddle within the screen boundaries
    current_paddle_x = max(0, min(screen_width - paddle_width, current_paddle_x))

    # Move the ball
    ball_x += ball_speed_x * ball_direction_x
    ball_y += ball_speed_y * ball_direction_y

    # Bounce the ball on the walls
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= screen_width:
        ball_direction_x *= -1

    if ball_y - ball_radius <= 0:
        ball_direction_y *= -1

    # Bounce the ball on the paddle
    if (
        ball_y + ball_radius >= screen_height - paddle_height - 10
        and current_paddle_x <= ball_x <= current_paddle_x + paddle_width
    ):
        ball_direction_y *= -1

    # Draw the paddle
    tft.fill(TFT.BLACK)  # Clear the screen
    tft.fillrect((current_paddle_x, screen_height - paddle_height - 10), (paddle_width, paddle_height), paddle_color)

    # Draw the ball
    tft.fillcircle((int(ball_x), int(ball_y)), ball_radius, ball_color)

    # Update the display
    time.sleep_ms(20)  # Adjust the delay for the desired update rate
