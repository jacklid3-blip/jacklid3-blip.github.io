# Authors: Jack Lidster, Anthony Sison
# Date: 9/19/2025
# Description: This program finds the surface area of a horse track field based on user input.

import math

PI = math.pi

outer_radius = float(input("Enter the outer radius of the horse track (in meters): "))
inner_radius = float(input("Enter the inner radius of the horse track (in meters): "))
length = float(input("Enter the length of the straight sections (in meters): "))
width = float(input("Enter the width of the track (in meters): "))

outer_circle_area = PI * (outer_radius ** 2)
inner_circle_area = PI * (inner_radius ** 2)
rectangle_area = length * width
track_area = (outer_circle_area - inner_circle_area) + rectangle_area

print("The surface area of the horse track field is", round(track_area, 2), "square meters.")
input("Press Enter to exit")