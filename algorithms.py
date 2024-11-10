import math
from typing import Tuple

def geographic_midpoint(coordinates: list) -> Tuple[float, float]:
    """
    Calculate the geographic midpoint of a list of latitude and longitude points.

    param: coordinates (list of tuples): A list of (latitude, longitude) tuples.

    return: tuple: Midpoint as (latitude, longitude).

    """
    x_total, y_total, z_total = 0.0, 0.0, 0.0
    num_points = len(coordinates)

    if num_points == 1:
        return coordinates[0]

    for lat, lon in coordinates:
        # Convert latitude and longitude to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        # Convert to Cartesian coordinates
        x = math.cos(lat_rad) * math.cos(lon_rad)
        y = math.cos(lat_rad) * math.sin(lon_rad)
        z = math.sin(lat_rad)

        # Sum up all the coordinates
        x_total += x
        y_total += y
        z_total += z

    # Average the coordinates
    x_avg = x_total / num_points
    y_avg = y_total / num_points
    z_avg = z_total / num_points

    # Convert averaged Cartesian coordinates back to latitude and longitude
    hypotenuse = math.sqrt(x_avg ** 2 + y_avg ** 2)
    lat_mid = math.degrees(math.atan2(z_avg, hypotenuse))
    lon_mid = math.degrees(math.atan2(y_avg, x_avg))

    return (lat_mid, lon_mid)

def find_cheapest_combination(prices: dict) -> Tuple[str, float]:
  """
  Find the cheapest combination of flights.

  param: prices (dict): A dictionary of flight prices for each guest to each destination.

  return: tuple: The cheapest destination and the minimum total cost.

  """
  total_costs = {}
  for destination, guest_prices in prices.items():
      total_costs[destination] = sum(guest_prices.values())

  # Find the destination with the minimum total cost
  cheapest_destination = min(total_costs, key=total_costs.get)
  min_total_cost = total_costs[cheapest_destination]

  return cheapest_destination, min_total_cost