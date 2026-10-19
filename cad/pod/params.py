"""S3 Rally Pod dimensions. Millimetres and degrees.

layout switches the cockpit template. Rebuild after changing it.
  0  rally, two seats, LHD: driver on the left, co-driver / instructor on the right
  1  formula, one seat on the centreline, reclined, no co-driver

Positive X is forward, positive Y is the driver's left, positive Z is up. Screens, doors and the
shell stay still. The floor, seats, occupants, wheel, pedals and dash frame move together.
The ergonomics (seat travel, column reach, mannequins) are worked out in ergo.py from these numbers.
"""

layout = 0  # 0 rally two-seat, 1 formula single-seat
driver_pct = 95  # percentile 5 (small woman) or 95 (large man) in the driver seat
codriver_pct = 95  # percentile 5 or 95 in the passenger seat

surge_mm = 50  # mm fore-aft stop
roll_deg = 7  # deg corner and camber stop
pitch_deg = 7  # deg nose up and down stop
heave_mm = 40  # mm bump and landing stop

shell_h = 1880  # mm enclosure height
shell_front = 980  # mm front posts
shell_rear = -1160  # mm rear posts
shell_half_w = 880  # mm side posts from the centreline
screen_x = 800  # mm windscreen display plane
screen_z = 1330  # mm windscreen display centre

sled_top = 78  # mm surge carriage top
roll_z = 118  # mm roll shaft axis
pitch_z = 176  # mm pitch shaft axis
post_z0 = 190  # mm heave guide start
post_h = 190  # mm heave guide length, stops under the floor
deck_z = 430  # mm moving floor centre
deck_t = 12  # mm moving floor thickness
deck_top = 436  # mm moving floor top

seat_y = 330  # mm seat centreline from the car centreline
seat_rake = 18  # deg seat back from vertical
h30 = 210  # mm hip point above the heel point (95th percentile)
heel_x = 470  # mm heel point on the heel plate
sole_deg = 60  # deg sole of the foot on the pedal face, from horizontal
knee_deg = 128  # deg target knee angle, the seat slides to give it
elbow_deg = 100  # deg target elbow angle, hands at quarter to three
seat_travel = 200  # mm seat rail travel forward of the 95th percentile position
seat_lift_max = 80  # mm cushion lift for small drivers to see over the rim
column_travel = 60  # mm steering column reach adjustment
wheel_z = 1080  # mm wheel centre height
wheel_tilt = 25  # deg wheel face from vertical, top toward the screens
wheel_r = 175  # mm rim radius (350 mm rally wheel)
column_len = 280  # mm wheel centre to the dash crossbar along the column
