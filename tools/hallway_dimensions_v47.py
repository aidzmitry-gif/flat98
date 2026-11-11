"""Single dimensional basis for APT-001 hallway v47 (millimetres).

B01 segment lengths, measured heights and proposed furniture remain distinct;
none of the computed gaps establish real door hardware or finished dimensions.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class HallDimensions:
    room_width: int = 2090
    room_depth: int = 1675
    height_points: int = 2750
    d1_left: int = 610
    d1_segment: int = 1010
    d1_right: int = 470
    d1_control_width: int = 1140
    d1_control_height: int = 2150
    bench_from_entry: int = 25
    bench_width: int = 575
    bench_depth: int = 420
    bench_height: int = 460
    wardrobe_width: int = 1050
    wardrobe_depth: int = 580
    wardrobe_height: int = 2700
    facade_thickness: int = 18
    panel_clear_width: int = 550
    coat_clear_width: int = 446
    proposed_panel_facade: int = 574
    proposed_coat_facade: int = 470
    drawer_width: int = 250
    drawer_height: int = 90
    underseat_clearance: int = 400
    d2_begin: int = 565
    d2_end: int = 1475

    def validate(self):
        assert self.d1_left+self.d1_segment+self.d1_right==self.room_width
        assert 25+self.bench_width+self.wardrobe_width+25==self.room_depth
        assert self.panel_clear_width+self.coat_clear_width+3*18==self.wardrobe_width
        assert self.proposed_panel_facade+self.proposed_coat_facade+3*2==self.wardrobe_width
        assert self.d2_end-self.d2_begin==910
        assert self.bench_height-35-25==self.underseat_clearance
        assert self.underseat_clearance-self.drawer_height==310
        assert self.bench_width-self.drawer_width==325
        assert self.room_width-self.wardrobe_depth==1510
        assert self.room_width-self.bench_depth==1670
        assert self.room_width-self.wardrobe_depth-self.proposed_panel_facade==936
        assert self.d1_left-self.wardrobe_depth==30

D=HallDimensions()
D.validate()
