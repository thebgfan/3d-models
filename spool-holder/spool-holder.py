import cadquery as cq

#
# Dimensions
#

# Spindle
spindle_inner_diameter = 42
spindle_outer_diameter = 50
spindle_rim_radius = 1
spindle_rim_height = 1.4

spindle_height = 69
spindle_clearance_from_case = 1

# Bearings
spindle_num_bearings = 2
spindle_bearings_inset_height = 4
spindle_bearings_rim_radius = 1
spindle_bearings_rim_height = 4

spindle_bearing_height = 7
spindle_bearing_outer_diameter = 22.2
spindle_bearing_inner_diameter = 8

# Air cuts
spindle_air_cuts_number = 10
spindle_air_cuts_width = 6
spindle_air_cuts_end_below_top_rim = 3

# Bolt
bolt_diameter = 6.2
bolt_head_diameter = 14

# Spacer
spacer_base_diameter = 11
spacer_ends_below_bearing_top = 1

# Base
base_height = 4
base_diameter = 150
base_outer_ring_radius = 10

base_lip_base_width = 20
base_lip_base_depth = 24
base_lip_base_height = 4

base_lip_width = 26
base_lip_height = 4
base_lip_fillet = 0.75

mount_offset_from_center = 0

# Heights for bolt length calculation (do not participate in the model)
rubber_isolation_height = 1
case_height = 2
nut_height = 6
number_of_nuts = 2

# Calculated
spindle_bearings_height = spindle_num_bearings * spindle_bearing_height

spacer_base_height = spindle_clearance_from_case + spindle_bearings_inset_height
spacer_bolt_height = spindle_bearings_height - spacer_ends_below_bearing_top

#
# Render
#

wp = cq.Workplane("XY")
grow_z = (True, True, False)

#
# Spindle
#

spindle = wp.circle(spindle_outer_diameter / 2).extrude(spindle_height)

lower_rim = (
    wp.circle(spindle_outer_diameter / 2 + spindle_rim_radius)
    .extrude(spindle_rim_height)
    .edges(">Z")
    .chamfer(spindle_rim_radius - 0.01)
)
spindle = spindle.union(lower_rim)

upper_rim = (
    wp.workplane(offset=spindle_height - spindle_rim_height)
    .circle(spindle_outer_diameter / 2 + spindle_rim_radius)
    .extrude(spindle_rim_height)
    .edges("<Z")
    .chamfer(spindle_rim_radius - 0.01)
)
spindle = spindle.union(upper_rim)

bearing_hole = wp.circle(spindle_bearing_outer_diameter / 2).extrude(
    spindle_bearings_inset_height + spindle_bearings_height
)
spindle = spindle.cut(bearing_hole)

bearing_rim = (
    wp.workplane(offset=spindle_bearings_inset_height + spindle_bearings_height)
    .circle(spindle_bearing_outer_diameter / 2 - spindle_bearings_rim_radius)
    .extrude(spindle_bearings_rim_height)
)
spindle = spindle.cut(bearing_rim)

# Bearings rim chamfer
spindle = spindle.edges(
    cq.NearestToPointSelector(
        (0, 0, spindle_bearings_inset_height + spindle_bearings_height)
    )
).chamfer(spindle_bearings_rim_radius - 0.01)

spindle_top_hole_wp = wp.workplane(
    offset=spindle_bearings_inset_height
    + spindle_bearings_height
    + spindle_bearings_rim_height
)

spindle_top_hole = spindle_top_hole_wp.circle(spindle_inner_diameter / 2).extrude(
    spindle_height
)
spindle = spindle.cut(spindle_top_hole)

spindle_air_gaps = (
    spindle_top_hole_wp.sketch()
    .circle(spindle_inner_diameter / 2, mode="c", tag="circle")
    .wires(tag="circle")
    .distribute(spindle_air_cuts_number)
    .rect(spindle_air_cuts_width, 20, mode="a")
    .finalize()
    .extrude(
        spindle_height
        - spindle_bearings_inset_height
        - spindle_bearings_height
        - spindle_bearings_rim_height
        - spindle_rim_height
        - spindle_air_cuts_end_below_top_rim
    )
    .edges(">Z")
    .chamfer(spindle_air_cuts_width / 2 - 0.01)
)

spindle = spindle.cut(spindle_air_gaps)

#
# Spacer
#

spacer = wp.circle(spacer_base_diameter / 2).extrude(spacer_base_height)

spacer_support = (
    wp.workplane(offset=spacer_base_height)
    .circle(spindle_bearing_inner_diameter / 2)
    .extrude(spacer_bolt_height)
)

spacer = spacer.union(spacer_support)

spacer_hole = wp.circle(bolt_diameter / 2).extrude(
    spacer_base_height + spacer_bolt_height
)

spacer = spacer.cut(spacer_hole)

# To visualize the spacer when correctly positioned against the spindle
# spacer = spacer.translate((0, 0, -spindle_clearance_from_case))

#
# Bolt length calculation
#

total = (
    base_height
    + rubber_isolation_height
    + case_height
    + spindle_clearance_from_case
    + spindle_bearings_inset_height
    + spindle_bearings_height
    + nut_height * number_of_nuts
)
print(f"Bolt length needed: {total}mm")

#
# Base
#

base_ring = (
    wp.circle(base_diameter / 2)
    .circle(base_diameter / 2 - base_outer_ring_radius)
    .extrude(base_height)
)

base_rectangle_x = wp.box(
    base_diameter - base_outer_ring_radius / 2,
    base_lip_base_width,
    base_height,
    centered=grow_z,
)
base = base_ring.union(base_rectangle_x)

base_rectangle_y = wp.box(
    base_lip_base_width,
    base_diameter - base_outer_ring_radius / 2,
    base_height,
    centered=grow_z,
)
base = base.union(base_rectangle_y)

lip_base_wp = wp.workplane(offset=base_height).center(0, mount_offset_from_center)

lip_base = lip_base_wp.box(
    base_lip_base_width, base_lip_base_depth, base_lip_base_height, centered=grow_z
)

base = base.union(lip_base)

lip_wp = lip_base_wp.workplane(offset=base_lip_base_height)

lip_rect = lip_wp.box(
    base_lip_width, base_lip_base_depth, base_lip_height, centered=grow_z
)
lip_circle = (
    lip_wp.center(0, -base_lip_base_depth / 2)
    .circle(base_lip_width / 2)
    .extrude(base_lip_height)
)

lip = lip_rect.union(lip_circle)

lip = lip.edges("|Y").fillet(base_lip_fillet)

base = base.union(lip)

base = base.copyWorkplane(
    cq.Workplane().workplane(
        offset=base_height + base_lip_base_height + base_lip_height
    )
).cboreHole(bolt_diameter, bolt_head_diameter, base_lip_base_height + base_lip_height)

#
# Export to STL
#

cq.exporters.export(spindle, "spindle.stl")
cq.exporters.export(spacer, "spacer.stl")
cq.exporters.export(base, "base.stl")

print("Done")
