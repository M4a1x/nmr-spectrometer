// Set $fn to 20-50 for 3D printing
// Sizes in mm
$fn = 100;

// Magnet slot constants
slot_height = 10;
slot_width = 70;
slot_depth = 88.35;

// Design constants
tolerance = 0.2;
nmr_tube_diameter = 5 + tolerance;
coil_tube_diameter = 7 + tolerance;
tube_holder_width = 15;
global_thickness = 3;

// Calculated

module single_inset(width, depth, thickness) {
    translate(v = [-width/2, 0, 0]) {
        cube(size = [width, depth, thickness], center = false);
    }
}

module inset() {
    inset_width = (slot_width - tube_holder_width) / 2;
    inset_offset = (tube_holder_width + inset_width) / 2; 
    
    translate(v = [inset_offset, 0, 0]) {
        single_inset(width = inset_width, depth = slot_depth, thickness = global_thickness);
    }

    translate(v = [-inset_offset, 0, 0]) {
        single_inset(width = inset_width, depth = slot_depth, thickness = global_thickness);
    }

}

module tube(diameter = nmr_tube_diameter, length = global_thickness + tolerance) {
    translate(v = [0, global_thickness / 2, slot_height / 2]) {
        rotate(a = [90, 0, 0]) {
            cylinder(h = length, r = diameter / 2, center = true);
        }
    }
}

module tube_holder() {
    translate(v = [-tube_holder_width / 2, 0, 0]) {
        cube(size = [tube_holder_width, global_thickness, slot_height], center = false);
    }
}

module nmr_tube_holder() {
    difference() {
        tube_holder();
        tube();
    }
}

module coil_tube_holder() {
    difference() {
        tube_holder();
        tube(diameter = coil_tube_diameter);
        translate(v = [-tube_holder_width / 2 - tolerance / 2, -tolerance / 2, slot_height / 2]) {
            cube(size=[tube_holder_width + tolerance, global_thickness + tolerance, slot_height + tolerance], center = false);
        }
    }
}

module holder() {
    nmr_tube_holder();

    translate(v = [0, slot_depth - global_thickness, 0]) {
        nmr_tube_holder();
    }

    translate(v = [0, (slot_depth - global_thickness) / 3, 0]) { 
        coil_tube_holder();
    }

    translate(v = [0, (slot_depth - global_thickness) / 3 * 2, 0]) {
        coil_tube_holder();
    }
}

inset();
holder();

