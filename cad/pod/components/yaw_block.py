from steve import Component
from params import pivot_z
from motion import YAW_PIN_X, YAW_POST, YAW_POST_X, YAW_POST_Y, YAW_ARM_T, GUIDE_RAIL_H
from bought import YAW_GUIDE, YAW_ROD_END

# Yaw restraint slider (fix I): the guide block on the carriage post's rail, an arm under the floor's tail pin, and
# the rod end whose ball the pin passes through. It rides the rail with the pin through heave and pitch, and holds
# the pin sideways, so the floor cannot yaw. Drawn at rest; main.py slides it.
yaw_block = Component("yaw_block", name="Yaw restraint slider")
h1 = YAW_ROD_END["center_to_shank_end_mm"]
face = YAW_POST_Y - YAW_POST / 2 - GUIDE_RAIL_H  # block's mounting face on the rail
block_h = YAW_GUIDE["total_height_mm"] - GUIDE_RAIL_H
arm_z = pivot_z - h1 - YAW_ARM_T / 2
yaw_block.box("block", YAW_GUIDE["block_width_mm"], block_h, YAW_GUIDE["block_length_mm"],
              at=(YAW_POST_X, face - block_h / 2, arm_z))
arm_y0 = -YAW_ROD_END["eye_diameter_mm"] / 2 + 5
yaw_block.box("arm", YAW_GUIDE["block_width_mm"], face - block_h - arm_y0, YAW_ARM_T,
              at=(YAW_POST_X, (face - block_h + arm_y0) / 2, arm_z), op="new")
# Rod end: shank up from the arm, housing round the ball, the ball's bore along X on the pin.
eye_r = YAW_ROD_END["eye_diameter_mm"] / 2
ball_r = 17.45  # ball diameter dk 34.9 (card notes)
yaw_block.cylinder("rod_shank", 15, h1 - eye_r + 10, at=(YAW_PIN_X, 0, pivot_z - h1), op="new")
w = YAW_ROD_END["eye_width_mm"]
yaw_block.cylinder("rod_eye", eye_r, w, at=(YAW_PIN_X - w / 2, 0, pivot_z), direction=(1, 0, 0), op="new")
yaw_block.cylinder("rod_eye_hole", ball_r, w + 2, at=(YAW_PIN_X - w / 2 - 1, 0, pivot_z), direction=(1, 0, 0),
                   op="cut", body="rod_eye")
b = YAW_ROD_END["ball_width_mm"]
yaw_block.cylinder("rod_ball", ball_r, b, at=(YAW_PIN_X - b / 2, 0, pivot_z), direction=(1, 0, 0), op="new")
yaw_block.cylinder("rod_ball_bore", YAW_ROD_END["bore_mm"] / 2, b + 2, at=(YAW_PIN_X - b / 2 - 1, 0, pivot_z),
                   direction=(1, 0, 0), op="cut", body="rod_ball")
yaw_block.material("steel-1c45", color="#8d939c")
yaw_block.material("steel-s235jr", bodies=["arm"], color="#4a515b")
